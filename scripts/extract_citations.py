#!/usr/bin/env python3
"""Modular citation extraction CLI."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Optional

from citations import CitationPipeline, load_config
from citations.logging_utils import setup_logging


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract BibTeX from reference PDFs")
    parser.add_argument(
        "--references-dir",
        type=Path,
        default=Path("references"),
        help="Directory containing reference PDFs",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("references") / "references.bib",
        help="BibTeX file to append entries to",
    )
    parser.add_argument(
        "--skip-doi",
        action="store_true",
        help="Skip DOI lookups and jump straight to Scholar",
    )
    parser.add_argument(
        "--no-interactive",
        dest="interactive",
        action="store_false",
        help="Disable interactive prompts",
    )
    parser.add_argument(
        "--run-log",
        type=Path,
        default=None,
        help="Write a JSONL audit log to the given path",
    )
    parser.add_argument(
        "--terminal-log",
        type=Path,
        default=Path("references") / "citations.log",
        help="Copy terminal output to a searchable log file",
    )
    parser.set_defaults(interactive=True)
    return parser.parse_args(argv)


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = parse_args(argv)
    setup_logging(log_path=args.terminal_log)
    config = load_config(
        references_dir=args.references_dir,
        output_bib=args.output,
        skip_doi=args.skip_doi,
        interactive=args.interactive,
        run_log_path=args.run_log,
    )
    pipeline = CitationPipeline(config)
    accepted = pipeline.process_directory()
    print(f"\nCompleted processing. {accepted} citation(s) accepted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
