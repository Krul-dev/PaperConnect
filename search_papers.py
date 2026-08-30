"""
Paper Search Tool for SIMA Research
Searches OpenAlex for papers you might be missing, filtered against your .bib collection.
"""

import argparse
import csv
import re
from datetime import date
from pathlib import Path

from citation_graph import parse_bib
from paperconnect.openalex import search_works


BIB_FILE = Path("SIMA PERSONAL.bib")
SEARCH_LOG = Path("search_log.csv")

LOG_FIELDS = ["date", "query", "year_from", "year_to", "title", "authors", "year",
              "citations", "doi", "status"]


def get_existing_titles(bib_path):
    """Get a set of normalized titles from the .bib file for deduplication."""
    entries = parse_bib(bib_path)
    titles = set()
    for e in entries:
        normalized = re.sub(r'[^a-z0-9]', '', e["title"].lower())
        titles.add(normalized)
    return titles


def get_author_str(work):
    """Extract a short author string from an OpenAlex work."""
    authors = work.get("authorships", [])
    author_names = [a.get("author", {}).get("display_name", "") for a in authors[:3]]
    author_str = ", ".join(author_names)
    if len(authors) > 3:
        author_str += " et al."
    return author_str


def log_results(query, year_from, year_to, results):
    """Append search results to the CSV log."""
    write_header = not SEARCH_LOG.exists()

    with open(SEARCH_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if write_header:
            writer.writeheader()

        today = date.today().isoformat()
        for work in results:
            writer.writerow({
                "date": today,
                "query": query,
                "year_from": year_from or "",
                "year_to": year_to or "",
                "title": work.get("title", ""),
                "authors": get_author_str(work),
                "year": work.get("publication_year", ""),
                "citations": work.get("cited_by_count", 0),
                "doi": work.get("doi", ""),
                "status": "",
            })


def format_result(work, index):
    """Format a single OpenAlex work for display."""
    title = work.get("title", "Unknown title")
    year = work.get("publication_year", "?")
    cited_by = work.get("cited_by_count", 0)
    doi = work.get("doi", "")

    lines = [
        f"  {index}. {title}",
        f"     {get_author_str(work)} ({year}) — {cited_by} citations",
    ]
    if doi:
        lines.append(f"     {doi}")
    return "\n".join(lines)


def search(query, year_from=None, year_to=None, n=10):
    """Search for papers and filter out ones already in the collection."""
    existing = get_existing_titles(BIB_FILE)

    print(f"Searching OpenAlex for: \"{query}\"", end="")
    if year_from or year_to:
        print(f" ({year_from or '...'} to {year_to or '...'})", end="")
    print("\n")

    results = search_works(query, year_from=year_from, year_to=year_to, per_page=50)

    new_results = []
    skipped = 0
    for work in results:
        title = work.get("title", "")
        normalized = re.sub(r'[^a-z0-9]', '', title.lower())
        if normalized in existing:
            skipped += 1
            continue
        new_results.append(work)
        if len(new_results) >= n:
            break

    if not new_results:
        print("No new papers found (all results are already in your collection).")
        return

    print(f"Top {len(new_results)} papers NOT in your collection (skipped {skipped} you already have):\n")
    for i, work in enumerate(new_results, 1):
        print(format_result(work, i))
        print()

    log_results(query, year_from, year_to, new_results)
    print(f"Results saved to {SEARCH_LOG}")


def main():
    parser = argparse.ArgumentParser(description="Search OpenAlex for papers to add to your collection")
    parser.add_argument("query", help="Search terms (e.g., 'KNN imputation time series')")
    parser.add_argument("--from", dest="year_from", type=int, help="Start year (e.g., 2000)")
    parser.add_argument("--to", dest="year_to", type=int, help="End year (e.g., 2014)")
    parser.add_argument("-n", type=int, default=10, help="Number of results to show (default: 10)")

    args = parser.parse_args()
    search(args.query, year_from=args.year_from, year_to=args.year_to, n=args.n)


if __name__ == "__main__":
    main()
