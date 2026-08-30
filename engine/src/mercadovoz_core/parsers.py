from __future__ import annotations

from typing import Any, Protocol

from mercadovoz import parse_text

from .explicit_rules import parse_explicit_core


class Parser(Protocol):
    version: str

    def parse(self, text: str) -> dict[str, Any] | None: ...


class ExplicitCoreParser:
    version = "explicit-v0.4.0"

    def parse(self, text: str) -> dict[str, Any] | None:
        return parse_explicit_core(text)


class FrozenV0Parser:
    version = "rules-v0.1.0"

    def parse(self, text: str) -> dict[str, Any]:
        return parse_text(text)


class CompositeParser:
    version = "explicit-v0.4.0+rules-v0.1.0"

    def __init__(self, parsers: tuple[Parser, ...] | None = None) -> None:
        self.parsers = parsers or (ExplicitCoreParser(), FrozenV0Parser())

    def parse(self, text: str) -> dict[str, Any]:
        for parser in self.parsers:
            result = parser.parse(text)
            if result is not None:
                return result
        raise RuntimeError("parser chain returned no result")
