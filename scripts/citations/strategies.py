from __future__ import annotations

import logging
import re
from typing import Optional

import requests
from scholarly import scholarly

from .config import CitationConfig
from .interactions import InteractionProvider
from .models import ExtractionContext, StrategyOutcome, StrategyResult

LOGGER = logging.getLogger(__name__)


class BaseStrategy:
    name = "base"

    def applicable(self, ctx: ExtractionContext, config: CitationConfig) -> bool:
        return True

    def skip_reason(self, ctx: ExtractionContext, config: CitationConfig) -> str:
        return "Not applicable"

    def execute(
        self,
        ctx: ExtractionContext,
        config: CitationConfig,
        interactions: InteractionProvider,
    ) -> StrategyResult:
        raise NotImplementedError


class DOIStrategy(BaseStrategy):
    name = "doi"
    DOI_PATTERN = re.compile(r"10\.\d{4,}(?:\.\d+)?/[\w\-.;()/:%]+", re.IGNORECASE)

    def applicable(self, ctx: ExtractionContext, config: CitationConfig) -> bool:
        if config.skip_doi:
            return False
        return bool(self._extract_doi(ctx))

    def skip_reason(self, ctx: ExtractionContext, config: CitationConfig) -> str:
        if config.skip_doi:
            return "Disabled via --skip-doi"
        doi = ctx.metadata.get("doi") or self._extract_doi(ctx)
        if not doi:
            return "No DOI detected"
        return "Not applicable"

    def execute(
        self,
        ctx: ExtractionContext,
        config: CitationConfig,
        interactions: InteractionProvider,
    ) -> StrategyResult:
        doi = self._extract_doi(ctx)
        if not doi:
            return StrategyResult(StrategyOutcome.SKIPPED, message="No DOI in context")
        if doi.lower() in ctx.tried_dois:
            return StrategyResult(StrategyOutcome.SKIPPED, message="DOI already tried")
        ctx.tried_dois.add(doi.lower())
        LOGGER.info("Attempting DOI lookup for %s", doi)
        try:
            response = requests.get(
                f"https://doi.org/{doi}",
                headers={"Accept": "application/x-bibtex"},
                timeout=config.doi_timeout,
            )
        except Exception as exc:  # pragma: no cover - network failures
            LOGGER.warning("DOI lookup error for %s: %s", ctx.pdf_path.name, exc)
            return StrategyResult(StrategyOutcome.FAILED, message=str(exc))
        if response.status_code == 200 and response.text.strip().startswith("@"):
            LOGGER.info("DOI lookup succeeded for %s", ctx.pdf_path.name)
            ctx.metadata.setdefault("doi", doi)
            return StrategyResult(
                StrategyOutcome.SUCCESS,
                bibtex=response.text.strip(),
                metadata=dict(ctx.metadata),
            )
        LOGGER.warning(
            "DOI lookup failed for %s (status=%s)", ctx.pdf_path.name, response.status_code
        )
        return StrategyResult(StrategyOutcome.FAILED, message=f"HTTP {response.status_code}")

    def _extract_doi(self, ctx: ExtractionContext) -> Optional[str]:
        if ctx.metadata.get("doi"):
            return ctx.metadata["doi"]
        match = self.DOI_PATTERN.search(ctx.text)
        if match:
            ctx.metadata["doi"] = match.group(0).rstrip(".)")
            return ctx.metadata["doi"]
        return None


class ScholarStrategy(BaseStrategy):
    name = "scholar"

    def applicable(self, ctx: ExtractionContext, config: CitationConfig) -> bool:
        title = ctx.metadata.get("title")
        if not title:
            return False
        return title.lower() not in ctx.tried_titles

    def skip_reason(self, ctx: ExtractionContext, config: CitationConfig) -> str:
        title = ctx.metadata.get("title")
        if not title:
            return "No title candidate"
        if title.lower() in ctx.tried_titles:
            return "Title already tried"
        return "Not applicable"

    def execute(
        self,
        ctx: ExtractionContext,
        config: CitationConfig,
        interactions: InteractionProvider,
    ) -> StrategyResult:
        title = ctx.metadata.get("title")
        if not title:
            return StrategyResult(StrategyOutcome.SKIPPED, message="No title candidate")
        lowered = title.lower()
        if lowered in ctx.tried_titles:
            return StrategyResult(StrategyOutcome.SKIPPED, message="Title already tried")
        ctx.tried_titles.add(lowered)
        LOGGER.info("Searching Scholar for '%s'", title)
        try:
            search = scholarly.search_pubs(title)
            result = next(search, None)
        except StopIteration:
            result = None
        except Exception as exc:  # pragma: no cover - network failures
            LOGGER.warning("Scholar lookup error for %s: %s", ctx.pdf_path.name, exc)
            return StrategyResult(StrategyOutcome.FAILED, message=str(exc))
        if not result:
            return StrategyResult(StrategyOutcome.FAILED, message="No Scholar results")
        bibtex = scholarly.bibtex(result)
        if not bibtex or not bibtex.strip().startswith("@"):
            return StrategyResult(StrategyOutcome.FAILED, message="Scholar result had no BibTeX")
        LOGGER.info("Scholar lookup succeeded for %s", ctx.pdf_path.name)
        return StrategyResult(
            StrategyOutcome.SUCCESS,
            bibtex=bibtex.strip(),
            metadata=dict(ctx.metadata),
        )


class ManualStrategy(BaseStrategy):
    name = "manual"

    def execute(
        self,
        ctx: ExtractionContext,
        config: CitationConfig,
        interactions: InteractionProvider,
    ) -> StrategyResult:
        LOGGER.info("Prompting user for manual citation (%s)", ctx.pdf_path.name)
        title = interactions.prompt("Title", ctx.metadata.get("title", ctx.pdf_path.stem))
        authors = interactions.prompt("Authors (BibTeX format)")
        journal = interactions.prompt("Journal")
        year = interactions.prompt("Year", ctx.metadata.get("year", ""))
        if not title or not authors or not journal or not year:
            return StrategyResult(StrategyOutcome.FAILED, message="Missing required fields")
        doi = interactions.prompt("DOI (optional)", ctx.metadata.get("doi", ""))
        pages = interactions.prompt("Pages (optional)")
        volume = interactions.prompt("Volume (optional)")
        number = interactions.prompt("Number (optional)")
        url = interactions.prompt("URL (optional)")
        key_default = ctx.pdf_path.stem.replace(" ", "")
        bib_key = interactions.prompt("BibTeX key", key_default)
        lines = [f"@article{{{bib_key},"]
        lines.append(f"    author = {{{authors}}},")
        lines.append(f"    title = {{{title}}},")
        lines.append(f"    journal = {{{journal}}},")
        lines.append(f"    year = {{{year}}},")
        if volume:
            lines.append(f"    volume = {{{volume}}},")
        if number:
            lines.append(f"    number = {{{number}}},")
        if pages:
            lines.append(f"    pages = {{{pages}}},")
        if doi:
            lines.append(f"    doi = {{{doi}}},")
        if url:
            lines.append(f"    url = {{{url}}},")
        lines.append("}")
        return StrategyResult(
            StrategyOutcome.NEEDS_REVIEW,
            bibtex="\n".join(lines),
            metadata={"title": title, "author": authors, "year": year, "journal": journal, "doi": doi},
            message="Manual entry",
        )


STRATEGIES = [DOIStrategy(), ScholarStrategy(), ManualStrategy()]
