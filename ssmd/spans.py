"""Span data types for SSMD parsing."""

from dataclasses import dataclass, field


@dataclass
class AnnotationSpan:
    char_start: int
    char_end: int
    attrs: dict[str, str]
    kind: str | None = None
    node_id: str | None = None


@dataclass
class ParseSpansResult:
    clean_text: str
    annotations: list[AnnotationSpan] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


__all__ = ["AnnotationSpan", "ParseSpansResult"]
