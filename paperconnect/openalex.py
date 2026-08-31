"""Shared OpenAlex API functions: querying, caching, and version resolution."""

import json
import time
from pathlib import Path

import requests


OPENALEX_BASE = "https://api.openalex.org"
POLITE_EMAIL = "sima.research@example.com"
CACHE_FILE = Path("openalex_cache.json")


def load_cache():
    if CACHE_FILE.exists():
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def query_by_doi(doi, cache):
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


def query_by_title(title, cache):
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


def query_by_id(openalex_id, cache):
    """Fetch a work's referenced_works by its OpenAlex ID."""
    cache_key = f"id:{openalex_id}"
    if cache_key in cache:
        return cache[cache_key]

    short_id = openalex_id.replace("https://openalex.org/", "")
    url = f"{OPENALEX_BASE}/works/{short_id}"
    params = {"select": "id,title,referenced_works", "mailto": POLITE_EMAIL}

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
        cache[cache_key] = None
        return None
    except requests.RequestException:
        return None


def find_all_versions(title, first_author, known_id, cache):
    """Find all versions of a paper on OpenAlex.

    Many papers exist as multiple OpenAlex records (working paper vs journal,
    preprint vs publication). We want to identify all versions so that
    forward and reverse matching catches all citations.
    """
    cache_key = f"all_versions:{known_id}"
    if cache_key in cache:
        return cache[cache_key]

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


def search_works(query, year_from=None, year_to=None, per_page=25):
    """Search OpenAlex for papers matching a query, sorted by citation count."""
    filters = []
    if year_from:
        filters.append(f"from_publication_date:{year_from}-01-01")
    if year_to:
        filters.append(f"to_publication_date:{year_to}-12-31")

    url = f"{OPENALEX_BASE}/works"
    params = {
        "search": query,
        "sort": "cited_by_count:desc",
        "per_page": per_page,
        "mailto": POLITE_EMAIL,
    }
    if filters:
        params["filter"] = ",".join(filters)

    try:
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            return resp.json().get("results", [])
        return []
    except requests.RequestException:
        return []
