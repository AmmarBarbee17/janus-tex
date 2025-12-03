import json
from dataclasses import replace

from citations.config import CitationConfig, load_config
from citations.interactions import InteractionProvider
from citations.models import StrategyOutcome, StrategyResult
from citations.pipeline import CitationPipeline
import citations.pipeline as pipeline_module


class AcceptAllInteractions(InteractionProvider):
    def prompt(self, message: str, default: str = "") -> str:
        return default

    def confirm(self, message: str, default_yes: bool = True) -> bool:
        return True


def make_config(tmp_path) -> CitationConfig:
    refs_dir = tmp_path / "pdfs"
    refs_dir.mkdir()
    config = load_config(
        references_dir=refs_dir,
        output_bib=tmp_path / "references.bib",
        skip_doi=True,
        interactive=False,
        run_log_path=tmp_path / "run-log.jsonl",
    )
    return replace(
        config,
        rejected_dir=tmp_path / "rejected",
        rejected_log=tmp_path / "rejected" / "rejected.md",
        summary_path=tmp_path / "summary.md",
    )


def test_pipeline_accepts_successful_strategy(tmp_path, monkeypatch):
    config = make_config(tmp_path)
    pdf_path = config.references_dir / "paper.pdf"
    pdf_path.write_text("dummy", encoding="utf-8")

    class SuccessfulStrategy:
        name = "success"

        def applicable(self, ctx, cfg):
            return True

        def execute(self, ctx, cfg, interactions):
            return StrategyResult(
                StrategyOutcome.SUCCESS,
                bibtex="""@article{demo,\n    author = {Doe, Jane},\n    title = {Sample Title},\n    journal = {Test Journal},\n    year = {2024},\n}\n""",
                metadata={"author": "Doe, Jane", "year": "2024"},
            )

    monkeypatch.setattr(pipeline_module, "STRATEGIES", [SuccessfulStrategy()])
    monkeypatch.setattr(CitationPipeline, "_read_pdf_text", lambda self, path: "SAMPLE TITLE\n2024")

    pipeline = CitationPipeline(config, interactions=AcceptAllInteractions())
    assert pipeline.process_pdf(pdf_path) is True

    bib_content = config.output_bib.read_text(encoding="utf-8")
    assert "@article{demo" in bib_content
    renamed_pdf = config.references_dir / "Doe2024.pdf"
    assert renamed_pdf.exists()
    run_log_entries = [json.loads(line) for line in config.run_log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert run_log_entries[-1]["status"] == "accepted"
    assert run_log_entries[-1]["strategy"] == "success"


def test_pipeline_rejects_when_strategies_fail(tmp_path, monkeypatch):
    config = make_config(tmp_path)
    pdf_path = config.references_dir / "paper.pdf"
    pdf_path.write_text("dummy", encoding="utf-8")

    class FailingStrategy:
        name = "fail"

        def applicable(self, ctx, cfg):
            return True

        def execute(self, ctx, cfg, interactions):
            return StrategyResult(StrategyOutcome.FAILED, message="no match")

    monkeypatch.setattr(pipeline_module, "STRATEGIES", [FailingStrategy()])
    monkeypatch.setattr(CitationPipeline, "_read_pdf_text", lambda self, path: "SAMPLE TITLE\n2024")

    pipeline = CitationPipeline(config, interactions=AcceptAllInteractions())
    assert pipeline.process_pdf(pdf_path) is False

    rejected_dir = config.rejected_dir
    moved_files = list(rejected_dir.glob("*.pdf"))
    assert len(moved_files) == 1
    log_text = config.rejected_log.read_text(encoding="utf-8")
    assert "All strategies exhausted" in log_text or "no match" in log_text
    run_log_entries = [json.loads(line) for line in config.run_log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert run_log_entries[-1]["status"] == "rejected"
