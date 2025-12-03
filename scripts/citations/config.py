from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

DEFAULT_REFERENCES_DIR = Path("references")
DEFAULT_OUTPUT_BIB = DEFAULT_REFERENCES_DIR / "references.bib"
DEFAULT_REJECTED_DIR = DEFAULT_REFERENCES_DIR / "rejected"
DEFAULT_REJECTED_LOG = DEFAULT_REJECTED_DIR / "rejected.md"


def _int_from_env(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class CitationConfig:
    references_dir: Path = DEFAULT_REFERENCES_DIR
    output_bib: Path = DEFAULT_OUTPUT_BIB
    rejected_dir: Path = DEFAULT_REJECTED_DIR
    rejected_log: Path = DEFAULT_REJECTED_LOG
    skip_doi: bool = False
    interactive: bool = True
    ocr_dpi: int = _int_from_env("OCR_DPI", 600)
    ocr_preview_chars: int = _int_from_env("OCR_PREVIEW_CHARS", 500)
    llm_model: str = os.environ.get("OCR_TITLE_MODEL", "models/gemini-2.5-pro")
    llm_max_chars: int = _int_from_env("MAX_LLM_INPUT_CHARS", 4000)
    llm_temperature: float = float(os.environ.get("LLM_TEMPERATURE", "0.3"))
    llm_max_tokens: int = _int_from_env("LLM_MAX_OUTPUT_TOKENS", 400)
    doi_timeout: int = _int_from_env("DOI_TIMEOUT_SECONDS", 10)
    summary_path: Optional[Path] = None
    run_log_path: Optional[Path] = None


def load_config(
    references_dir: Optional[Path] = None,
    output_bib: Optional[Path] = None,
    skip_doi: Optional[bool] = None,
    interactive: Optional[bool] = None,
    run_log_path: Optional[Path] = None,
) -> CitationConfig:
    base = CitationConfig()
    return CitationConfig(
        references_dir=references_dir or base.references_dir,
        output_bib=output_bib or base.output_bib,
        rejected_dir=base.rejected_dir,
        rejected_log=base.rejected_log,
        skip_doi=base.skip_doi if skip_doi is None else skip_doi,
        interactive=base.interactive if interactive is None else interactive,
        ocr_dpi=base.ocr_dpi,
        ocr_preview_chars=base.ocr_preview_chars,
        llm_model=base.llm_model,
        llm_max_chars=base.llm_max_chars,
        llm_temperature=base.llm_temperature,
        llm_max_tokens=base.llm_max_tokens,
        doi_timeout=base.doi_timeout,
        summary_path=base.summary_path,
        run_log_path=run_log_path or base.run_log_path,
    )
