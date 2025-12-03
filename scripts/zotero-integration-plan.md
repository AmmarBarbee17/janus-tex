# Zotero Integration Action Plan

## Objectives
- Preserve the curated PDF intake workflow provided by `scripts/extract_citations.py`.
- Leverage Zotero + Better BibTeX to enrich metadata, collaborate, and auto-export citation files.
- Keep LaTeX builds (`compile.bat`) consuming a single, consistently formatted `references/references.bib`.
- Maintain the rejection audit trail already established in `references/rejected/`.

## Phase 1 – Environment Setup
1. Install Zotero desktop and browser connector on the primary workstation.
2. Install the Better BibTeX (BBT) Zotero plugin for stable citation keys and auto-export support.
3. Create or select a Zotero account and enable sync so group members can share the library later.

## Phase 2 – Library Structure
1. Create a Zotero collection named "Janus AFP" (or similar) dedicated to this project.
2. Within the collection, define tags that mirror our local categories (e.g., `review`, `process`, `materials`).
3. Configure Zotero sync to include file attachments if collaboration requires shared PDFs; otherwise rely on local storage to avoid duplication.

## Phase 3 – Ingestion Workflow Coupling
1. Continue running `python scripts/extract_citations.py` for every new PDF drop:
   - Accepted entries append to `references/references.bib` and rename the PDF.
   - Rejected items move to `references/rejected/` with `rejected.md` logging.
2. After a successful run, bulk-import the newly accepted BibTeX entries into the Zotero "Janus AFP" collection:
   - Zotero → `File > Import > BibTeX` and point to `references/references.bib`.
   - Use Zotero's dedupe pane to merge duplicates rather than adjusting the Python script.
3. Allow Zotero translators to enhance metadata (abstracts, keywords, DOIs) and attach supplementary files when useful.

## Phase 4 – Better BibTeX Auto-Export
1. Open Zotero → right-click the "Janus AFP" collection → `Export Collection`.
2. Choose the `Better BibLaTeX` format, set the destination to `references/references.bib`, and check `Keep Updated`.
3. In BBT preferences:
   - Citation key formula: `{authors3}{year}` to stay aligned with our `AuthorYear` keys.
   - Enable `Quick Copy` if citation drag-and-drop is needed for notes.
4. Verify the exporter rewrites `references/references.bib` in the aligned, indented format we now rely on.

## Phase 5 – Day-to-Day Usage
1. Primary intake remains the Python script:
   - OCR fallback, suspicious-title gating, DOI auto-accept, and rejection log stay authoritative.
2. After Zotero enriches entries:
   - Use Zotero notes/tags for annotations and collaboration.
   - Attach cleaned PDFs from `references/` so readers reach the same file versions.
3. For LaTeX builds, continue running `compile.bat`; it will pick up the latest exported `.bib`.
4. For Word/LibreOffice documents, install the Zotero cite-while-you-write plugin to pull the same references.

## Phase 6 – Rejection & Cleanup Hygiene
1. When Zotero reveals an irrelevant or incorrect item, delete it there and drop the associated PDF back into `references/rejected/` (or tag it `rejected`) to preserve the audit trail.
2. Periodically prune the `rejected/` folder and update `rejected.md` summaries if the reason metadata needs refinement.
3. Run `python scripts/extract_citations.py --skip-doi` when testing to avoid redundant auto-imports during experimentation.

## Phase 7 – Validation & Training
1. Smoke-test the full loop with two sample PDFs:
   - One DOI-rich article to confirm auto-acceptance and Zotero import.
   - One ambiguous article to ensure the rejection path mirrors Zotero tagging.
2. Document the workflow in `scripts/README.md` once validated, referencing this plan.
3. Provide teammates a quick-reference guide covering: PDF drop location, script usage, Zotero collection etiquette, and LaTeX/BibTeX refresh steps.

## Metrics & Review
- Monthly: review Zotero duplicate logs and rejected.md for false positives.
- Quarterly: confirm BBT auto-export still targets `references/references.bib` and that LaTeX builds succeed without manual citation edits.
- Update this plan as tooling evolves (e.g., if switching to Overleaf sync or adopting a lab-wide Zotero group).
