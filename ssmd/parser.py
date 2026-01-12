"""SSMD parser for extracting structured data from SSMD text.

This module provides functions to parse SSMD markup into structured data
(segments and sentences) without converting to SSML. This allows TTS engines
to handle SSMD features programmatically.
"""

import logging
import re
from typing import TYPE_CHECKING

from ssmd.parser_types import (
    AudioAttrs,
    BreakAttrs,
    PhonemeAttrs,
    ProsodyAttrs,
    SayAsAttrs,
    SSMDSegment,
    SSMDSentence,
    VoiceAttrs,
)

if TYPE_CHECKING:
    from ssmd.capabilities import TTSCapabilities

logger = logging.getLogger(__name__)


def parse_voice_blocks(ssmd_text: str) -> list[tuple[VoiceAttrs | None, str]]:
    """Parse SSMD text into voice blocks.

    Splits text at @voice: directives and extracts voice parameters.

    Args:
        ssmd_text: SSMD markdown text

    Returns:
        List of (voice_attrs, text_content) tuples

    Example:
        >>> for voice, text in parse_voice_blocks(script):
        ...     print(f"Voice: {voice}, Text: {text}")
    """
    # Pattern to match @voice: directives
    # Matches: @voice: name or @voice: lang, gender: X, variant: Y
    voice_pattern = re.compile(
        r"^@voice(?::\s*|\()"
        r"([a-zA-Z0-9_-]+(?:\s*,\s*(?:gender|variant):\s*[a-zA-Z0-9]+)*)"
        r"\)?\s*\n",
        re.MULTILINE,
    )

    blocks: list[tuple[VoiceAttrs | None, str]] = []
    last_end = 0
    current_voice: VoiceAttrs | None = None

    for match in voice_pattern.finditer(ssmd_text):
        # Extract text before this voice directive
        text_before = ssmd_text[last_end : match.start()].strip()
        if text_before:
            blocks.append((current_voice, text_before))

        # Parse voice parameters
        params_str = match.group(1)
        current_voice = _parse_voice_params(params_str)

        last_end = match.end()

    # Extract remaining text after last voice directive
    text_after = ssmd_text[last_end:].strip()
    if text_after:
        blocks.append((current_voice, text_after))

    # If no voice directives found, return entire text with None voice
    if not blocks and ssmd_text.strip():
        blocks.append((None, ssmd_text.strip()))

    return blocks


def _parse_voice_params(params_str: str) -> VoiceAttrs:
    """Parse voice parameters from directive string.

    Args:
        params_str: Parameter string like "sarah" or "fr-FR, gender: female"

    Returns:
        VoiceAttrs object
    """
    voice = VoiceAttrs()

    # Check for gender or variant attributes
    has_gender = "gender:" in params_str
    has_variant = "variant:" in params_str

    # Extract the first parameter (voice name or language)
    voice_match = re.match(r"([a-zA-Z0-9_-]+)", params_str)
    if voice_match:
        voice_value = voice_match.group(1)

        # If gender/variant specified, or if it looks like a language code,
        # treat as language
        if (
            has_gender
            or has_variant
            or re.match(r"^[a-z]{2}(-[A-Z]{2})?$", voice_value)
        ):
            voice.language = voice_value
        else:
            # Otherwise it's a voice name
            voice.name = voice_value

    # Parse gender if present
    gender_match = re.search(r"gender:\s*([a-zA-Z]+)", params_str)
    if gender_match:
        gender_value = gender_match.group(1).lower()
        if gender_value in ("male", "female", "neutral"):
            voice.gender = gender_value  # type: ignore

    # Parse variant if present
    variant_match = re.search(r"variant:\s*(\d+)", params_str)
    if variant_match:
        voice.variant = int(variant_match.group(1))

    return voice


def parse_segments(
    ssmd_text: str,
    *,
    capabilities: "TTSCapabilities | str | None" = None,
    voice_context: VoiceAttrs | None = None,
) -> list[SSMDSegment]:
    """Parse SSMD text into flat list of segments.

    This is a lower-level function that doesn't group segments into sentences.
    Use parse_sentences() for most use cases.

    Args:
        ssmd_text: SSMD markdown text
        capabilities: TTS engine capabilities (filters unsupported features)
        voice_context: Voice context inherited from parent block

    Returns:
        List of SSMDSegment objects

    Example:
        >>> segments = parse_segments("Hello *world*!")
        >>> for seg in segments:
        ...     print(f"{seg.text} (emphasis={seg.emphasis})")
    """
    from ssmd.capabilities import get_preset

    # Resolve capabilities if string preset provided
    caps = None
    if isinstance(capabilities, str):
        caps = get_preset(capabilities)
    elif capabilities is not None:
        caps = capabilities

    # Strategy: Use existing SSMD → SSML conversion, then extract features
    # from the intermediate representation
    # This reuses all existing processors and ensures consistency

    # For the initial implementation, we'll use a simpler approach:
    # Extract features using regex patterns similar to the processors

    segments = []
    text = ssmd_text
    position = 0

    # Process inline voice annotations first (they create segment boundaries)
    voice_pattern = re.compile(r"\[([^\]]+)\]\(voice:\s*([^)]+)\)")
    for match in voice_pattern.finditer(text):
        # Text before this voice annotation
        before_text = text[position : match.start()]
        if before_text.strip():
            # Parse the text before voice change
            pre_segments = _parse_text_segments(before_text, caps)
            segments.extend(pre_segments)

        # Voice annotation segment
        voice_text = match.group(1)
        voice_params = match.group(2)
        voice_attrs = _parse_voice_params(voice_params)

        # Create segment with voice annotation
        seg = SSMDSegment(
            text=voice_text,
            voice=voice_attrs,
            position=match.start(),
        )
        segments.append(seg)

        position = match.end()

    # Process remaining text
    remaining = text[position:]
    if remaining.strip():
        remaining_segments = _parse_text_segments(remaining, caps)
        segments.extend(remaining_segments)

    # If no segments created, create a simple text segment
    if not segments and text.strip():
        segments.append(SSMDSegment(text=text.strip(), position=0))

    return segments


def _parse_text_segments(  # noqa: C901
    text: str,
    capabilities: "TTSCapabilities | None" = None,
) -> list[SSMDSegment]:
    """Parse text segment extracting all SSMD features.

    This function splits text into segments at markup boundaries, ensuring
    that emphasis, annotations, breaks, etc. are properly separated.

    A segment is a part of a sentence with consistent styling/attributes.
    For example, "*Hello* world" has two segments: "Hello" (emphasized) and
    "world" (plain text).

    Args:
        text: Text to parse
        capabilities: TTS capabilities for filtering

    Returns:
        List of SSMDSegment objects
    """
    segments = []
    position = 0

    # Patterns for different markup types
    strong_emphasis_pattern = re.compile(r"\*\*([^\*]+)\*\*")
    emphasis_pattern = re.compile(r"\*([^\*]+)\*")
    reduced_emphasis_pattern = re.compile(r"_([^_]+)_")
    annotation_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    # Combined pattern to find ALL markup boundaries  # noqa: C901
    # This matches: emphasis, annotations, breaks, marks
    # Order matters: match ** before *
    combined_pattern = re.compile(
        r"("
        r"\*\*[^\*]+\*\*"  # Strong emphasis (must come before single *)
        r"|\*[^\*]+\*"  # Regular emphasis
        r"|_[^_]+_"  # Reduced emphasis
        r"|\[[^\]]+\]\([^)]+\)"  # Annotations (including audio)
        r"|\.\.\.(?:\d+(?:s|ms)|[nwcsp])"  # Breaks
        r"|@(?!voice[:(])\w+"  # Marks
        r")"
    )

    # Split text into markup and non-markup parts
    current_pos = 0
    pending_breaks = []
    pending_marks_before = []

    for match in combined_pattern.finditer(text):
        # Get any plain text before this markup
        if match.start() > current_pos:
            plain_text = text[current_pos : match.start()]
            # Normalize: strip leading and trailing spaces
            # Also remove space before punctuation
            plain_text = plain_text.strip()
            # Remove space before punctuation
            plain_text = re.sub(r"\s+([.!?,;:])", r"\1", plain_text)
            if plain_text:
                seg = SSMDSegment(text=plain_text, position=position)
                if pending_breaks:
                    seg.breaks_before.extend(pending_breaks)
                    pending_breaks = []
                if pending_marks_before:
                    seg.marks_before = pending_marks_before
                    pending_marks_before = []
                segments.append(seg)
                position += len(plain_text)

        # Process the markup
        markup = match.group(0)

        # Check what type of markup this is
        if markup.startswith("..."):
            # This is a break
            break_val = markup[3:]
            break_attr = _parse_break(break_val)
            if segments:
                # Add to last segment
                segments[-1].breaks_after.append(break_attr)
            else:
                # Break before any segment
                pending_breaks.append(break_attr)

        elif markup.startswith("@"):
            # This is a mark
            mark_name = markup[1:]

            if segments:
                # Add mark after last segment
                segments[-1].marks_after.append(mark_name)
            else:
                # Mark before any text - will be added to next segment
                pending_marks_before.append(mark_name)

        elif markup.startswith("**"):
            # Strong emphasis
            strong_match = strong_emphasis_pattern.match(markup)
            if strong_match:
                emph_text = strong_match.group(1)
                seg = SSMDSegment(text=emph_text, emphasis="strong", position=position)
                if pending_breaks:
                    seg.breaks_before.extend(pending_breaks)
                    pending_breaks = []
                if pending_marks_before:
                    seg.marks_before = pending_marks_before
                    pending_marks_before = []
                segments.append(seg)
                position += len(emph_text)

        elif markup.startswith("_"):
            # Reduced emphasis
            reduced_match = reduced_emphasis_pattern.match(markup)
            if reduced_match:
                emph_text = reduced_match.group(1)
                seg = SSMDSegment(text=emph_text, emphasis="reduced", position=position)
                if pending_breaks:
                    seg.breaks_before.extend(pending_breaks)
                    pending_breaks = []
                if pending_marks_before:
                    seg.marks_before = pending_marks_before
                    pending_marks_before = []
                segments.append(seg)
                position += len(emph_text)

        elif markup.startswith("*"):
            # Regular emphasis
            emph_match = emphasis_pattern.match(markup)
            if emph_match:
                emph_text = emph_match.group(1)
                seg = SSMDSegment(text=emph_text, emphasis=True, position=position)
                if pending_breaks:
                    seg.breaks_before.extend(pending_breaks)
                    pending_breaks = []
                if pending_marks_before:
                    seg.marks_before = pending_marks_before
                    pending_marks_before = []
                segments.append(seg)
                position += len(emph_text)

        elif markup.startswith("["):
            # Annotation (including audio detected by URL pattern)
            ann_match = annotation_pattern.match(markup)
            if ann_match:
                ann_text = ann_match.group(1)
                ann_params = ann_match.group(2)
                seg = _parse_annotation_segment(ann_text, ann_params, position)
                if pending_breaks:
                    seg.breaks_before.extend(pending_breaks)
                    pending_breaks = []
                if pending_marks_before:
                    seg.marks_before = pending_marks_before
                    pending_marks_before = []
                segments.append(seg)
                position += len(ann_text)

        current_pos = match.end()

    # Handle any remaining text after last markup
    if current_pos < len(text):
        remaining_text = text[current_pos:].strip()
        # Remove space before punctuation
        remaining_text = re.sub(r"\s+([.!?,;:])", r"\1", remaining_text)
        if remaining_text:
            seg = SSMDSegment(text=remaining_text, position=position)
            if pending_breaks:
                seg.breaks_before.extend(pending_breaks)
                pending_breaks = []
            if pending_marks_before:
                seg.marks_before = pending_marks_before
                pending_marks_before = []
            segments.append(seg)

    # If no segments created, create simple text segment
    if not segments and text.strip():
        seg = SSMDSegment(text=text.strip(), position=0)
        if pending_breaks:
            seg.breaks_before.extend(pending_breaks)
        if pending_marks_before:
            seg.marks_before = pending_marks_before
        segments.append(seg)

    return segments


def _parse_annotation_segment(  # noqa: C901
    text: str, params: str, position: int
) -> SSMDSegment:
    """Parse annotation parameters and create segment.

    Args:
        text: Annotation text
        params: Annotation parameters
        position: Position in source text

    Returns:
        SSMDSegment with appropriate attributes set
    """
    seg = SSMDSegment(text=text, position=position)

    # Parse different annotation types
    if params.startswith("sub:"):
        # Substitution
        alias = params[4:].strip()
        seg.substitution = alias
    elif params.startswith("lang:"):
        # Language annotation
        lang_code = params[5:].strip()
        seg.language = lang_code
    elif params.startswith("say-as:"):
        # Say-as
        rest = params[7:].strip()
        parts = rest.split(",")
        interpret_as = parts[0].strip()
        format_val = None
        if len(parts) > 1 and "format:" in parts[1]:
            format_val = parts[1].split("format:")[1].strip().strip("\"'")
        seg.say_as = SayAsAttrs(interpret_as=interpret_as, format=format_val)
    elif params.startswith("as:"):
        # Say-as (short form)
        parts = params[3:].split(",")
        interpret_as = parts[0].strip()
        format_val = None
        if len(parts) > 1 and "format:" in parts[1]:
            format_val = parts[1].split("format:")[1].strip().strip("\"'")
        seg.say_as = SayAsAttrs(interpret_as=interpret_as, format=format_val)
    elif params.startswith("ph:") or params.startswith("ipa:"):
        # Phoneme
        rest = params.split(":", 1)[1].strip()

        # Parse phoneme and alphabet
        alphabet = "ipa" if params.startswith("ipa:") else "ipa"  # Default to ipa
        ph = rest

        # Check if alphabet is specified
        if ", alphabet:" in rest:
            parts = rest.split(", alphabet:")
            ph = parts[0].strip()
            alphabet = parts[1].strip()
        elif ",alphabet:" in rest:
            parts = rest.split(",alphabet:")
            ph = parts[0].strip()
            alphabet = parts[1].strip()

        seg.phoneme = PhonemeAttrs(ph=ph, alphabet=alphabet)
    elif (
        params.startswith("rate:")
        or params.startswith("pitch:")
        or params.startswith("volume:")
    ):
        # Prosody with explicit parameter names
        seg.prosody = _parse_prosody_annotation(params)
    elif (
        params.startswith("v:")
        or params.startswith("r:")
        or params.startswith("p:")
        or params.startswith("vrp:")
    ):
        # Prosody (short form)
        seg.prosody = _parse_prosody_annotation(params)
    elif params.startswith("ext:"):
        # Extension
        ext_name = params[4:].strip()
        seg.extension = ext_name
    elif params.startswith("voice:"):
        # Voice annotation: [text](voice: name)
        # or [text](voice: lang, gender: X, variant: Y)
        voice_params = params[6:].strip()
        seg.voice = _parse_voice_annotation(voice_params)
    elif re.match(r"^[a-z]{2}(-[A-Z]{2})?$", params):
        # Language code (standalone, without "lang:" prefix)
        seg.language = params
    elif (
        params.startswith("http://")
        or params.startswith("https://")
        or params.startswith("file://")
        or (
            "." in params
            and any(
                params.split()[0].endswith(ext)
                for ext in [".mp3", ".ogg", ".wav", ".m4a", ".flac"]
            )
        )
    ):
        # Audio file: [text](url.mp3) or [text](url.mp3 alt)
        # or [text](url.mp3 attrs alt)
        # Parse URL and optional attributes
        parts = params.split()
        url = parts[0] if parts else params

        # Check for 'alt' marker (indicates alt text in description)
        has_alt_marker = "alt" in parts[1:] if len(parts) > 1 else False

        # Parse additional attributes (clip, speed, repeat, level)
        attrs = {}
        i = 1
        while i < len(parts):
            part = parts[i]
            if part == "alt":
                # Skip the 'alt' marker
                i += 1
                continue
            elif ":" in part:
                # Parse attribute (e.g., "clip: 0s-5s", "speed: 150%")
                key_val = part.split(":", 1)
                if len(key_val) == 2:
                    key = key_val[0].strip()
                    val = key_val[1].strip()
                    # Handle multi-word values
                    if i + 1 < len(parts) and ":" not in parts[i + 1]:
                        val += " " + parts[i + 1]
                        i += 1
                    attrs[key] = val
            i += 1

        # Create AudioAttrs
        audio_attrs = AudioAttrs(src=url)
        if has_alt_marker:
            audio_attrs.alt_text = "alt"  # Marker that alt text is in description

        # Set additional attributes if present
        if "clip" in attrs:
            clip_range = attrs["clip"].split("-")
            if len(clip_range) == 2:
                audio_attrs.clip_begin = clip_range[0].strip()
                audio_attrs.clip_end = clip_range[1].strip()
        if "speed" in attrs:
            audio_attrs.speed = attrs["speed"]
        if "repeat" in attrs:
            try:
                audio_attrs.repeat_count = int(attrs["repeat"])
            except ValueError:
                pass
        if "repeatDur" in attrs:
            audio_attrs.repeat_dur = attrs["repeatDur"]
        if "level" in attrs:
            audio_attrs.sound_level = attrs["level"]

        seg.audio = audio_attrs

    return seg


def _parse_audio_segment(text: str, params: str, position: int) -> SSMDSegment:
    """Parse audio annotation parameters and create segment.

    Args:
        text: Audio description text
        params: Audio parameters (e.g., "sound.mp3" or "sound.mp3 alt")
        position: Position in source text

    Returns:
        SSMDSegment with audio attribute set
    """
    seg = SSMDSegment(text=text, position=position)

    # Parse URL and optional attributes
    parts = params.split()
    url = parts[0] if parts else params

    # Check for 'alt' marker (indicates alt text in description)
    has_alt_marker = "alt" in parts[1:] if len(parts) > 1 else False

    # Parse additional attributes (clip, speed, repeat, level)
    attrs = {}
    i = 1
    while i < len(parts):
        part = parts[i]
        if part == "alt":
            # Skip the 'alt' marker
            i += 1
            continue
        elif ":" in part:
            # Parse attribute (e.g., "clip: 0s-5s", "speed: 150%")
            key_val = part.split(":", 1)
            if len(key_val) == 2:
                key = key_val[0].strip()
                val = key_val[1].strip()
                # Handle multi-word values
                if i + 1 < len(parts) and ":" not in parts[i + 1]:
                    val += " " + parts[i + 1]
                    i += 1
                attrs[key] = val
        i += 1

    # Create AudioAttrs
    audio_attrs = AudioAttrs(src=url)
    if has_alt_marker:
        audio_attrs.alt_text = "alt"  # Marker that alt text is in description

    # Set additional attributes if present
    if "clip" in attrs:
        clip_range = attrs["clip"].split("-")
        if len(clip_range) == 2:
            audio_attrs.clip_begin = clip_range[0].strip()
            audio_attrs.clip_end = clip_range[1].strip()
    if "speed" in attrs:
        audio_attrs.speed = attrs["speed"]
    if "repeat" in attrs:
        try:
            audio_attrs.repeat_count = int(attrs["repeat"])
        except ValueError:
            pass
    if "repeatDur" in attrs:
        audio_attrs.repeat_dur = attrs["repeatDur"]
    if "level" in attrs:
        audio_attrs.sound_level = attrs["level"]

    seg.audio = audio_attrs
    return seg


def _parse_prosody_annotation(params: str) -> ProsodyAttrs:
    """Parse prosody annotation parameters.

    Args:
        params: Prosody parameters (e.g., "v: 5", "vrp: 555")

    Returns:
        ProsodyAttrs object
    """
    prosody = ProsodyAttrs()

    # VRP shorthand
    if params.startswith("vrp:"):
        vrp = params[4:].strip()
        volume_map = {
            "0": "silent",
            "1": "x-soft",
            "2": "soft",
            "3": "medium",
            "4": "loud",
            "5": "x-loud",
        }
        rate_map = {
            "1": "x-slow",
            "2": "slow",
            "3": "medium",
            "4": "fast",
            "5": "x-fast",
        }
        pitch_map = {
            "1": "x-low",
            "2": "low",
            "3": "medium",
            "4": "high",
            "5": "x-high",
        }

        if len(vrp) >= 1:
            prosody.volume = volume_map.get(vrp[0])
        if len(vrp) >= 2:
            prosody.rate = rate_map.get(vrp[1])
        if len(vrp) >= 3:
            prosody.pitch = pitch_map.get(vrp[2])
    else:
        # Individual parameters
        for part in params.split(","):
            part = part.strip()
            if ":" in part:
                key, value = part.split(":", 1)
                key = key.strip()
                value = value.strip()

                # Map numeric values or handle full names
                if key in ("v", "volume"):
                    if value.startswith(("+", "-")) or value.endswith(("dB", "%")):
                        prosody.volume = value
                    else:
                        volume_map = {
                            "0": "silent",
                            "1": "x-soft",
                            "2": "soft",
                            "3": "medium",
                            "4": "loud",
                            "5": "x-loud",
                        }
                        prosody.volume = volume_map.get(value, value)
                elif key in ("r", "rate"):
                    if value.startswith(("+", "-")) or value.endswith("%"):
                        prosody.rate = value
                    else:
                        rate_map = {
                            "1": "x-slow",
                            "2": "slow",
                            "3": "medium",
                            "4": "fast",
                            "5": "x-fast",
                        }
                        prosody.rate = rate_map.get(value, value)
                elif key in ("p", "pitch"):
                    if value.startswith(("+", "-")) or value.endswith("%"):
                        prosody.pitch = value
                    else:
                        pitch_map = {
                            "1": "x-low",
                            "2": "low",
                            "3": "medium",
                            "4": "high",
                            "5": "x-high",
                        }
                        prosody.pitch = pitch_map.get(value, value)

    return prosody


def _parse_voice_annotation(params: str) -> VoiceAttrs:
    """Parse voice annotation parameters.

    Args:
        params: Voice parameters
            (e.g., "Joanna", "en-US", "en-GB, gender: male, variant: 1")

    Returns:
        VoiceAttrs object
    """
    voice = VoiceAttrs()

    # Check if it's a simple name (no commas)
    if "," not in params:
        # Could be a name or just a language code
        # If it looks like a language code, set language; otherwise set name
        if re.match(r"^[a-z]{2}(-[A-Z]{2})?$", params.strip()):
            voice.language = params.strip()
        else:
            voice.name = params.strip()
    else:
        # Parse multiple parameters
        parts = params.split(",")
        for i, part in enumerate(parts):
            part = part.strip()

            if ":" in part:
                # Key-value parameter
                key, value = part.split(":", 1)
                key = key.strip()
                value = value.strip()

                if key == "gender":
                    voice.gender = value  # type: ignore
                elif key == "variant":
                    try:
                        voice.variant = int(value)
                    except ValueError:
                        pass
            elif i == 0:
                # First part without colon is the language or name
                if re.match(r"^[a-z]{2}(-[A-Z]{2})?$", part):
                    voice.language = part
                else:
                    voice.name = part

    return voice


def _parse_break(modifier: str) -> BreakAttrs:
    """Parse break modifier into BreakAttrs.

    Args:
        modifier: Break modifier (e.g., "500ms", "2s", "n", "w", "c", "s", "p")

    Returns:
        BreakAttrs object
    """
    if modifier == "n":
        return BreakAttrs(strength="none")
    elif modifier == "w":
        return BreakAttrs(strength="x-weak")
    elif modifier == "c":
        return BreakAttrs(strength="medium")
    elif modifier == "s":
        return BreakAttrs(strength="strong")
    elif modifier == "p":
        return BreakAttrs(strength="x-strong")
    elif modifier.endswith("s") or modifier.endswith("ms"):
        return BreakAttrs(time=modifier)
    else:
        # Number without unit = milliseconds
        return BreakAttrs(time=f"{modifier}ms")


def parse_sentences(
    ssmd_text: str,
    *,
    capabilities: "TTSCapabilities | str | None" = None,
    include_default_voice: bool = True,
    sentence_detection: bool = True,
    language: str = "en",
    model_size: str | None = None,
    spacy_model: str | None = None,
    use_spacy: bool | None = None,
) -> list[SSMDSentence]:
    """Parse SSMD text into sentences with segments.

    This is the main parser function. It splits text by voice changes and
    sentence boundaries, then extracts all SSMD features into structured segments.

    Args:
        ssmd_text: SSMD markdown text
        capabilities: TTS engine capabilities (auto-filters unsupported features)
        include_default_voice: If True, include text before first @voice: directive
        sentence_detection: If True, auto-split on sentence boundaries using phrasplit
        language: Language code for sentence detection (default: "en")
        model_size: spaCy model size: "sm", "md", "lg", "trf" (default: "sm")
        spacy_model: Custom spaCy model name (overrides model_size)
        use_spacy: If False, use fast regex splitting instead of spaCy (default: True)

    Returns:
        List of SSMDSentence objects

    Example:
        >>> # Default: uses small models (en_core_web_sm)
        >>> for sentence in parse_sentences(script):
        ...     full_text = "".join(seg.text for seg in sentence.segments)
        ...     tts.speak(full_text, voice=sentence.voice)
        >>>
        >>> # Fast mode: no spaCy required
        >>> sentences = parse_sentences(script, use_spacy=False)
        >>>
        >>> # High quality: use large model
        >>> sentences = parse_sentences(script, model_size="lg")
    """
    sentences = []

    # Step 1: Split into voice blocks
    voice_blocks = parse_voice_blocks(ssmd_text)

    if not include_default_voice:
        # Filter out blocks with no voice
        voice_blocks = [(v, t) for v, t in voice_blocks if v is not None]

    # Step 2: Process each voice block
    for voice, text in voice_blocks:
        # Determine language for sentence splitting
        # Use voice language if available, otherwise use default
        split_language = language
        if voice and voice.language:
            # Extract language code from BCP-47 (e.g., "en-US" -> "en")
            split_language = voice.language.split("-")[0]

        # Step 3: Split by sentence boundaries if enabled
        if sentence_detection:
            sentence_texts = _split_sentences(
                text,
                language=split_language,
                model_size=model_size,
                spacy_model=spacy_model,
                use_spacy=use_spacy,
            )
        else:
            sentence_texts = [text]

        # Step 4: Parse each sentence into segments
        for sent_text in sentence_texts:
            # Check for paragraph break
            is_para_end = sent_text.endswith("\n\n")
            sent_text_clean = sent_text.rstrip()

            if not sent_text_clean:
                continue

            # Parse segments
            segments = parse_segments(
                sent_text_clean,
                capabilities=capabilities,
                voice_context=voice,
            )

            # Create sentence
            sentence = SSMDSentence(
                voice=voice,
                segments=segments,
                is_paragraph_end=is_para_end,
            )
            sentences.append(sentence)

    return sentences


def _split_sentences(
    text: str,
    language: str = "en",
    model_size: str | None = None,
    spacy_model: str | None = None,
    use_spacy: bool | None = None,
) -> list[str]:
    """Split text into sentences using phrasplit.

    phrasplit handles all the complexity: spaCy detection, model loading,
    fallback to regex, error handling, and multi-language support.

    Args:
        text: Text to split
        language: Language code (e.g., "en", "fr", "de")
        model_size: spaCy model size ("sm", "md", "lg", "trf")
        spacy_model: Custom spaCy model name (overrides model_size/language)
        use_spacy: Force spaCy mode (True), regex mode (False), or auto-detect (None)

    Returns:
        List of sentence strings (preserving paragraph breaks)
    """
    from phrasplit import split_text

    # Determine language model name
    if spacy_model is not None:
        # Custom model name provided - use it directly
        language_model = spacy_model
    else:
        # Build model name from language + size
        # phrasplit will auto-detect if spaCy is available and fall back to regex
        size = model_size or "sm"
        # Extract 2-letter language code from BCP-47 locale (e.g., "en-US" -> "en")
        # spaCy models use simple 2-letter codes: en_core_web_sm, not en-US_core_web_sm
        lang_code = language.split("-")[0] if "-" in language else language

        # Language-specific model name patterns
        # Some languages use "news" instead of "web"
        if lang_code in (
            "fr",
            "ca",
            "da",
            "el",
            "hr",
            "it",
            "lt",
            "mk",
            "nb",
            "pl",
            "pt",
            "ro",
            "ru",
        ):
            language_model = f"{lang_code}_core_news_{size}"
        else:
            # Most languages use "web"
            language_model = f"{lang_code}_core_web_{size}"

    # phrasplit handles everything: spaCy detection, fallback, errors
    segments = split_text(
        text,
        mode="sentence",
        language_model=language_model,
        apply_corrections=True,
        split_on_colon=True,
        use_spacy=use_spacy,  # None = auto-detect, True = force, False = regex
    )

    # Convert phrasplit.Segment to sentence strings
    # Group by sentence, track paragraph boundaries
    sentences = []
    current_sentence = ""
    last_sentence_id = None
    last_paragraph_id = None

    for seg in segments:
        seg_text = seg.text.strip()
        if not seg_text:
            continue

        # Check if we've moved to a new sentence or paragraph
        sentence_changed = (
            last_sentence_id is not None and seg.sentence != last_sentence_id
        )
        paragraph_changed = (
            last_paragraph_id is not None and seg.paragraph != last_paragraph_id
        )

        if sentence_changed or paragraph_changed:
            # Finish previous sentence
            if current_sentence.strip():
                # Mark paragraph end if paragraph changed
                if paragraph_changed:
                    sentences.append(current_sentence + "\n\n")
                else:
                    sentences.append(current_sentence)
            current_sentence = ""

        current_sentence += seg_text

        last_sentence_id = seg.sentence
        last_paragraph_id = seg.paragraph

    # Add any remaining text
    if current_sentence.strip():
        sentences.append(current_sentence)

    return [s for s in sentences if s.strip()]
