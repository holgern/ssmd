"""Data types for SSMD parser.

This module defines the data structures returned by the SSMD parser.
These types allow programmatic access to SSMD features without parsing SSML/XML.
"""

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class VoiceAttrs:
    """Voice attributes for TTS voice selection.

    Attributes:
        name: Voice name (e.g., "Joanna", "en-US-Wavenet-A")
        language: BCP-47 language code (e.g., "en-US", "fr-FR")
        gender: Voice gender
        variant: Variant number for disambiguation
    """

    name: str | None = None
    language: str | None = None
    gender: Literal["male", "female", "neutral"] | None = None
    variant: int | None = None


@dataclass
class ProsodyAttrs:
    """Prosody attributes for volume, rate, and pitch control.

    Attributes:
        volume: Volume level ('silent', 'x-soft', 'soft', 'medium', 'loud',
                'x-loud', or relative like '+10dB')
        rate: Speech rate ('x-slow', 'slow', 'medium', 'fast', 'x-fast',
              or relative like '+20%')
        pitch: Pitch level ('x-low', 'low', 'medium', 'high', 'x-high',
               or relative like '-5%')
    """

    volume: str | None = None
    rate: str | None = None
    pitch: str | None = None


@dataclass
class BreakAttrs:
    """Break/pause attributes.

    Attributes:
        time: Time duration (e.g., '500ms', '2s')
        strength: Break strength ('none', 'x-weak', 'medium', 'strong', 'x-strong')
    """

    time: str | None = None
    strength: str | None = None


@dataclass
class SayAsAttrs:
    """Say-as attributes for text interpretation.

    Attributes:
        interpret_as: Interpretation type ('telephone', 'date', 'cardinal',
                      'ordinal', 'characters', 'expletive', etc.)
        format: Optional format string (e.g., 'dd.mm.yyyy' for dates)
        detail: Optional detail level (e.g., '2' for verbosity)
    """

    interpret_as: str
    format: str | None = None
    detail: str | None = None


@dataclass
class AudioAttrs:
    """Audio file attributes.

    Attributes:
        src: Audio file URL or path
        alt_text: Fallback text if audio cannot be played
        clip_begin: Start time for playback (e.g., "0s", "500ms")
        clip_end: End time for playback (e.g., "10s", "5000ms")
        speed: Playback speed as percentage (e.g., "150%", "80%")
        repeat_count: Number of times to repeat audio
        repeat_dur: Total duration for repetitions (e.g., "10s")
        sound_level: Volume adjustment in dB (e.g., "+6dB", "-3dB")
    """

    src: str
    alt_text: str | None = None
    clip_begin: str | None = None
    clip_end: str | None = None
    speed: str | None = None
    repeat_count: int | None = None
    repeat_dur: str | None = None
    sound_level: str | None = None


@dataclass
class SSMDSegment:
    """A segment of text with SSMD features.

    Represents a portion of text with specific formatting and processing attributes.
    You process these segments to build the final sentence text for TTS.

    Attributes:
        text: Raw text content (before say-as/substitution/phoneme conversion)

        say_as: Say-as interpretation (you convert text using these rules)
        substitution: Replacement text (use this instead of text)
        phoneme: IPA pronunciation (use this instead of text if preferred)

        emphasis: True if text should be emphasized
        language: Language code for this segment
        prosody: Volume, rate, and pitch attributes

        audio: Audio file to play (text is description)
        extension: Platform-specific extension name (e.g., 'whisper')

        breaks_before: Pauses before this segment
        breaks_after: Pauses after this segment
        marks_before: Event markers before this segment
        marks_after: Event markers after this segment

        position: Character position in original SSMD text
    """

    # Raw text content
    text: str

    # Text transformation features (mutually exclusive - only one should be set)
    say_as: SayAsAttrs | None = None  # Convert using say-as rules
    substitution: str | None = None  # Replace text with alias
    phoneme: str | None = None  # IPA pronunciation

    # Styling features (can be combined)
    emphasis: bool = False
    language: str | None = None
    prosody: ProsodyAttrs | None = None

    # Audio (replaces text entirely)
    audio: AudioAttrs | None = None

    # Platform-specific
    extension: str | None = None

    # Breaks and marks
    breaks_before: list[BreakAttrs] = field(default_factory=list)
    breaks_after: list[BreakAttrs] = field(default_factory=list)
    marks_before: list[str] = field(default_factory=list)
    marks_after: list[str] = field(default_factory=list)

    # Metadata
    position: int = 0


@dataclass
class SSMDSentence:
    """A complete sentence with voice context and segments.

    Represents a logical sentence unit that should be spoken together.
    Sentences are split on:
    - Voice changes (@voice: directive or inline [](voice:))
    - Sentence boundaries (.!?) when sentence_detection=True
    - Paragraph breaks (\\n\\n)

    Attributes:
        voice: Voice context for entire sentence
        segments: List of segments to build the sentence
        breaks_after: Pauses after sentence ends
        is_paragraph_end: True if sentence ends with paragraph break
        position: Character position in original SSMD text
    """

    # Voice context for entire sentence
    voice: VoiceAttrs | None = None

    # List of segments to build the sentence
    segments: list[SSMDSegment] = field(default_factory=list)

    # Sentence-level breaks (after sentence ends)
    breaks_after: list[BreakAttrs] = field(default_factory=list)

    # Metadata
    is_paragraph_end: bool = False
    position: int = 0
