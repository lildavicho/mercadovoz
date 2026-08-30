from __future__ import annotations

import re
from dataclasses import dataclass

from mercadovoz.numbers import strip_accents


MAX_INPUT_CHARS = 2_000
MAX_SEGMENTS = 20

_CONNECTOR = re.compile(
    r"(?i)\b(?:y|también|además|luego|después|entonces|aparte|más\s+tarde|de\s+ahí|por\s+otro\s+lado)\b"
)
_STRONG_BOUNDARY = re.compile(r"[;.!?]+|\r?\n+")
_COMMA = re.compile(r",")
_PREDICATE = re.compile(
    r"(?i)\b(?:vend(?:í|i|imos)|se\s+fueron|salieron|gast(?:é|e|amos)|compr(?:é|e|amos)|"
    r"fi(?:é|e|aron)|qued(?:ó|o)\s+debiendo|abon(?:ó|o|aron)|pag(?:ó|o|aron)|"
    r"me\s+pag(?:ó|o)|llev(?:ó|o|aron)|dej(?:ó|o|aron))\b"
)
_PREFIXED_PREDICATE = re.compile(
    r"(?i)^\s*(?:(?:hoy|ayer|después|luego|entonces)\s+)?"
    r"(?:(?:a\s+)?[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚáéíóúÑñ-]*(?:\s+[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚáéíóúÑñ-]*)?\s+)?"
    r"(?:me\s+)?(?:vend(?:í|i|imos)|gast(?:é|e|amos)|compr(?:é|e|amos)|fi(?:é|e|aron)|"
    r"qued(?:ó|o)\s+debiendo|abon(?:ó|o|aron)|pag(?:ó|o|aron)|llev(?:ó|o|aron)|dej(?:ó|o|aron))\b"
)
_SETTLEMENT_PREFIX = re.compile(r"(?i)\b(?:llev(?:ó|o)|compr(?:ó|o))\b")
_SETTLEMENT_SUFFIX = re.compile(r"(?i)^\s*(?:dej(?:ó|o)|pag(?:ó|o))\b")


@dataclass(frozen=True)
class NarrativeSegment:
    sequence: int
    start: int
    end: int
    text: str


def _trim_span(text: str, start: int, end: int) -> tuple[int, int] | None:
    while start < end and (text[start].isspace() or text[start] in ",;.!?"):
        start += 1
    while end > start and (text[end - 1].isspace() or text[end - 1] in ",;.!?"):
        end -= 1
    return (start, end) if start < end else None


def _starts_commercial_clause(value: str) -> bool:
    return bool(_PREFIXED_PREDICATE.search(value))


class CommercialNarrativeSegmenter:
    """Conservative clause scanner with exact source-span provenance."""

    version = "commercial-clause-v1"

    def __init__(self, *, max_chars: int = MAX_INPUT_CHARS, max_segments: int = MAX_SEGMENTS) -> None:
        self.max_chars = max_chars
        self.max_segments = max_segments

    def segment(self, text: str) -> list[NarrativeSegment]:
        if len(text) > self.max_chars:
            raise ValueError(f"maximum input length is {self.max_chars} characters")
        if not text.strip():
            return []

        cuts: set[int] = set()
        for match in _STRONG_BOUNDARY.finditer(text):
            cuts.add(match.end())

        for match in _COMMA.finditer(text):
            suffix = text[match.end() :]
            if _starts_commercial_clause(suffix):
                cuts.add(match.end())

        for match in _CONNECTOR.finditer(text):
            prefix = text[: match.start()]
            suffix_start = match.end()
            suffix = text[suffix_start:]
            if not _starts_commercial_clause(suffix):
                continue
            # "llevó/compró ... y dejó/pagó ..." is one settlement group.
            if _SETTLEMENT_PREFIX.search(prefix) and _SETTLEMENT_SUFFIX.search(suffix):
                continue
            cuts.add(suffix_start)

        spans: list[tuple[int, int]] = []
        cursor = 0
        for cut in sorted(cuts):
            trimmed = _trim_span(text, cursor, cut)
            if trimmed:
                spans.append(trimmed)
            cursor = cut
        trimmed = _trim_span(text, cursor, len(text))
        if trimmed:
            spans.append(trimmed)

        # A punctuation boundary followed by discourse text is not useful if no
        # commercial predicate exists in the new span; merge it back.
        merged: list[tuple[int, int]] = []
        for span in spans:
            segment_text = text[span[0] : span[1]]
            plain = strip_accents(segment_text.lower())
            if merged and not _PREDICATE.search(plain):
                merged[-1] = (merged[-1][0], span[1])
            else:
                merged.append(span)

        if len(merged) > self.max_segments:
            raise ValueError(f"maximum segment count is {self.max_segments}")
        return [
            NarrativeSegment(index, start, end, text[start:end])
            for index, (start, end) in enumerate(merged, start=1)
        ]
