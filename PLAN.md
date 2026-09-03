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

## Phase 1.5: Citation Graph Improvements (DONE)

**Objective:** Fix known issues and add usability features to the citation graph.

### Bug fixes
- [x] Investigate missing edge: "The estimation of multivariate normal density functions using incomplete data" — root cause was multi-version papers on OpenAlex (e.g., Rubin 1975 ETS vs Rubin 1976 Biometrika). Fixed by reworking `find_canonical_version()` into `find_all_versions()` to collect all version IDs instead of just one
- [x] Check if similar matching failures affect other papers — fix applies globally to all papers in the collection
- [x] Fix isolated preprints (e.g., Mahmud 2025 ImpuGAN): arXiv versions often have 0 references on OpenAlex. Now fetches references from published alternate versions when the original has none
- [x] Fix .bib parser compatibility with Zotero re-exports: handle `date` field (not just `year`) and accept non-standard entry types like `@report` (Dempster 1977, Murray 1979, etc. were being silently skipped)

### New features
- [x] Search bar: autocomplete dropdown that filters and highlights matching nodes, click to zoom
- [x] Timeline view: static matplotlib timeline (papers on year axis with citation arrows)
- [x] View switcher: top-right menu toggles between "Interactive View" (graph) and "Timeline View" (timeline) — replaces the old overlay approach
- [x] Click-to-highlight: clicking a node dims all unconnected nodes/edges, highlights the selected node and its neighbors. Click empty space to restore.
- [x] Color legend: always-visible legend (bottom-left) showing era colors in both views
- [x] Improved node spacing: stronger repulsion and longer springs to reduce overlap

---

## Phase 1.7: Address Peer Review Gaps (CURRENT — prioritized over 1.6)

**Objective:** Strengthen the collection based on NotebookLM peer review feedback and professor meeting (2026-09-02). Focus on gaps that fit our scope.

**Key decision (2026-09-03):** Phase 1.7 is now prioritized *before* finishing Phase 1.6 (extraction matrix). Reason: the extraction matrix needs columns like "Assumed missingness mechanism" and "Relevance to taxonomy." Without understanding the MNAR landscape first, those columns can't be filled meaningfully.

**Professor meeting feedback (2026-09-02):**
- Professors confirmed the MNAR gap is the highest priority
- The central problem: modern DL imputation methods (BRITS, SAITS, CSDI) don't state or verify the theoretical conditions (missingness mechanism) under which they are valid — the justification that links Rubin's framework to the method is missing
- Fernando noted that Sun, Qin & Huang (2018) — "Missing Information Principle" — is the only paper in the collection that touches this. We traced its citations via OpenAlex but found they are survival analysis focused, not useful for the imputation bridge.
- Valeria finds it difficult to understand the types of MNAR — this is a reading priority

**Scope decisions (2026-08-31):** The peer review identified 7 areas of concern. We evaluated each against our review's focus (imputation methods for multivariate time series in air quality) and made the following calls. These decisions can be revisited if a journal reviewer or Facundo disagrees:

- **MNAR mechanisms → IN SCOPE.** Sensor saturation at SIMA is textbook MNAR. Our review should acknowledge this and cover sensitivity analysis approaches. Without this, a reviewer could argue our applied framing is naive.
- **Imputation uncertainty propagation → IN SCOPE.** The tension between Rubin's proper inference and deep learning's RMSE optimization is the central narrative thread of our review (from Rubin to SAITS). We need papers that bridge this.
- **Burst missingness / long gaps → IN SCOPE.** Multi-day sensor outages are a real SIMA problem. Relevant to our applied context.
- **Bidirectional info leakage → BRIEF MENTION.** Valid point about real-time vs. retrospective, but it's an operational concern, not a methodological gap. One paragraph in discussion.
- **Extreme value / regulatory peaks → BRIEF FUTURE WORK.** Important for SIMA's regulatory context but it's a specialized topic beyond our review's arc.
- **Causal inference (m-DAGs, TMLE) → OUT OF SCOPE.** Our review is about imputation methods, not causal epidemiology. Adding this would change the paper's focus entirely.
- **Spatial methods (kriging, INLA, GP) → BRIEF FUTURE WORK.** Our narrative follows a temporal arc (statistics → ML → deep learning). Geostatistics is a parallel branch, not part of that evolution.

### Gap 1: MNAR mechanisms + Rubin-to-DL bridge (high priority) — IN PROGRESS

**Approach:** Used NotebookLM deep search (free, saves Claude tokens) instead of OpenAlex keyword search (too noisy for conceptual gaps). Results in `Notebooklm/research-report-bridging-missing-data.md`.

NotebookLM found 11 candidate papers across 4 themes:
1. MNAR identification & sensitivity analysis (NARFCS, tipping-point analysis)
2. Theoretical validity of DL under different mechanisms (FragmGAN proving GAIN assumes MCAR, VAE conditions under MAR)
3. Deep generative models designed for MNAR (MIWAE, not-MIWAE, PSMVAE, GNR)
4. RMSE vs. inferential validity tension (van Buuren "imputation is not prediction", Beyond Accuracy benchmark)

**Important caveat:** These 11 papers are mostly about tabular data, not time series. The bridge between MNAR theory and time series DL (BRITS, SAITS) specifically is still a gap — will need to be addressed in writing.

**Known gap in the 11 candidates:** All are post-2018. Missing the older foundational work (1990s-2010s) on pattern-mixture models, selection models, and early MNAR theory that the newer papers build on. Plan: after reviewing the 11 candidates, run a second NotebookLM deep search targeting pre-2018 foundations.

- [x] NotebookLM deep search #1: modern bridge papers (2018-2025) — 11 candidates found
- [x] Review and triage the 11 candidates — 6 accepted, 5 skipped. Added to Zotero and .bib.
  - ADD: #1 NARFCS (Tompsett 2018), #3 FragmGAN (Fang 2023), #5 MIWAE (Mattei 2019), #6 not-MIWAE (Ipsen 2021), #8 PSMVAE (Ghalebikesabi 2021), #10 Beyond Accuracy (2025)
  - SKIP: #2 Tipping Point, #4 Nazábal VAE, #7 GNR, #9 IVGAE, #11 van Buuren
- [ ] NotebookLM deep search #2: pre-2018 foundational MNAR/pattern-mixture/selection model theory
- [ ] Triage second batch of candidates
- [ ] Re-run citation graph to verify the bridge connects

### Gap 2: Imputation uncertainty propagation (high priority)
- [ ] Search for papers on Rubin's pooling rules applied to deep learning, conformal prediction intervals for time series imputation
- [ ] Triage and add to collection
- Note: partially covered by Gap 1 candidates — van Buuren (2018) and "Beyond Accuracy" (2025) address this directly

### Gap 3: Burst missingness / long consecutive gaps (medium priority)
- [ ] Search for papers specifically addressing multi-day sensor outages or long gap imputation
- [ ] Triage and add to collection

### Discussion section additions (for Phase 4 writing)
- [ ] Point reconstruction vs. inferential validity — the field traded rigor (Rubin) for accuracy (SAITS). Core narrative thread.
- [ ] Bidirectional info leakage — retrospective reconstruction vs. real-time alerting. Brief paragraph.
- [ ] Extreme value / regulatory peaks — RMSE-optimized models underpredict toxic peaks. Brief future work.
- [ ] Spatiotemporal methods — mention as a future direction, not part of our arc.

---

## Phase 1.6: Collection Analysis (PAUSED — waiting on 1.7)

**Objective:** Use the citation graph to understand the collection's strengths, gaps, and guide what to read or add next.

### Tasks
- [x] Year distribution analysis: identified thin spots in 1980-1999 (practical MI era), 2000-2014 (ML bridge — only 6 relevant papers), and 2015-2018 (early deep learning imputation like GAIN/BRITS)
- [x] OpenAlex search tool (`search_papers.py`): searches by topic + year range, filters out papers already in collection, sorted by citations. Logs all searches to `search_log.csv` for methodology traceability
- [x] Candidate paper triage: used NotebookLM to compare candidate papers (from search tool) against current collection. 3-step process: (1) baseline analysis of current collection's coverage and blind spots, (2) novelty filter to find candidates that fill gaps, (3) generate ADD/SKIP verdicts with rationale. Results saved to `Notebooklm/candidates_veredict.csv`. Updated `.bib` with accepted papers.
- [ ] Extraction matrix template: build a structured CSV/table matching Phase 2 columns, ready to fill in as the team reads papers (blocked on finishing 1.7 — need MNAR understanding first)

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



## Phase 4: Article Writing

**Narrative arc:** Classical statistical foundations (Rubin, EM, MI) --> Traditional methods (interpolation, regression, KNN, Kalman) --> Machine learning (SOM, MLP, RF) --> Deep generative models (GANs, VAEs, diffusion, transformers/SAITS/CSDI) --> Application to air quality --> Limitations & open challenges

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
