from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


class InteractionProvider:
    def prompt(self, message: str, default: str = "") -> str:
        raise NotImplementedError

    def confirm(self, message: str, default_yes: bool = True) -> bool:
        raise NotImplementedError


@dataclass
class CLIInteractionProvider(InteractionProvider):
    interactive: bool = True

    def prompt(self, message: str, default: str = "") -> str:
        if not self.interactive:
            return default
        suffix = f" [{default}]" if default else ""
        try:
            value = input(f"{message}{suffix}: ").strip()
        except EOFError:
            value = ""
        return value or default

    def confirm(self, message: str, default_yes: bool = True) -> bool:
        if not self.interactive:
            return default_yes
        prompt_token = "Y/n" if default_yes else "y/N"
        try:
            value = input(f"{message} [{prompt_token}]: ").strip().lower()
        except EOFError:
            value = ""
        if not value:
            return default_yes
        if value in {"y", "yes"}:
            return True
        if value in {"n", "no"}:
            return False
        return default_yes


class NonInteractiveProvider(InteractionProvider):
    def prompt(self, message: str, default: str = "") -> str:  # pragma: no cover - simple passthrough
        return default

    def confirm(self, message: str, default_yes: bool = True) -> bool:  # pragma: no cover
        return default_yes


def provider_for_mode(interactive: bool) -> InteractionProvider:
    return CLIInteractionProvider(interactive=interactive) if interactive else NonInteractiveProvider()
