# Citation Extraction Script

Automatically extract BibTeX citations from PDF journal articles in the `references/` directory.

## Features

- **Modular strategy pipeline**:
  1. DOI extraction → CrossRef (fastest, most reliable)
  2. Title extraction → Google Scholar fallback
  3. Guided manual entry when automation fails
- **Interactive review**: Always shows the candidate citation before writing to `references.bib`
- **Rejected queue tracking**: Moves problematic PDFs into `references/rejected/` and logs the reason in `rejected.md`
- **Automatic PDF renaming**: `FirstAuthorLastnameYYYY.pdf` (e.g., `Ehsani2025.pdf`)
- **Configurable behaviour**: Control directories, DOI usage, and interactivity via CLI flags or env vars

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

> **Note:** OCR + LLM title assistance has been disabled for now to keep the workflow deterministic. The new modular design makes it easy to re-enable those strategies later.

## Usage

### Process all PDFs in references/ (one-time)
```bash
python scripts/extract_citations.py
```

> The refreshed pipeline processes the entire `references/` folder in one pass. For targeted runs, move the PDFs you care about into a temporary directory and point `--references-dir` at it.

### Custom options
```bash
# Disable interactive prompts (use for batch processing)
python scripts/extract_citations.py --no-interactive

# Custom directories
python scripts/extract_citations.py --references-dir path/to/pdfs --output citations.bib

# Mirror terminal output to a log file inside references/
python scripts/extract_citations.py --terminal-log references/citations.log
```

## Configuration

The CLI exposes the most common switches so you do not have to edit the code:

- `--references-dir`: Directory that the pipeline scans for `*.pdf` files. Move focused batches into a scratch folder and point this flag there.
- `--output`: Destination `.bib` file. A new database is created automatically when the path does not exist yet.
- `--skip-doi`: Bypass DOI lookups when you know the PDFs will not contain them (e.g., workshop notes). The pipeline goes straight to the Scholar strategy.
- `--no-interactive`: Accept every candidate automatically and suppress the manual entry wizard. Pair this with a temporary directory when running unattended jobs.
- `--run-log`: Persist a JSONL audit trail (one line per PDF) so you can diff or post-process results later. The file is created if it does not exist.
- `--terminal-log`: Tee the entire terminal session into a timestamped log (defaults to `references/citations.log`) so you can grep how each citation made it into the library.

Advanced tuning happens through environment variables that `load_config()` reads once at startup:

| Variable | Default | Purpose |
| --- | --- | --- |
| `OCR_DPI` | `600` | Controls rasterization quality for the future OCR strategy. Higher values improve text extraction but slow down processing. |
| `OCR_PREVIEW_CHARS` | `500` | Length of OCR text snippets shown to the reviewer. |
| `OCR_TITLE_MODEL` | `models/gemini-2.5-pro` | LLM identifier used when the OCR assistant is enabled again. |
| `MAX_LLM_INPUT_CHARS` | `4000` | Safety cap on how much text is sent to the LLM. |
| `LLM_TEMPERATURE` | `0.3` | Sampling temperature for the LLM helper. |
| `LLM_MAX_OUTPUT_TOKENS` | `400` | Response budget for the LLM helper. |
| `DOI_TIMEOUT_SECONDS` | `10` | Network timeout for CrossRef DOI lookups. Lower this when running on flaky connections to keep the batch moving. |

These env vars work in both PowerShell and POSIX shells, for example:

```powershell
$env:DOI_TIMEOUT_SECONDS = 5
python scripts/extract_citations.py --references-dir scratch
```

Unset the variables (or open a new shell) to fall back to the defaults listed above.

## Interactive Mode (Default)

When the DOI + Scholar strategies cannot yield a citation, the pipeline falls back to prompts that gather the required `@article` fields. You can press Enter to accept defaults (usually based on the PDF file name or whatever metadata was parsed from the text). Use `--no-interactive` to automatically accept every candidate and skip manual entry.

## How It Works

1. Extract text from the first two pages of each PDF.
2. Search the text for DOI patterns. If found, fetch BibTeX from CrossRef.
3. If no DOI or the lookup fails, extract an uppercase title line and query Google Scholar.
4. Still stuck? Prompt the user for the missing fields and build an `@article` record.
5. Show the candidate citation for confirmation.
6. On approval, append to `references/references.bib` and rename the PDF.
7. Otherwise move the PDF to `references/rejected/` and record the reason.

## Example

```bash
$ python scripts/extract_citations.py

Found 1 PDF file(s) in references

📄 Processing: 1-s2.0-S1359835X25001691-main.pdf
  Found DOI: 10.1016/j.compositesa.2025.108691
Strategy 1: DOI lookup
  ✓ Success: Retrieved BibTeX from DOI
  ✓ Renamed: 1-s2.0-S1359835X25001691-main.pdf → Ehsani2025.pdf
  ✓ Added to references.bib

============================================================
✓ Complete: Processed 1 file(s)
============================================================
```

## Future Enhancements

- [ ] Reintroduce OCR + LLM strategies inside the new modular pipeline
- [ ] Improved author name parsing for edge cases
- [ ] GUI interface for drag-and-drop operation
- [ ] Integration with Zotero/Mendeley libraries
