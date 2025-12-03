from __future__ import annotations

import logging
import re
import shutil
from pathlib import Path
from typing import Dict, Optional, Tuple

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
import pdfplumber

from .config import CitationConfig
from .interactions import InteractionProvider, provider_for_mode
from .logging_utils import log_rejection, summarize_run, write_run_log_entry
from .models import ExtractionContext, StrategyOutcome
from .strategies import STRATEGIES

LOGGER = logging.getLogger(__name__)


class CitationPipeline:
    STEP_SEQUENCE: Tuple[Tuple[str, str], ...] = (
        ("text", "Extract text (first two pages)"),
        ("doi", "Strategy 1: DOI lookup"),
        ("scholar", "Strategy 2: Scholar lookup"),
        ("manual", "Strategy 3: Manual entry prompts"),
        ("review", "Review + confirm"),
        ("store", "Append to references.bib + rename PDF"),
    )
    STRATEGY_TO_STEP = {"doi": "doi", "scholar": "scholar", "manual": "manual"}
    STEP_LABELS = dict(STEP_SEQUENCE)
    STEP_SYMBOLS = {"pending": "[ ]", "success": "[x]", "skipped": "[-]", "failed": "[!]"}

    def __init__(self, config: CitationConfig, interactions: Optional[InteractionProvider] = None) -> None:
        self.config = config
        self.interactions = interactions or provider_for_mode(config.interactive)
        self.stats: Dict[str, int] = {"processed": 0, "accepted": 0, "rejected": 0}

    def process_directory(self) -> int:
        pdfs = sorted(self.config.references_dir.glob("*.pdf"))
        if not pdfs:
            LOGGER.info("No PDF files found in %s", self.config.references_dir)
            return 0
        for idx, pdf in enumerate(pdfs):
            if idx > 0:
                LOGGER.info("")
            if self.process_pdf(pdf):
                self.stats["accepted"] += 1
            else:
                self.stats["rejected"] += 1
            self.stats["processed"] += 1
        summarize_run(self.config.summary_path, self.stats)
        return self.stats["accepted"]

    def process_pdf(self, pdf_path: Path) -> bool:
        LOGGER.info("Processing %s", pdf_path.name)
        step_status = self._init_step_statuses()
        text = self._read_pdf_text(pdf_path)
        if not text.strip():
            self._set_step_status(step_status, "text", "failed", "No text extracted", emit=True)
            self._finalize_pending_statuses(step_status)
            self._reject(pdf_path, "Unable to extract text")
            return False
        self._set_step_status(step_status, "text", "success", emit=True)
        context = ExtractionContext(pdf_path=pdf_path, text=text, metadata=self._extract_metadata(text))
        for strategy in STRATEGIES:
            step_key = self.STRATEGY_TO_STEP.get(strategy.name)
            if not strategy.applicable(context, self.config):
                if step_key:
                    self._set_step_status(
                        step_status,
                        step_key,
                        "skipped",
                        strategy.skip_reason(context, self.config),
                        emit=True,
                    )
                continue
            result = strategy.execute(context, self.config, self.interactions)
            if step_key:
                if result.outcome in {StrategyOutcome.SUCCESS, StrategyOutcome.NEEDS_REVIEW}:
                    note = result.message or None
                    self._set_step_status(step_status, step_key, "success", note, emit=True)
                elif result.outcome == StrategyOutcome.SKIPPED:
                    self._set_step_status(step_status, step_key, "skipped", result.message or None, emit=True)
                    continue
                elif result.outcome == StrategyOutcome.FAILED:
                    self._set_step_status(step_status, step_key, "failed", result.message or None, emit=True)
                    continue
            if result.outcome in {StrategyOutcome.SKIPPED, StrategyOutcome.FAILED}:
                continue
            bibtex = result.bibtex or ""
            if not bibtex.strip():
                continue
            source_label = self.STEP_LABELS.get(step_key or "manual", "Automated strategy")
            if not self._review_and_store(pdf_path, bibtex, result.metadata, step_status, source_label):
                self._set_step_status_if_pending(step_status, "store", "skipped", "Not reached", emit=True)
                self._finalize_pending_statuses(step_status)
                self._log_run(pdf_path, strategy.name, "discarded", {
                    "metadata": result.metadata,
                    "reason": "user_rejected",
                })
                return False
            summary = self._summarize_bibtex(bibtex)
            self._mark_not_needed_steps(step_status, step_key)
            self._finalize_pending_statuses(step_status)
            self._log_run(pdf_path, strategy.name, "accepted", {
                "metadata": result.metadata,
                "bibtex_summary": summary,
            })
            return True
        self._set_step_status_if_pending(step_status, "manual", "skipped", "No viable strategy", emit=True)
        self._set_step_status_if_pending(step_status, "review", "skipped", "No candidate", emit=True)
        self._set_step_status_if_pending(step_status, "store", "skipped", "No candidate", emit=True)
        self._finalize_pending_statuses(step_status)
        self._reject(pdf_path, "All strategies exhausted")
        return False

    def _review_and_store(
        self,
        pdf_path: Path,
        bibtex: str,
        metadata: Dict[str, str],
        step_status: Dict[str, Tuple[str, Optional[str]]],
        source_label: str,
    ) -> bool:
        summary = self._summarize_bibtex(bibtex)
        LOGGER.info("Candidate citation for %s:", pdf_path.name)
        if summary:
            for key in ["title", "author", "journal", "year", "doi"]:
                if summary.get(key):
                    LOGGER.info("    • %s: %s", key.capitalize(), summary[key])
        prompt = f"  Accept this entry? ({source_label})"
        if not self.interactions.confirm(prompt, default_yes=True):
            LOGGER.warning("User rejected citation (%s)", pdf_path.name)
            self._set_step_status(step_status, "review", "failed", "User rejected candidate", emit=True)
            return False
        self._set_step_status(step_status, "review", "success", emit=True)
        LOGGER.info("Approval: Derived from %s", source_label)
        if not self._append_to_bib(bibtex):
            self._set_step_status(step_status, "store", "failed", "Failed to write references.bib", emit=True)
            return False
        self._rename_pdf(pdf_path, summary or metadata)
        self._set_step_status(step_status, "store", "success", emit=True)
        return True

    def _append_to_bib(self, bibtex: str) -> bool:
        try:
            new_db = bibtexparser.loads(bibtex)
        except Exception as exc:
            LOGGER.error("Invalid BibTeX entry: %s", exc)
            return False
        if not new_db.entries:
            LOGGER.error("BibTeX entry missing data")
            return False
        entry = dict(new_db.entries[0])
        parser = BibTexParser(common_strings=True)
        try:
            with self.config.output_bib.open("r", encoding="utf-8") as handle:
                database = bibtexparser.load(handle, parser=parser)
        except Exception:
            database = BibDatabase()
        database.entries = getattr(database, "entries", []) or []
        database.entries.append(entry)
        writer = BibTexWriter()
        writer.indent = "    "
        writer.order_entries_by = None
        formatted = writer.write(database)
        self.config.output_bib.parent.mkdir(parents=True, exist_ok=True)
        self.config.output_bib.write_text(formatted, encoding="utf-8")
        LOGGER.info("Appended citation to %s", self.config.output_bib)
        return True

    def _rename_pdf(self, pdf_path: Path, metadata: Dict[str, str]) -> None:
        author = metadata.get("author", "").split(" and ")[0].split(",")[0].split(" ")[-1]
        author = "".join(ch for ch in author if ch.isalpha())
        year = "".join(ch for ch in (metadata.get("year") or "") if ch.isdigit())
        if not author or not year:
            return
        candidate = f"{author}{year}.pdf"
        destination = pdf_path.with_name(candidate)
        counter = 1
        while destination.exists() and destination != pdf_path:
            destination = pdf_path.with_name(f"{author}{year}_{counter}.pdf")
            counter += 1
        if destination == pdf_path:
            return
        try:
            pdf_path.rename(destination)
            LOGGER.info("Renamed %s → %s", pdf_path.name, destination.name)
        except Exception as exc:
            LOGGER.warning("Failed to rename %s: %s", pdf_path.name, exc)

    def _read_pdf_text(self, pdf_path: Path) -> str:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                pages = pdf.pages[:2]
                return "\n".join(page.extract_text() or "" for page in pages)
        except Exception as exc:
            LOGGER.error("Failed to read %s: %s", pdf_path.name, exc)
            return ""

    def _extract_metadata(self, text: str) -> Dict[str, str]:
        metadata: Dict[str, str] = {}
        year_match = re.search(r"\b(19\d{2}|20\d{2})\b", text)
        if year_match:
            metadata["year"] = year_match.group(1)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for line in lines[:40]:
            if line.isupper() and len(line) > 10:
                metadata.setdefault("title", line.title())
                break
        return metadata

    def _summarize_bibtex(self, bibtex: str) -> Dict[str, str]:
        try:
            db = bibtexparser.loads(bibtex)
        except Exception:
            return {}
        if not db.entries:
            return {}
        entry = db.entries[0]
        return {
            "key": entry.get("ID", ""),
            "title": entry.get("title", ""),
            "author": entry.get("author", ""),
            "journal": entry.get("journal", ""),
            "year": entry.get("year", ""),
            "doi": entry.get("doi", ""),
        }

    def _reject(self, pdf_path: Path, reason: str) -> None:
        LOGGER.warning("Rejecting %s: %s", pdf_path.name, reason)
        self.config.rejected_dir.mkdir(parents=True, exist_ok=True)
        destination = self.config.rejected_dir / pdf_path.name
        counter = 1
        while destination.exists():
            destination = self.config.rejected_dir / f"{pdf_path.stem}_{counter}{pdf_path.suffix}"
            counter += 1
        try:
            shutil.move(str(pdf_path), destination)
        except Exception as exc:
            LOGGER.error("Failed to move %s to rejected/: %s", pdf_path.name, exc)
            destination = pdf_path
        log_rejection(self.config.rejected_log, destination.name, reason)
        self._log_run(pdf_path, "none", "rejected", {"reason": reason})

    def _log_run(self, pdf_path: Path, strategy: str, status: str, extras: Optional[Dict[str, object]] = None) -> None:
        if not self.config.run_log_path:
            return
        payload: Dict[str, object] = {
            "pdf": pdf_path.name,
            "strategy": strategy,
            "status": status,
        }
        if extras:
            payload.update(extras)
        write_run_log_entry(self.config.run_log_path, payload)

    def _init_step_statuses(self) -> Dict[str, Tuple[str, Optional[str]]]:
        return {key: ("pending", None) for key, _ in self.STEP_SEQUENCE}

    def _set_step_status(
        self,
        statuses: Dict[str, Tuple[str, Optional[str]]],
        key: Optional[str],
        state: str,
        note: Optional[str] = None,
        emit: bool = False,
    ) -> None:
        if not key or key not in statuses:
            return
        statuses[key] = (state, note)
        if emit:
            self._emit_step_status(key, state, note)

    def _set_step_status_if_pending(
        self,
        statuses: Dict[str, Tuple[str, Optional[str]]],
        key: str,
        state: str,
        note: Optional[str] = None,
        emit: bool = False,
    ) -> None:
        current = statuses.get(key)
        if not current or current[0] != "pending":
            return
        self._set_step_status(statuses, key, state, note, emit=emit)

    def _mark_not_needed_steps(self, statuses: Dict[str, Tuple[str, Optional[str]]], completed_step: Optional[str]) -> None:
        if completed_step == "doi":
            self._set_step_status_if_pending(statuses, "scholar", "skipped", "Resolved via DOI", emit=True)
            self._set_step_status_if_pending(statuses, "manual", "skipped", "Not needed", emit=True)
        elif completed_step == "scholar":
            self._set_step_status_if_pending(statuses, "manual", "skipped", "Not needed", emit=True)
        elif completed_step == "manual":
            # manual already handled; nothing else to skip
            pass

    def _emit_step_status(self, key: str, state: str, note: Optional[str]) -> None:
        label = self.STEP_LABELS.get(key, key)
        symbol = self.STEP_SYMBOLS.get(state, "[ ]")
        suffix = f" — {note}" if note else ""
        LOGGER.info("%s %s%s", symbol, label, suffix)

    def _finalize_pending_statuses(self, statuses: Dict[str, Tuple[str, Optional[str]]]) -> None:
        for key, (state, note) in list(statuses.items()):
            if state == "pending":
                self._set_step_status(statuses, key, "skipped", "Not reached", emit=True)
