from __future__ import annotations

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


def setup_logging(verbose: bool = False, log_path: Optional[Path] = None) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    logging.getLogger("pdfminer").setLevel(logging.WARNING)
    logging.getLogger("pdfplumber").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    if log_path:
        logging.getLogger(__name__).info("Mirroring terminal output to %s", log_path)


def log_rejection(log_path: Path, entry_name: str, reason: str) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if not log_path.exists():
        log_path.write_text("# Rejected References\n\n| Date | File | Reason |\n| --- | --- | --- |\n", encoding="utf-8")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    sanitized = " ".join(reason.split()) or "unspecified"
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"| {timestamp} | `{entry_name}` | {sanitized} |\n")


def summarize_run(summary_path: Optional[Path], stats: dict[str, int]) -> None:
    if not summary_path:
        return
    summary_lines = ["Citation Extraction Summary", "============================", ""]
    for key, value in stats.items():
        summary_lines.append(f"- {key}: {value}")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")


def write_run_log_entry(run_log_path: Optional[Path], payload: dict[str, Any]) -> None:
    if not run_log_path:
        return
    entry = {"timestamp": datetime.now().isoformat(), **payload}
    run_log_path.parent.mkdir(parents=True, exist_ok=True)
    with run_log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
