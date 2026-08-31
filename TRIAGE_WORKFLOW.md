# Paper Triage Workflow (Personal Reference)

## Prerequisites
- Two Zotero subcollections: one with your current papers, one with candidates (extracted from `search_log.csv`)
- Export both as CSV with abstracts

## Step 1: Establish the Baseline
Upload both CSVs to NotebookLM. Select only your current collection CSV in the source panel and run:

> "Analyze the abstracts in this CSV. Give me a structured summary of my current literature review on missing data inferences. What specific mechanisms (e.g., MCAR, MAR, MNAR) and imputation methods (e.g., MICE, Deep Learning, listwise deletion) are already heavily represented here? What are the blind spots?"

Pin the best response to a Note — this forces the AI to hold your "known research" in its active memory.

## Step 2: The Novelty Filter
Select both CSVs in the source panel. Run:

> "I have two sources selected. One is my 'Current Collection' and the other is a list of 'Candidate Papers'. Compare the abstracts of the candidates against my current collection. Identify any candidate papers that introduce novel imputation techniques, address the blind spots we just identified, or apply missing data theory to new domains not covered in my current library. Group your recommendations by theme."

## Step 3: Generate the Triage Table
Run:

> "Act as a senior research advisor. Evaluate every abstract in the 'Candidate Papers' CSV against the 'Current Collection' CSV. Generate a strict triage list formatted as a Markdown table with the following columns:
>
> DOI | Title | Verdict (ADD/SKIP) | Rationale (1-sentence justification based on the abstract).
>
> Only evaluate the candidate papers."

## Step 4: Save and Apply
- Copy the Markdown table into `candidates_veredict.csv`
- Add accepted papers (ADD) to Zotero and re-export `SIMA PERSONAL.bib`
- Regenerate the citation graph
