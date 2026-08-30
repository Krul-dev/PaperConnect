# SIMA Research - Project Plan with Claude

## Overview

**Goal:** Write a narrative review article on imputation for multivariate time series, focused on air pollution data.

**Working title:** *From Statistical Missing-Data Inference to Deep Generative Imputation for Multivariate Time Series: A Narrative Review*

**Team:** Valeria, Fernando, Arturo + 2 professors (including Facundo)

**Context:** College degree research project. The review will later inform the development of an imputation method for SIMA (Sistema Integral de Monitoreo Ambiental) in Monterrey.

---

## Phase 1: Citation Graph Tool (DONE)

**Objective:** Build an interactive, directed citation graph of the ~75 articles in the Zotero collection. Use it to:
- Identify which articles are central (many connections)
- Spot isolated articles that may not belong
- Discover clusters/communities (classical, air quality, deep learning, etc.)
- Guide decisions about what to keep/discard

**Approach:**
- Language: Python
- Data source: Export from Zotero (.bib already in repo)
- Citation lookup: OpenAlex API (by DOI, with title fallback)
- Forward + reverse citation matching, canonical version resolution
- Visualization: Interactive pyvis — runs locally in browser
- Graph is directed: edge from A to B means "A cites B"

**Input:** `SIMA PERSONAL.bib`

**Output:** Interactive HTML graph + summary of isolated/central nodes

### Tasks
- [x] Parse .bib file, extract metadata (DOI, title, authors, year)
- [x] Query OpenAlex for each article's references
- [x] Match references against other articles in the collection
- [x] Build directed graph (networkx)
- [x] Generate interactive visualization (pyvis)
- [x] Export list of isolated nodes (no connections to other articles in collection)
- [x] Export list of most-cited nodes within the collection (hubs)

---

## Phase 1.5: Citation Graph Improvements (CURRENT)

**Objective:** Fix known issues and add usability features to the citation graph.

### Bug fixes
- [x] Investigate missing edge: "The estimation of multivariate normal density functions using incomplete data" — root cause was multi-version papers on OpenAlex (e.g., Rubin 1975 ETS vs Rubin 1976 Biometrika). Fixed by reworking `find_canonical_version()` into `find_all_versions()` to collect all version IDs instead of just one
- [x] Check if similar matching failures affect other papers — fix applies globally to all papers in the collection

### New features
- [x] Search bar: autocomplete dropdown that filters and highlights matching nodes, click to zoom
- [ ] Timeline view: sort nodes by publication year on one axis while keeping citation arrows (via vis.js position constraints)

---

## Phase 2: Literature Extraction Matrix

**Objective:** Create a structured table to enable comparative writing (arguments, not summaries).

**Columns** (from Facundo's recommendation):
| Column | Description |
|--------|-------------|
| Reference | Author, year |
| Application domain | Air quality, health, traffic, energy, etc. |
| Data type | Univariate / Multivariate time series |
| Number of variables | Count |
| Temporal length | Duration / frequency of data |
| Assumed missingness mechanism | MCAR, MAR, MNAR |
| Evaluated missing pattern | Random, block/gap, mixed |
| Method | Name of imputation method |
| Output type | Point or probabilistic |
| Training loss | Loss function used |
| Metrics | RMSE, MAE, R2, etc. |
| Baselines | What they compared against |
| Advantages | Key strengths |
| Limitations | Key weaknesses |penAlex can be 
| Code/data available | Yes/No + link |
| Relevance to taxonomy | Where it fits in the review's narrative |

**Status:** Not started. Depends on Phase 1 to filter relevant articles.

---

## Phase 3: Review Methodology Section

**Objective:** Write section 2 of the article (methodology of the review itself).

**Subsections** (from Fernando's outline):
- 2.1 Type of review (narrative, interpretive synthesis)
- 2.2 Sources consulted (backward/forward search from seminal articles)
- 2.3 Search strings (table by topic: fundamentals, time series, deep learning, generative, applications)
- 2.4 Inclusion criteria
- 2.5 Exclusion criteria
- 2.6 Synthesis strategy (organize by inferential foundations, method family, output type, missingness mechanism, data structure, computational cost, application domain)

**Status:** Not started. Fernando proposed the structure on Aug 23.

---

## Phase 4: Article Writing

**Narrative arc:** Classical statistical foundations (Rubin, EM, MI) --> Traditional methods (interpolation, regression, KNN, Kalman) --> Machine learning (SOM, MLP, RF) --> Deep generative models (GANs, VAEs, diffusion, transformers/SAITS/CSDI) --> Application to air quality

**Status:** Not started. Depends on Phases 2 and 3.

---

## Notes from Facundo (Aug 24)

- SIMA data available since 1997; can be standardized
- Must review computational capacity to choose appropriate methods
- Climate in 1997 was very different from today — check validity, train multiple models, EDA, prior bias
- Don't discard old data — behavior/shape should be similar
- Prediction model: next-day forecasts, model confidence
- SIMA constraint: 15-minute publishing window (7 min data collection + 7 min calculation, not parallel)
- Machine limitations at SIMA

---

## Potentially Off-Topic Articles (to verify with graph)

These entries in the .bib don't seem to match the review's scope:
- Lee 2005 — mobile ad hoc network routing
- Sarrouy 2009 — intrusion detection
- Zaki 2019 — 3D spatial modeling in MADS
- Espejo Chahuara 2024 — municipal HR management (abstract doesn't match title)
- Dong 2024 (SpecAR-Net) — abstract about multiwinner elections, not time series
- Hamidi 2024 — customer behavior segmentation

---

## Tools & Setup

- **Reference manager:** Zotero (migrated from Mendeley on Aug 24)
- **Language:** Python
- **APIs:** Semantic Scholar, OpenAlex (free, no key needed for basic use)
- **This repo:** Tooling only (not the manuscript)
