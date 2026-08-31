# PaperConnect

Tooling for a narrative review on imputation methods for multivariate time series, focused on air quality data from SIMA (Sistema Integral de Monitoreo Ambiental) in Monterrey, Mexico.

## What's in this repo

- **`citation_graph.py`** — Builds an interactive citation graph from a Zotero `.bib` export. Queries OpenAlex for citation relationships, resolves multi-version papers, and generates an HTML visualization with search and timeline view.
- **`search_papers.py`** — Searches OpenAlex for papers by topic and year range, filters out papers already in the collection, and logs results to `search_log.csv`.
- **`paperconnect/`** — Shared OpenAlex API module used by both tools.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Generate the citation graph

```bash
python citation_graph.py
```

Opens `citation_graph.html` in your browser. Features:
- Nodes colored by era (red = foundational, orange = classical, green = ML, blue = deep learning, purple = recent)
- Node size by citation count within the collection
- Search bar with autocomplete
- Timeline view button (top-right)

### Search for papers

```bash
python search_papers.py "imputation time series air quality" --from 2000 --to 2015 -n 10
```

Results are printed to the terminal and logged to `search_log.csv`.

## Project context

This repo is tooling only — the manuscript is written separately. See `PLAN.md` for the project roadmap.
