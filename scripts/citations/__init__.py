"""Citation extraction package with modular pipeline components."""

from .config import CitationConfig, load_config
from .models import (
    CitationCandidate,
    ExtractionContext,
    StrategyOutcome,
    StrategyResult,
)
from .pipeline import CitationPipeline

__all__ = [
    "CitationCandidate",
    "CitationConfig",
    "CitationPipeline",
    "ExtractionContext",
    "StrategyOutcome",
    "StrategyResult",
    "load_config",
]
