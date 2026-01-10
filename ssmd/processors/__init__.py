"""SSMD processors for converting markdown syntax to SSML."""

from typing import Any


def get_all_processors(config: dict[str, Any]) -> list:
    """Get all processors in the correct order.

    Args:
        config: Configuration dictionary

    Returns:
        List of processor instances in processing order
    """
    from ssmd.processors.emphasis import EmphasisProcessor
    from ssmd.processors.annotation import AnnotationProcessor
    from ssmd.processors.mark import MarkProcessor
    from ssmd.processors.prosody import ProsodyProcessor
    from ssmd.processors.heading import HeadingProcessor
    from ssmd.processors.paragraph import ParagraphProcessor
    from ssmd.processors.sentence import SentenceProcessor
    from ssmd.processors.break_processor import BreakProcessor

    # Order matters! Process in this sequence
    return [
        EmphasisProcessor(config),
        AnnotationProcessor(config),
        MarkProcessor(config),
        ProsodyProcessor(config),
        HeadingProcessor(config),
        ParagraphProcessor(config),
        SentenceProcessor(config),
        BreakProcessor(config),
    ]


__all__ = ["get_all_processors"]
