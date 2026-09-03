"""
Citation Graph Builder for SIMA Research
Parses a .bib file, queries OpenAlex for citation relationships,
and generates an interactive directed graph visualization.
"""

import re
import time
from pathlib import Path

import base64
from io import BytesIO

import bibtexparser
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from pyvis.network import Network

from paperconnect.openalex import (
    load_cache, save_cache, query_by_doi, query_by_title,
    query_by_id, find_all_versions, query_cited_by,
)


BIB_FILE = Path("SIMA PERSONAL.bib")
OUTPUT_HTML = Path("citation_graph.html")


def parse_bib(path):
    """Parse .bib file and return list of entries with key, title, doi, year, authors."""
    with open(path, encoding="utf-8") as f:
        parser = bibtexparser.bparser.BibTexParser(common_strings=True)
        parser.ignore_nonstandard_types = False
        library = bibtexparser.load(f, parser=parser)

    entries = []
    for entry in library.entries:
        doi = entry.get("doi", "").strip().rstrip(".")
        if doi:
            doi = re.sub(r'^https?://(dx\.)?doi\.org/', '', doi)

        authors_raw = entry.get("author", "")
        first_author = authors_raw.split(" and ")[0].split(",")[0].strip() if authors_raw else ""

        year = entry.get("year", "") or entry.get("date", "")[:4]
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
        result = query_by_doi(entry["doi"], cache)
        if not result:
            result = query_by_title(entry["title"], cache)

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

            # If the original has no references, pull them from the alternate
            if not data.get("referenced_works"):
                alt_data = query_by_id(v_id, cache)
                if alt_data and alt_data.get("referenced_works"):
                    entry_data[entry["key"]]["referenced_works"] = alt_data["referenced_works"]
                    print(f"    {entry['label']}: got {len(alt_data['referenced_works'])} refs from alternate version")
                time.sleep(0.12)

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
    net.barnes_hut(gravity=-5000, spring_length=250, spring_strength=0.005)

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
          "gravitationalConstant": -5000,
          "springLength": 250,
          "springConstant": 0.005
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

    view_switcher_html = """
    <div id="view-menu" style="
        position:fixed; top:15px; right:15px; z-index:1000;
        background:#16213e; border-radius:8px; overflow:hidden;
        box-shadow:0 2px 10px rgba(0,0,0,0.5); display:flex;
        border:1px solid #555;">
      <button id="btn-interactive" onclick="switchView('interactive')" style="
        padding:8px 16px; border:none; cursor:pointer; font-size:13px;
        background:#3498db; color:white;">
        Interactive View
      </button>
      <button id="btn-timeline" onclick="switchView('timeline')" style="
        padding:8px 16px; border:none; cursor:pointer; font-size:13px;
        background:#16213e; color:#aaa;">
        Timeline View
      </button>
    </div>

    <div id="timeline-container" style="
      display:none; position:fixed; top:0; left:0; width:100%%; height:100%%;
      background:#1a1a2e; z-index:500;
      flex-direction:column; align-items:center; justify-content:center;">
      <img src="data:image/png;base64,%s" style="max-width:95%%; max-height:90%%;
        object-fit:contain;">
    </div>

    <div id="color-legend" style="
        position:fixed; bottom:15px; left:15px; z-index:1000;
        background:#16213e; padding:12px 16px; border-radius:8px;
        box-shadow:0 2px 10px rgba(0,0,0,0.5); border:1px solid #555;
        font-size:12px; color:white; line-height:1.8;">
      <div style="font-weight:bold; margin-bottom:4px; font-size:13px;">Color by Era</div>
      <div><span style="display:inline-block;width:12px;height:12px;border-radius:50%%;background:#e74c3c;margin-right:6px;vertical-align:middle;"></span>Foundational (pre-1980)</div>
      <div><span style="display:inline-block;width:12px;height:12px;border-radius:50%%;background:#f39c12;margin-right:6px;vertical-align:middle;"></span>Classical (1980-1999)</div>
      <div><span style="display:inline-block;width:12px;height:12px;border-radius:50%%;background:#2ecc71;margin-right:6px;vertical-align:middle;"></span>Traditional ML (2000-2014)</div>
      <div><span style="display:inline-block;width:12px;height:12px;border-radius:50%%;background:#3498db;margin-right:6px;vertical-align:middle;"></span>Early Deep Learning (2015-2021)</div>
      <div><span style="display:inline-block;width:12px;height:12px;border-radius:50%%;background:#9b59b6;margin-right:6px;vertical-align:middle;"></span>Recent / Generative (2022+)</div>
    </div>

    <script>
    function switchView(view) {
      var graphDiv = document.getElementById("mynetwork");
      var timelineDiv = document.getElementById("timeline-container");
      var searchDiv = document.getElementById("search-container");
      var btnInteractive = document.getElementById("btn-interactive");
      var btnTimeline = document.getElementById("btn-timeline");

      if (view === "timeline") {
        graphDiv.style.display = "none";
        searchDiv.style.display = "none";
        timelineDiv.style.display = "flex";
        btnTimeline.style.background = "#3498db";
        btnTimeline.style.color = "white";
        btnInteractive.style.background = "#16213e";
        btnInteractive.style.color = "#aaa";
      } else {
        timelineDiv.style.display = "none";
        graphDiv.style.display = "block";
        searchDiv.style.display = "block";
        btnInteractive.style.background = "#3498db";
        btnInteractive.style.color = "white";
        btnTimeline.style.background = "#16213e";
        btnTimeline.style.color = "#aaa";
      }
    }
    </script>
    """ % timeline_b64

    highlight_js = """
    <script>
    (function() {
      var originalColors = {};
      var originalEdgeColors = {};

      function storeOriginals() {
        nodes.get().forEach(function(n) {
          originalColors[n.id] = { color: n.color, font: n.font };
        });
        edges.get().forEach(function(e) {
          originalEdgeColors[e.id] = e.color;
        });
      }

      network.once("stabilized", storeOriginals);
      setTimeout(storeOriginals, 3000);

      function restoreAll() {
        var updatedNodes = [];
        nodes.get().forEach(function(n) {
          var orig = originalColors[n.id];
          if (orig) {
            updatedNodes.push({id: n.id, color: orig.color, font: {color: "white"}});
          }
        });
        nodes.update(updatedNodes);

        var updatedEdges = [];
        edges.get().forEach(function(e) {
          updatedEdges.push({id: e.id, color: originalEdgeColors[e.id] || "#555555"});
        });
        edges.update(updatedEdges);
      }

      network.on("selectNode", function(params) {
        if (params.nodes.length === 0) return;
        var selectedId = params.nodes[0];
        var connected = network.getConnectedNodes(selectedId);
        connected.push(selectedId);

        var updatedNodes = [];
        nodes.get().forEach(function(n) {
          if (connected.indexOf(n.id) !== -1) {
            var orig = originalColors[n.id];
            updatedNodes.push({
              id: n.id,
              color: orig ? orig.color : n.color,
              font: {color: "white"}
            });
          } else {
            updatedNodes.push({
              id: n.id,
              color: "rgba(80,80,80,0.15)",
              font: {color: "rgba(255,255,255,0.1)"}
            });
          }
        });
        nodes.update(updatedNodes);

        var updatedEdges = [];
        edges.get().forEach(function(e) {
          if (e.from === selectedId || e.to === selectedId) {
            updatedEdges.push({id: e.id, color: {color: "#ffffff", opacity: 0.8}});
          } else {
            updatedEdges.push({id: e.id, color: {color: "#555555", opacity: 0.03}});
          }
        });
        edges.update(updatedEdges);
      });

      network.on("deselectNode", restoreAll);
      network.on("click", function(params) {
        if (params.nodes.length === 0) restoreAll();
      });
    })();
    </script>
    """

    with open(output_path) as f:
        html = f.read()
    html = html.replace("</body>", search_bar_html + view_switcher_html + highlight_js + "</body>")
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
