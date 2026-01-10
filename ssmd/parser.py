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
        _parse_voice_params(voice_params)  # Parsed but not used in segment extraction

        # This creates a sentence boundary, but for now we'll just mark it
        seg = SSMDSegment(
            text=voice_text,
            position=match.start(),
        )
        # Note: Voice changes mid-sentence will be handled by parse_sentences
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


def _parse_text_segments(
    text: str,
    capabilities: "TTSCapabilities | None" = None,
) -> list[SSMDSegment]:
    """Parse text segment extracting all SSMD features.

    This function extracts emphasis, prosody, annotations, breaks, marks, etc.

    Args:
        text: Text to parse
        capabilities: TTS capabilities for filtering

    Returns:
        List of SSMDSegment objects
    """
    # For initial implementation, create single segment with basic feature detection
    segments = []

    # Detect emphasis (*text*)
    emphasis_pattern = re.compile(r"\*([^\*]+)\*")
    # Detect breaks (...500ms, ...2s, ...n/w/c/s/p)
    break_pattern = re.compile(r"\.\.\.(\d+(?:s|ms)|[nwcsp])")
    # Detect marks (@marker)
    mark_pattern = re.compile(r"@(?!voice[:(])(\w+)")
    # Detect annotations [text](type: value)
    annotation_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    # Note: Prosody shorthand (++loud++, >>fast>>, etc.) is handled by the
    # main SSMD converter, not extracted as segments in the parser

    # For now, extract features but create simple segments
    # Full implementation would handle nesting and create multiple segments

    current_text = text
    position = 0

    # Extract breaks and create segments
    parts = break_pattern.split(current_text)
    for i, part in enumerate(parts):
        if i % 2 == 0:
            # Text part
            if part.strip():
                seg = SSMDSegment(text=part.strip(), position=position)

                # Check for emphasis
                if emphasis_pattern.search(part):
                    seg.emphasis = True
                    # Remove emphasis markers for plain text
                    seg.text = emphasis_pattern.sub(r"\1", seg.text)

                # Check for marks
                mark_matches = list(mark_pattern.finditer(part))
                if mark_matches:
                    seg.marks_before = [m.group(1) for m in mark_matches]
                    # Remove marks from text
                    seg.text = mark_pattern.sub("", seg.text).strip()

                # Check for annotations
                ann_match = annotation_pattern.search(part)
                if ann_match:
                    ann_text = ann_match.group(1)
                    ann_params = ann_match.group(2)

                    # Parse annotation type
                    seg = _parse_annotation_segment(ann_text, ann_params, position)

                if seg.text:  # Only add if has text
                    segments.append(seg)
                position += len(part)
        else:
            # Break modifier
            if i > 0 and segments:
                # Add break to previous segment
                break_attr = _parse_break(part)
                segments[-1].breaks_after.append(break_attr)

    # If no segments created, create simple text segment
    if not segments and text.strip():
        segments.append(SSMDSegment(text=text.strip(), position=0))

    return segments


def _parse_annotation_segment(text: str, params: str, position: int) -> SSMDSegment:
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
    elif params.startswith("as:"):
        # Say-as
        parts = params[3:].split(",")
        interpret_as = parts[0].strip()
        format_val = None
        if len(parts) > 1 and "format:" in parts[1]:
            format_val = parts[1].split("format:")[1].strip().strip("\"'")
        seg.say_as = SayAsAttrs(interpret_as=interpret_as, format=format_val)
    elif params.startswith("ph:") or params.startswith("ipa:"):
        # Phoneme
        is_xsampa = params.startswith("ph:")
        phoneme_text = params.split(":", 1)[1].strip()
        if is_xsampa:
            # Would need X-SAMPA to IPA conversion
            # For now, store as-is
            seg.phoneme = phoneme_text
        else:
            seg.phoneme = phoneme_text
    elif (
        params.startswith("v:")
        or params.startswith("r:")
        or params.startswith("p:")
        or params.startswith("vrp:")
    ):
        # Prosody
        seg.prosody = _parse_prosody_annotation(params)
    elif params.startswith("ext:"):
        # Extension
        ext_name = params[4:].strip()
        seg.extension = ext_name
    elif re.match(r"^[a-z]{2}(-[A-Z]{2})?$", params):
        # Language code
        seg.language = params
    elif (
        params.startswith("http://")
        or params.startswith("https://")
        or "." in params
        and params.split(".")[-1] in ["mp3", "ogg", "wav"]
    ):
        # Audio file
        parts = params.split(None, 1)
        url = parts[0]
        alt_text = parts[1] if len(parts) > 1 else None
        seg.audio = AudioAttrs(src=url, alt_text=alt_text)

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

                # Map numeric values
                if key == "v":
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
                elif key == "r":
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
                elif key == "p":
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

    Returns:
        List of SSMDSentence objects

    Example:
        >>> for sentence in parse_sentences(script):
        ...     full_text = "".join(seg.text for seg in sentence.segments)
        ...     tts.speak(full_text, voice=sentence.voice)
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
            sentence_texts = _split_sentences(text, language=split_language)
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
    use_phrasplit: bool = True,
) -> list[str]:
    """Split text into sentences using phrasplit or fallback regex.

    Args:
        text: Text to split
        language: Language code for phrasplit
        use_phrasplit: If True, use phrasplit for accurate splitting

    Returns:
        List of sentence strings (preserving paragraph breaks)
    """
    language_model = None
    if language.startswith("en"):
        language_model = "en_core_web_sm"
    elif language.startswith("fr"):
        language_model = "fr_core_news_sm"
    elif language.startswith("de"):
        language_model = "de_core_news_sm"
    elif language.startswith("es"):
        language_model = "es_core_news_sm"
    elif language.startswith("it"):
        language_model = "it_core_news_sm"
    elif language.startswith("pt"):
        language_model = "pt_core_news_sm"
    if use_phrasplit and language_model is not None:
        try:
            from phrasplit import split_text  # noqa: F401

            # Use phrasplit for accurate sentence detection
            segments = split_text(
                text,
                mode="sentence",  # Split by sentences
                language_model=language_model,
                apply_corrections=True,
                split_on_colon=True,
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

        except ImportError:
            logger.warning(
                "phrasplit not available, falling back to regex sentence splitting"
            )
        except Exception as e:
            logger.warning(f"phrasplit error: {e}, falling back to regex")

    # Fallback: Simple regex-based splitting
    # Split on .!? followed by whitespace or end of string
    # Keep the punctuation with the sentence
    pattern = re.compile(r"([.!?]+(?:\s+|$))")
    parts = pattern.split(text)

    sentences = []
    current = ""

    for part in parts:
        current += part
        if pattern.match(part):
            # This part is a sentence ending
            sentences.append(current)
            current = ""

    # Add any remaining text
    if current.strip():
        sentences.append(current)

    return [s for s in sentences if s.strip()]
