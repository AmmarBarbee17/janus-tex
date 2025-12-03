from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional


class StrategyOutcome(Enum):
    SUCCESS = auto()
    NEEDS_REVIEW = auto()
    SKIPPED = auto()
    FAILED = auto()


@dataclass
class CitationCandidate:
    title: str
    source: str
    bibtex: Optional[str] = None


@dataclass
class StrategyResult:
    outcome: StrategyOutcome
    bibtex: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)
    message: str = ""


@dataclass
class ExtractionContext:
    pdf_path: Path
    text: str
    metadata: Dict[str, str] = field(default_factory=dict)
    tried_dois: set[str] = field(default_factory=set)
    tried_titles: set[str] = field(default_factory=set)
    candidate_titles: List[str] = field(default_factory=list)
    ocr_text: Optional[str] = None