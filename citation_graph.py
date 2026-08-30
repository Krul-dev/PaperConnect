"""
Citation Graph Builder for SIMA Research
Parses a .bib file, queries OpenAlex for citation relationships,
and generates an interactive directed graph visualization.
"""

import json
import time
import re
from pathlib import Path

import base64
from io import BytesIO

import bibtexparser
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import requests
from pyvis.network import Network


BIB_FILE = Path("SIMA PERSONAL.bib")
OUTPUT_HTML = Path("citation_graph.html")
CACHE_FILE = Path("openalex_cache.json")

OPENALEX_BASE = "https://api.openalex.org"
POLITE_EMAIL = "sima.research@example.com"


def parse_bib(path):
    """Parse .bib file and return list of entries with key, title, doi, year, authors."""
    with open(path, encoding="utf-8") as f:
        parser = bibtexparser.bparser.BibTexParser(common_strings=True)
        library = bibtexparser.load(f, parser=parser)

    entries = []
    for entry in library.entries:
        doi = entry.get("doi", "").strip().rstrip(".")
        if doi:
            doi = re.sub(r'^https?://(dx\.)?doi\.org/', '', doi)

        authors_raw = entry.get("author", "")
        first_author = authors_raw.split(" and ")[0].split(",")[0].strip() if authors_raw else ""

        year = entry.get("year", "")
        title = entry.get("title", "").replace("{", "").replace("}", "")

        label = f"{first_author} {year}" if first_author else title[:30]

        entries.append({
            "key": entry.get("ID", ""),
            "title": title,
            "doi": doi,
            "year": year,
            "first_author": first_author,
            "label": label,
            "authors": authors_raw,
        })
    return entries


def load_cache():
    if CACHE_FILE.exists():
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def query_openalex_by_doi(doi, cache):
    """Get OpenAlex work ID and referenced_works by DOI."""
    if not doi:
        return None

    cache_key = f"doi:{doi}"
    if cache_key in cache:
        return cache[cache_key]

    url = f"{OPENALEX_BASE}/works/doi:{doi}"
    params = {"mailto": POLITE_EMAIL}

    try:
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            result = {
                "openalex_id": data.get("id", ""),
                "referenced_works": data.get("referenced_works", []),
                "title": data.get("title", ""),
            }
            cache[cache_key] = result
            return result
        else:
            cache[cache_key] = None
            return None
    except requests.RequestException:
        return None


def query_openalex_by_title(title, cache):
    """Fallback: search by title if DOI is missing."""
    if not title:
        return None

    cache_key = f"title:{title[:80]}"
    if cache_key in cache:
        return cache[cache_key]

    url = f"{OPENALEX_BASE}/works"
    params = {
        "filter": f'title.search:"{title[:100]}"',
        "mailto": POLITE_EMAIL,
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            if results:
                work = results[0]
                result = {
                    "openalex_id": work.get("id", ""),
                    "referenced_works": work.get("referenced_works", []),
                    "title": work.get("title", ""),
                }
                cache[cache_key] = result
                return result
        cache[cache_key] = None
        return None
    except requests.RequestException:
        return None


def find_all_versions(title, first_author, known_id, cache):
    """Find all versions of a paper on OpenAlex.

    Many papers exist as multiple OpenAlex records (working paper vs journal,
    preprint vs publication). We want to identify all versions so that
    forward and reverse matching catches all citations.

    Example: Rubin 1975 (ETS, 68 cites) vs Rubin 1976 (Biometrika, 9806 cites).
    """
    cache_key = f"all_versions:{known_id}"
    if cache_key in cache:
        return cache[cache_key]

    # Search for same title + author, pick the most cited version
    search_title = title[:80].replace('"', '')
    author_last = first_author.split()[-1] if first_author else ""

    url = f"{OPENALEX_BASE}/works"
    params = {
        "filter": f'title.search:"{search_title}"',
        "sort": "cited_by_count:desc",
        "per_page": 5,
        "mailto": POLITE_EMAIL,
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            version_ids = []
            for w in results:
                w_id = w.get("id", "")
                if w_id == known_id:
                    continue
                w_authors = w.get("authorships", [])
                author_names = [a.get("author", {}).get("display_name", "").lower() for a in w_authors]
                if author_last and any(author_last.lower() in name for name in author_names):
                    version_ids.append(w_id)
            cache[cache_key] = version_ids
            return version_ids
        cache[cache_key] = []
        return []
    except requests.RequestException:
        cache[cache_key] = []
        return []


def query_cited_by(openalex_id, our_ids, cache):
    """Reverse lookup: ask OpenAlex which works in our collection cite this article."""
    cache_key = f"cited_by:{openalex_id}"
    if cache_key in cache:
        return cache[cache_key]

    short_id = openalex_id.replace("https://openalex.org/", "")
    url = f"{OPENALEX_BASE}/works"
    params = {
        "filter": f"cites:{short_id}",
        "per_page": 200,
        "select": "id",
        "mailto": POLITE_EMAIL,
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            citers = [w["id"] for w in data.get("results", [])]
            relevant = [c for c in citers if c in our_ids]
            cache[cache_key] = relevant
            return relevant
        else:
            cache[cache_key] = []
            return []
    except requests.RequestException:
        return []


def build_graph(entries):
    """Query OpenAlex for each entry and build citation edges within the collection.

    Uses two methods to find edges:
    1. Forward: check each article's referenced_works list against our collection IDs
    2. Reverse: for each article, ask OpenAlex who in our collection cites it
       (catches multi-version papers like Rubin 1975/1976)
    """
    cache = load_cache()
    openalex_map = {}  # openalex_id -> entry key
    entry_data = {}    # entry key -> openalex result

    print(f"Looking up {len(entries)} articles on OpenAlex...")
    print()

    found = 0
    not_found = []

    for i, entry in enumerate(entries):
        result = query_openalex_by_doi(entry["doi"], cache)
        if not result:
            result = query_openalex_by_title(entry["title"], cache)

        if result and result.get("openalex_id"):
            openalex_map[result["openalex_id"]] = entry["key"]
            entry_data[entry["key"]] = result
            found += 1
            status = "OK"
        else:
            not_found.append(entry)
            status = "NOT FOUND"

        print(f"  [{i+1}/{len(entries)}] {entry['label']} — {status}")

        # Save cache after every 5 queries (so partial progress is kept)
        if (i + 1) % 5 == 0:
            save_cache(cache)

        # Rate limiting: OpenAlex polite pool allows 10 req/s
        time.sleep(0.12)

    save_cache(cache)

    print(f"\nFound {found}/{len(entries)} articles on OpenAlex.")
    if not_found:
        print(f"Not found ({len(not_found)}):")
        for e in not_found:
            print(f"  - {e['label']}: {e['title'][:60]}")

    # Build graph nodes
    G = nx.DiGraph()

    for entry in entries:
        G.add_node(entry["key"], label=entry["label"], title=entry["title"],
                   year=entry["year"], first_author=entry["first_author"])

    # Pass 0: Find canonical (most-cited) versions for each article
    # This handles papers published in multiple venues (e.g., working paper + journal)
    print("\n  Pass 0: Finding all versions...")
    alt_map = {}  # alt_id -> entry key (additional IDs to check)
    for i, entry in enumerate(entries):
        if entry["key"] not in entry_data:
            continue
        data = entry_data[entry["key"]]
        oa_id = data.get("openalex_id", "")
        versions = find_all_versions(
            entry["title"], entry["first_author"], oa_id, cache
        )
        for v_id in versions:
            if v_id not in openalex_map:
                alt_map[v_id] = entry["key"]
        if versions:
            print(f"    {entry['label']}: found {len(versions)} alternate version(s)")

        if (i + 1) % 5 == 0:
            save_cache(cache)
        time.sleep(0.12)

    save_cache(cache)
    print(f"  Found {len(alt_map)} alternate version IDs total")

    # Merge all version IDs into our lookup map
    all_id_to_key = dict(openalex_map)
    all_id_to_key.update(alt_map)
    our_ids = set(all_id_to_key.keys())

    # Pass 1: Forward matching (referenced_works)
    print("\n  Pass 1: Forward matching (referenced_works)...")
    forward_edges = 0
    for entry in entries:
        if entry["key"] not in entry_data:
            continue
        refs = entry_data[entry["key"]].get("referenced_works", [])
        for ref_id in refs:
            if ref_id in all_id_to_key:
                target_key = all_id_to_key[ref_id]
                if target_key != entry["key"]:
                    G.add_edge(entry["key"], target_key)
                    forward_edges += 1

    print(f"  Found {forward_edges} edges from forward matching")

    # Pass 2: Reverse lookup (cited_by) for both original and alternate IDs
    all_ids_to_check = {}
    for key, data in entry_data.items():
        oa_id = data.get("openalex_id")
        if oa_id:
            all_ids_to_check[oa_id] = key
    for alt_id, key in alt_map.items():
        all_ids_to_check[alt_id] = key

    print(f"\n  Pass 2: Reverse citation lookup ({len(all_ids_to_check)} IDs)...")
    reverse_edges = 0
    for i, (oa_id, key) in enumerate(all_ids_to_check.items()):
        citers_in_collection = query_cited_by(oa_id, our_ids, cache)
        for citer_id in citers_in_collection:
            if citer_id in all_id_to_key:
                citer_key = all_id_to_key[citer_id]
                if citer_key != key and not G.has_edge(citer_key, key):
                    G.add_edge(citer_key, key)
                    reverse_edges += 1

        if (i + 1) % 5 == 0:
            save_cache(cache)

        print(f"    [{i+1}/{len(all_ids_to_check)}] {key[:30]}...")
        time.sleep(0.12)

    save_cache(cache)
    total_edges = forward_edges + reverse_edges
    print(f"\n  Forward edges: {forward_edges}")
    print(f"  Reverse edges (new): {reverse_edges}")
    print(f"\nGraph: {G.number_of_nodes()} nodes, {total_edges} total edges")
    return G, not_found


def generate_timeline_base64(G):
    """Generate a timeline PNG of the citation graph and return it as a base64 string."""
    era_colors = {
        "Foundational (pre-1980)": "#e74c3c",
        "Classical (1980-1999)": "#f39c12",
        "Traditional ML (2000-2014)": "#2ecc71",
        "Early deep learning (2015-2021)": "#3498db",
        "Recent / Generative (2022+)": "#9b59b6",
    }

    def get_color(year):
        try:
            y = int(year)
        except (ValueError, TypeError):
            return "#888888"
        if y < 1980:
            return "#e74c3c"
        elif y < 2000:
            return "#f39c12"
        elif y < 2015:
            return "#2ecc71"
        elif y < 2022:
            return "#3498db"
        else:
            return "#9b59b6"

    nodes_by_year = {}
    for node in G.nodes():
        data = G.nodes[node]
        try:
            year = int(data.get("year", 0))
        except (ValueError, TypeError):
            year = 0
        if year not in nodes_by_year:
            nodes_by_year[year] = []
        nodes_by_year[year].append(node)

    node_positions = {}
    for year, year_nodes in nodes_by_year.items():
        for i, node in enumerate(year_nodes):
            node_positions[node] = (year, i)

    in_degrees = dict(G.in_degree())
    max_in = max(in_degrees.values()) if in_degrees else 1

    fig, ax = plt.subplots(figsize=(20, 10), facecolor="#1a1a2e")
    ax.set_facecolor("#1a1a2e")

    for src, dst in G.edges():
        if src in node_positions and dst in node_positions:
            x1, y1 = node_positions[src]
            x2, y2 = node_positions[dst]
            ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle="->", color="#555555",
                                        alpha=0.3, connectionstyle="arc3,rad=0.1"))

    for node, (x, y) in node_positions.items():
        data = G.nodes[node]
        in_deg = in_degrees.get(node, 0)
        size = 30 + (in_deg / max(max_in, 1)) * 200
        color = get_color(data.get("year"))
        ax.scatter(x, y, s=size, c=color, zorder=3, edgecolors="white", linewidths=0.5)
        ax.annotate(data.get("label", node), (x, y), fontsize=6, color="white",
                    ha="left", va="bottom", xytext=(4, 4), textcoords="offset points")

    years = [y for y in nodes_by_year.keys() if y > 0]
    if years:
        ax.set_xlim(min(years) - 2, max(years) + 2)

    ax.set_xlabel("Publication Year", color="white", fontsize=12)
    ax.tick_params(colors="white")
    ax.spines["bottom"].set_color("#555")
    ax.spines["left"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.set_visible(False)

    legend_patches = [mpatches.Patch(color=c, label=l) for l, c in era_colors.items()]
    ax.legend(handles=legend_patches, loc="upper left", fontsize=8,
              facecolor="#16213e", edgecolor="#555", labelcolor="white")

    plt.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, facecolor="#1a1a2e")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def visualize(G, entries, output_path):
    """Create interactive HTML visualization with pyvis."""
    net = Network(
        height="900px",
        width="100%",
        directed=True,
        bgcolor="#1a1a2e",
        font_color="white",
    )
    net.barnes_hut(gravity=-3000, spring_length=150, spring_strength=0.01)

    # Color nodes by era
    def get_color(year):
        try:
            y = int(year)
        except (ValueError, TypeError):
            return "#888888"
        if y < 1980:
            return "#e74c3c"  # red — foundational
        elif y < 2000:
            return "#f39c12"  # orange — classical
        elif y < 2015:
            return "#2ecc71"  # green — traditional ML
        elif y < 2022:
            return "#3498db"  # blue — early deep learning
        else:
            return "#9b59b6"  # purple — recent/generative

    # Size by in-degree (how many articles in collection cite this one)
    in_degrees = dict(G.in_degree())
    max_in = max(in_degrees.values()) if in_degrees else 1

    for node in G.nodes():
        data = G.nodes[node]
        in_deg = in_degrees.get(node, 0)
        out_deg = G.out_degree(node)
        size = 15 + (in_deg / max(max_in, 1)) * 35

        hover = (
            f"<b>{data.get('label', node)}</b><br>"
            f"{data.get('title', '')[:80]}<br>"
            f"Year: {data.get('year', '?')}<br>"
            f"Cited by {in_deg} in collection | Cites {out_deg} in collection"
        )

        net.add_node(
            node,
            label=data.get("label", node),
            title=hover,
            size=size,
            color=get_color(data.get("year")),
        )

    for src, dst in G.edges():
        net.add_edge(src, dst, color="#555555", arrows="to")

    net.set_options("""
    {
      "interaction": {
        "hover": true,
        "navigationButtons": true,
        "keyboard": true
      },
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -3000,
          "springLength": 150,
          "springConstant": 0.01
        }
      }
    }
    """)

    net.save_graph(str(output_path))

    search_bar_html = """
    <div id="search-container" style="
        position: fixed; top: 15px; left: 15px; z-index: 1000;
        background: #16213e; padding: 10px 15px; border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.5); width: 300px;">
      <input type="text" id="search-input" placeholder="Search papers..."
        autocomplete="off"
        style="padding: 6px 10px; border: 1px solid #555; border-radius: 4px;
        background: #1a1a2e; color: white; font-size: 14px; width: 100%;
        box-sizing: border-box; outline: none;"
        onfocus="this.style.borderColor='#3498db'"
        onblur="setTimeout(function(){document.getElementById('search-input').style.borderColor='#555'},200)">
      <div id="suggestions" style="
        max-height: 250px; overflow-y: auto; margin-top: 5px;
        display: none; border-radius: 4px;"></div>
    </div>
    <script>
    var searchInput = document.getElementById("search-input");
    var suggestionsDiv = document.getElementById("suggestions");

    searchInput.addEventListener("input", function() {
      var query = this.value.toLowerCase().trim();
      suggestionsDiv.innerHTML = "";
      if (!query) {
        suggestionsDiv.style.display = "none";
        network.unselectAll();
        return;
      }
      var allNodes = nodes.get();
      var matches = allNodes.filter(function(n) {
        return n.label.toLowerCase().includes(query) ||
               (n.title && n.title.toLowerCase().includes(query));
      });
      if (matches.length === 0) {
        suggestionsDiv.style.display = "block";
        suggestionsDiv.innerHTML = '<div style="padding:6px 10px;color:#e74c3c;font-size:13px;">No matches</div>';
        network.unselectAll();
        return;
      }
      suggestionsDiv.style.display = "block";
      var matchIds = matches.map(function(n) { return n.id; });
      network.selectNodes(matchIds);

      matches.slice(0, 15).forEach(function(n) {
        var item = document.createElement("div");
        item.textContent = n.label;
        item.style.cssText = "padding:6px 10px;color:white;font-size:13px;cursor:pointer;border-radius:3px;";
        item.addEventListener("mouseenter", function() {
          this.style.background = "#2a3a5c";
        });
        item.addEventListener("mouseleave", function() {
          this.style.background = "transparent";
        });
        item.addEventListener("click", function() {
          network.selectNodes([n.id]);
          network.focus(n.id, {scale: 1.5, animation: true});
          searchInput.value = n.label;
          suggestionsDiv.style.display = "none";
        });
        suggestionsDiv.appendChild(item);
      });
      if (matches.length > 15) {
        var more = document.createElement("div");
        more.textContent = "... and " + (matches.length - 15) + " more";
        more.style.cssText = "padding:6px 10px;color:#aaa;font-size:12px;";
        suggestionsDiv.appendChild(more);
      }
    });

    document.addEventListener("click", function(e) {
      if (!document.getElementById("search-container").contains(e.target)) {
        suggestionsDiv.style.display = "none";
      }
    });
    </script>
    """

    print("  Generating timeline image...")
    timeline_b64 = generate_timeline_base64(G)

    timeline_html = """
    <button id="timeline-btn" onclick="document.getElementById('timeline-overlay').style.display='flex'"
      style="position:fixed; top:15px; right:15px; z-index:1000;
      background:#16213e; color:white; border:1px solid #555; padding:8px 16px;
      border-radius:8px; cursor:pointer; font-size:14px;
      box-shadow:0 2px 10px rgba(0,0,0,0.5);"
      onmouseenter="this.style.background='#2a3a5c'"
      onmouseleave="this.style.background='#16213e'">
      Timeline View
    </button>
    <div id="timeline-overlay" style="
      display:none; position:fixed; top:0; left:0; width:100%%; height:100%%;
      background:rgba(0,0,0,0.85); z-index:2000;
      flex-direction:column; align-items:center; justify-content:center;">
      <button onclick="document.getElementById('timeline-overlay').style.display='none'"
        style="position:absolute; top:20px; right:30px; background:none;
        border:none; color:white; font-size:28px; cursor:pointer;">&#x2715;</button>
      <img src="data:image/png;base64,%s" style="max-width:95%%; max-height:90%%;
        object-fit:contain; border-radius:8px;">
    </div>
    """ % timeline_b64

    with open(output_path) as f:
        html = f.read()
    html = html.replace("</body>", search_bar_html + timeline_html + "</body>")
    with open(output_path, "w") as f:
        f.write(html)

    print(f"\nVisualization saved to: {output_path}")
    print("Open it in your browser to explore the graph.")


def print_summary(G):
    """Print useful stats about the graph."""
    print("\n" + "=" * 60)
    print("GRAPH SUMMARY")
    print("=" * 60)

    # Most cited within collection
    in_deg = sorted(G.in_degree(), key=lambda x: x[1], reverse=True)
    print("\nMost cited within your collection (hubs):")
    for node, deg in in_deg[:10]:
        if deg > 0:
            data = G.nodes[node]
            print(f"  {deg} citations <- {data.get('label', node)}: {data.get('title', '')[:50]}")

    # Most references to other articles in collection
    out_deg = sorted(G.out_degree(), key=lambda x: x[1], reverse=True)
    print("\nArticles referencing the most others in your collection:")
    for node, deg in out_deg[:10]:
        if deg > 0:
            data = G.nodes[node]
            print(f"  {deg} references -> {data.get('label', node)}: {data.get('title', '')[:50]}")

    # Isolated nodes (no connections at all)
    isolated = [n for n in G.nodes() if G.in_degree(n) == 0 and G.out_degree(n) == 0]
    if isolated:
        print(f"\nIsolated articles (no connections within collection): {len(isolated)}")
        for node in isolated:
            data = G.nodes[node]
            print(f"  - {data.get('label', node)}: {data.get('title', '')[:60]}")

    print("\nColor legend:")
    print("  Red    = Foundational (pre-1980)")
    print("  Orange = Classical (1980-1999)")
    print("  Green  = Traditional ML era (2000-2014)")
    print("  Blue   = Early deep learning (2015-2021)")
    print("  Purple = Recent / Generative (2022+)")
    print()


def main():
    print("=" * 60)
    print("CITATION GRAPH BUILDER — SIMA Research")
    print("=" * 60)
    print()

    entries = parse_bib(BIB_FILE)
    print(f"Parsed {len(entries)} entries from {BIB_FILE}")

    G, not_found = build_graph(entries)
    print_summary(G)
    visualize(G, entries, OUTPUT_HTML)


if __name__ == "__main__":
    main()
