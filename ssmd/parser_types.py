"""Data types for SSMD parser.

This module provides backward compatibility by re-exporting types from
the new locations. New code should import directly from ssmd.types,
ssmd.segment, and ssmd.sentence.

Deprecated: This module is provided for backward compatibility.
Import from ssmd.types, ssmd.segment, and ssmd.sentence instead.
"""

# Re-export types from new locations for backward compatibility
from ssmd.segment import Segment
from ssmd.sentence import Sentence
from ssmd.types import (
    AudioAttrs,
    BreakAttrs,
    DirectiveAttrs,
    PhonemeAttrs,
    ProsodyAttrs,
    SayAsAttrs,
    VoiceAttrs,
)

# Backward compatibility aliases
SSMDSegment = Segment
SSMDSentence = Sentence

__all__ = [
    # Types
    "VoiceAttrs",
    "ProsodyAttrs",
    "BreakAttrs",
    "SayAsAttrs",
    "AudioAttrs",
    "PhonemeAttrs",
    "DirectiveAttrs",
    # Classes
    "Segment",
    "Sentence",
    # Backward compatibility aliases
    "SSMDSegment",
    "SSMDSentence",
]
