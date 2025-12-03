from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from citations import CitationPipeline, load_config


def test_load_config_defaults(tmp_path: Path) -> None:
    refs = tmp_path / "refs"
    refs.mkdir()
    bib = refs / "references.bib"
    bib.write_text("", encoding="utf-8")
    config = load_config(references_dir=refs, output_bib=bib, skip_doi=True, interactive=False)
    assert config.references_dir == refs
    assert config.output_bib == bib
    pipeline = CitationPipeline(config)
    assert pipeline.config.skip_doi is True
