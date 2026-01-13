"""SSMD parser - Parse SSMD text into structured Sentence/Segment objects.

This module provides functions to parse SSMD markdown into structured data
that can be used for TTS processing or conversion to SSML.
"""

import re
from typing import TYPE_CHECKING

from ssmd.segment import Segment
from ssmd.sentence import Sentence
from ssmd.types import (
    DEFAULT_HEADING_LEVELS,
    AudioAttrs,
    BreakAttrs,
    PhonemeAttrs,
    ProsodyAttrs,
    SayAsAttrs,
    VoiceAttrs,
)

if TYPE_CHECKING:
    from ssmd.capabilities import TTSCapabilities


# ═══════════════════════════════════════════════════════════════════════════════
# REGEX PATTERNS
# ═══════════════════════════════════════════════════════════════════════════════

# Voice directive: @voice: name or @voice(name)
# Supports: name, language code, gender:, variant:, language:
VOICE_DIRECTIVE_PATTERN = re.compile(
    r"^@voice(?::\s*|\()"
    r"([a-zA-Z0-9_-]+(?:\s*,\s*(?:gender|variant|language):\s*[a-zA-Z0-9_-]+)*)"
    r"\)?\s*$",
    re.MULTILINE,
)

# Emphasis patterns
STRONG_EMPHASIS_PATTERN = re.compile(r"\*\*([^\*]+)\*\*")
MODERATE_EMPHASIS_PATTERN = re.compile(r"\*([^\*]+)\*")
REDUCED_EMPHASIS_PATTERN = re.compile(r"(?<!_)_(?!_)([^_]+?)(?<!_)_(?!_)")

# Annotation pattern: [text](annotation)
ANNOTATION_PATTERN = re.compile(r"\[([^\]]*)\]\(([^\)]+)\)")

# Break pattern: ...500ms, ...2s, ...n, ...w, ...c, ...s, ...p
BREAK_PATTERN = re.compile(r"\.\.\.(\d+(?:s|ms)|[nwcsp])")

# Mark pattern: @name (but not @voice)
MARK_PATTERN = re.compile(r"@(?!voice[:(])(\w+)")

# Heading pattern: # ## ###
HEADING_PATTERN = re.compile(r"^\s*(#{1,6})\s*(.+)$", re.MULTILINE)

# Prosody shorthand patterns (applied after XML escaping, but we handle raw here)
PROSODY_VOLUME_PATTERN = re.compile(
    r"(?<![a-zA-Z0-9])"
    r"(~~|--|\+\+|-(?!-)|(?<!\+)\+|~)"  # Volume markers
    r"([^~\-+<>_^]+?)"
    r"\1"
    r"(?![a-zA-Z0-9])"
)

PROSODY_RATE_PATTERN = re.compile(
    r"(?<![a-zA-Z0-9])"
    r"(<<|<(?!<)|(?<!>)>|>>)"  # Rate markers
    r"([^<>]+?)"
    r"\1"
    r"(?![a-zA-Z0-9])"
)

PROSODY_PITCH_PATTERN = re.compile(
    r"(?<![a-zA-Z0-9_])"
    r"(__|\^\^|(?<!_)_(?!_)|(?<!\^)\^(?!\^))"  # Pitch markers
    r"([^_^]+?)"
    r"\1"
    r"(?![a-zA-Z0-9_])"
)

# Paragraph break: two or more newlines
PARAGRAPH_PATTERN = re.compile(r"\n\n+")

# Space before punctuation (to normalize)
SPACE_BEFORE_PUNCT = re.compile(r"\s+([.!?,:;])")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN PARSING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def _normalize_text(text: str) -> str:
    """Normalize text by removing extra whitespace and fixing spacing.

    - Removes space before punctuation
    - Collapses multiple spaces
    """
    text = SPACE_BEFORE_PUNCT.sub(r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_ssmd(
    text: str,
    *,
    capabilities: "TTSCapabilities | str | None" = None,
    heading_levels: dict | None = None,
    extensions: dict | None = None,
    sentence_detection: bool = True,
    language: str = "en",
    use_spacy: bool | None = None,
    model_size: str | None = None,
) -> list[Sentence]:
    """Parse SSMD text into a list of Sentences.

    This is the main parsing function. It handles:
    - Voice directives (@voice: name)
    - Paragraph and sentence splitting
    - All SSMD markup (emphasis, annotations, breaks, etc.)

    Args:
        text: SSMD markdown text
        capabilities: TTS capabilities for filtering (optional)
        heading_levels: Custom heading configurations
        extensions: Custom extension handlers
        sentence_detection: If True, split text into sentences
        language: Default language for sentence detection
        use_spacy: If True, use spaCy for sentence detection
        model_size: spaCy model size ("sm", "md", "lg")

    Returns:
        List of Sentence objects
    """
    if not text or not text.strip():
        return []

    # Resolve capabilities
    caps = _resolve_capabilities(capabilities)

    # Split text into voice blocks
    voice_blocks = _split_voice_blocks(text)

    sentences = []

    for voice, block_text in voice_blocks:
        # Split block into paragraphs
        paragraphs = PARAGRAPH_PATTERN.split(block_text)

        for para_idx, paragraph in enumerate(paragraphs):
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            is_last_paragraph = para_idx == len(paragraphs) - 1

            # Split paragraph into sentences if enabled
            if sentence_detection:
                sent_texts = _split_sentences(
                    paragraph,
                    language=language,
                    use_spacy=use_spacy,
                    model_size=model_size,
                )
            else:
                sent_texts = [paragraph]

            for sent_idx, sent_text in enumerate(sent_texts):
                sent_text = sent_text.strip()
                if not sent_text:
                    continue

                is_last_sent_in_para = sent_idx == len(sent_texts) - 1

                # Parse the sentence content into segments
                segments = _parse_segments(
                    sent_text,
                    capabilities=caps,
                    heading_levels=heading_levels,
                    extensions=extensions,
                )

                if segments:
                    sentence = Sentence(
                        segments=segments,
                        voice=voice,
                        is_paragraph_end=is_last_sent_in_para and not is_last_paragraph,
                    )
                    sentences.append(sentence)

    return sentences


def _resolve_capabilities(
    capabilities: "TTSCapabilities | str | None",
) -> "TTSCapabilities | None":
    """Resolve capabilities from string or object."""
    if capabilities is None:
        return None
    if isinstance(capabilities, str):
        from ssmd.capabilities import get_preset

        return get_preset(capabilities)
    return capabilities


def _split_voice_blocks(text: str) -> list[tuple[VoiceAttrs | None, str]]:
    """Split text into voice blocks.

    Args:
        text: SSMD text

    Returns:
        List of (voice, text) tuples
    """
    blocks: list[tuple[VoiceAttrs | None, str]] = []
    lines = text.split("\n")

    current_voice: VoiceAttrs | None = None
    current_lines: list[str] = []

    for line in lines:
        # Check if this line is a voice directive
        match = VOICE_DIRECTIVE_PATTERN.match(line)
        if match:
            # Save previous block if any
            if current_lines:
                block_text = "\n".join(current_lines)
                if block_text.strip():
                    blocks.append((current_voice, block_text))
                current_lines = []

            # Parse new voice
            params = match.group(1)
            current_voice = _parse_voice_params(params)
        else:
            current_lines.append(line)

    # Save final block
    if current_lines:
        block_text = "\n".join(current_lines)
        if block_text.strip():
            blocks.append((current_voice, block_text))

    # If no blocks, return entire text with no voice
    if not blocks and text.strip():
        blocks.append((None, text.strip()))

    return blocks


def _parse_voice_params(params: str) -> VoiceAttrs:
    """Parse voice parameters from directive string."""
    voice = VoiceAttrs()

    has_gender = "gender:" in params
    has_variant = "variant:" in params
    has_language = "language:" in params

    # Extract voice name or language code (first value before any comma)
    voice_match = re.match(r"([a-zA-Z0-9_-]+)", params)
    if voice_match:
        value = voice_match.group(1)
        # If explicit language: is provided, or gender/variant present
        # with language-like
        # first value, or looks like language code, treat first value as language
        if (has_gender or has_variant) and not has_language:
            # Pattern like "@voice: fr-FR, gender: female" - first value is language
            if re.match(r"^[a-z]{2}(-[A-Z]{2})?$", value):
                voice.language = value
            else:
                voice.name = value
        elif has_language:
            # Explicit language: provided, so first value is the name
            voice.name = value
        elif re.match(r"^[a-z]{2}(-[A-Z]{2})?$", value):
            # Looks like a language code
            voice.language = value
        else:
            # Just a name
            voice.name = value

    # Parse explicit language: parameter
    lang_match = re.search(r"language:\s*([a-zA-Z0-9_-]+)", params, re.IGNORECASE)
    if lang_match:
        voice.language = lang_match.group(1)

    # Parse gender
    gender_match = re.search(r"gender:\s*(male|female|neutral)", params, re.IGNORECASE)
    if gender_match:
        voice.gender = gender_match.group(1).lower()  # type: ignore

    # Parse variant
    variant_match = re.search(r"variant:\s*(\d+)", params)
    if variant_match:
        voice.variant = int(variant_match.group(1))

    return voice


def _split_sentences(
    text: str,
    language: str = "en",
    use_spacy: bool | None = None,
    model_size: str | None = None,
) -> list[str]:
    """Split text into sentences using phrasplit."""
    try:
        from phrasplit import split_text

        # Build model name
        size = model_size or "sm"
        lang_code = language.split("-")[0] if "-" in language else language

        # Language-specific model patterns
        web_langs = {
            "en",
            "zh",
        }
        if lang_code in web_langs:
            model = f"{lang_code}_core_web_{size}"
        else:
            model = f"{lang_code}_core_news_{size}"

        segments = split_text(
            text,
            mode="sentence",
            language_model=model,
            apply_corrections=True,
            split_on_colon=True,
            use_spacy=use_spacy,
        )

        # Group segments by sentence
        sentences = []
        current = ""
        last_sent_id = None

        for seg in segments:
            if last_sent_id is not None and seg.sentence != last_sent_id:
                if current.strip():
                    sentences.append(current)
                current = ""
            current += seg.text
            last_sent_id = seg.sentence

        if current.strip():
            sentences.append(current)

        return sentences if sentences else [text]

    except ImportError:
        # Fallback: simple sentence splitting
        return _simple_sentence_split(text)


def _simple_sentence_split(text: str) -> list[str]:
    """Simple regex-based sentence splitting."""
    # Split on sentence-ending punctuation followed by space or newline
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def _parse_segments(  # noqa: C901
    text: str,
    capabilities: "TTSCapabilities | None" = None,
    heading_levels: dict | None = None,
    extensions: dict | None = None,
) -> list[Segment]:
    """Parse text into segments with SSMD features."""
    # Check for heading
    heading_match = HEADING_PATTERN.match(text)
    if heading_match:
        return _parse_heading(heading_match, heading_levels or DEFAULT_HEADING_LEVELS)

    segments: list[Segment] = []
    position = 0

    # Build combined pattern for all markup
    # Order matters: longer patterns first
    combined = re.compile(
        r"("
        r"\*\*[^\*]+\*\*"  # **strong**
        r"|\*[^\*]+\*"  # *moderate*
        r"|(?<![_a-zA-Z0-9])_(?!_)[^_]+?(?<!_)_(?![_a-zA-Z0-9])"  # _reduced_
        r"|\[[^\]]*\]\([^\)]+\)"  # [text](annotation)
        r"|\.\.\.(?:\d+(?:s|ms)|[nwcsp])"  # breaks
        r"|@(?!voice[:(])\w+"  # marks
        r"|~~[^~]+~~"  # ~silent~
        r"|--[^-]+--"  # --x-soft--
        r"|\+\+[^+]+\+\+"  # ++x-loud++
        r"|(?<![a-zA-Z0-9+])\+[^+]+\+(?![a-zA-Z0-9+])"  # +loud+
        r"|(?<![a-zA-Z0-9-])-[^-]+-(?![a-zA-Z0-9-])"  # -soft-
        r"|<<[^<>]+<<"  # <<x-slow<<
        r"|(?<![<a-zA-Z0-9])<[^<>]+<(?![<a-zA-Z0-9])"  # <slow<
        r"|>>[^<>]+>>"  # >>x-fast>>
        r"|(?<![>a-zA-Z0-9])>[^<>]+>(?![>a-zA-Z0-9])"  # >fast>
        r"|__[^_]+__"  # __x-low__
        r"|\^\^[^^]+\^\^"  # ^^x-high^^
        r"|(?<![a-zA-Z0-9^])\^[^^]+\^(?![a-zA-Z0-9^])"  # ^high^
        r")"
    )

    pending_breaks: list[BreakAttrs] = []
    pending_marks: list[str] = []

    for match in combined.finditer(text):
        # Add plain text before this match
        if match.start() > position:
            plain = _normalize_text(text[position : match.start()])
            if plain:
                seg = Segment(text=plain)
                if pending_breaks:
                    seg.breaks_before = pending_breaks
                    pending_breaks = []
                if pending_marks:
                    seg.marks_before = pending_marks
                    pending_marks = []
                segments.append(seg)

        markup = match.group(0)

        # Determine markup type and create segment
        if markup.startswith("..."):
            # Break
            brk = _parse_break(markup[3:])
            if segments:
                segments[-1].breaks_after.append(brk)
            else:
                pending_breaks.append(brk)

        elif markup.startswith("@"):
            # Mark
            mark_name = markup[1:]
            if segments:
                segments[-1].marks_after.append(mark_name)
            else:
                pending_marks.append(mark_name)

        elif markup.startswith("**"):
            # Strong emphasis
            inner = STRONG_EMPHASIS_PATTERN.match(markup)
            if inner:
                seg = Segment(text=inner.group(1), emphasis="strong")
                _apply_pending(seg, pending_breaks, pending_marks)
                pending_breaks, pending_marks = [], []
                segments.append(seg)

        elif markup.startswith("*"):
            # Moderate emphasis
            inner = MODERATE_EMPHASIS_PATTERN.match(markup)
            if inner:
                seg = Segment(text=inner.group(1), emphasis=True)
                _apply_pending(seg, pending_breaks, pending_marks)
                pending_breaks, pending_marks = [], []
                segments.append(seg)

        elif markup.startswith("_") and not markup.startswith("__"):
            # Reduced emphasis (single underscore)
            inner = REDUCED_EMPHASIS_PATTERN.match(markup)
            if inner:
                seg = Segment(text=inner.group(1), emphasis="reduced")
                _apply_pending(seg, pending_breaks, pending_marks)
                pending_breaks, pending_marks = [], []
                segments.append(seg)

        elif markup.startswith("["):
            # Annotation
            annotation_seg = _parse_annotation(markup, extensions)
            if annotation_seg:
                _apply_pending(annotation_seg, pending_breaks, pending_marks)
                pending_breaks, pending_marks = [], []
                segments.append(annotation_seg)

        else:
            # Prosody shorthand
            prosody_seg = _parse_prosody_shorthand(markup)
            if prosody_seg:
                _apply_pending(prosody_seg, pending_breaks, pending_marks)
                pending_breaks, pending_marks = [], []
                segments.append(prosody_seg)

        position = match.end()

    # Add remaining text
    if position < len(text):
        plain = _normalize_text(text[position:])
        if plain:
            seg = Segment(text=plain)
            _apply_pending(seg, pending_breaks, pending_marks)
            segments.append(seg)

    # If no segments created but we have text, create a plain segment
    if not segments and text.strip():
        seg = Segment(text=text.strip())
        _apply_pending(seg, pending_breaks, pending_marks)
        segments.append(seg)

    return segments


def _apply_pending(
    seg: Segment,
    pending_breaks: list[BreakAttrs],
    pending_marks: list[str],
) -> None:
    """Apply pending breaks and marks to a segment."""
    if pending_breaks:
        seg.breaks_before = pending_breaks.copy()
    if pending_marks:
        seg.marks_before = pending_marks.copy()


def _parse_heading(
    match: re.Match,
    heading_levels: dict,
) -> list[Segment]:
    """Parse heading into segments."""
    level = len(match.group(1))
    text = match.group(2).strip()

    if level not in heading_levels:
        return [Segment(text=text)]

    # Build segment with heading effects
    seg = Segment(text=text)

    for effect_type, value in heading_levels[level]:
        if effect_type == "emphasis":
            seg.emphasis = value
        elif effect_type == "pause":
            seg.breaks_after.append(BreakAttrs(time=value))
        elif effect_type == "prosody" and isinstance(value, dict):
            seg.prosody = ProsodyAttrs(
                volume=value.get("volume"),
                rate=value.get("rate"),
                pitch=value.get("pitch"),
            )

    return [seg]


def _parse_break(modifier: str) -> BreakAttrs:
    """Parse break modifier into BreakAttrs."""
    strength_map = {
        "n": "none",
        "w": "x-weak",
        "c": "medium",
        "s": "strong",
        "p": "x-strong",
    }

    if modifier in strength_map:
        return BreakAttrs(strength=strength_map[modifier])
    elif modifier.endswith("s") or modifier.endswith("ms"):
        return BreakAttrs(time=modifier)
    else:
        return BreakAttrs(time=f"{modifier}ms")


def _parse_annotation(markup: str, extensions: dict | None = None) -> Segment | None:
    """Parse [text](annotation) markup."""
    match = ANNOTATION_PATTERN.match(markup)
    if not match:
        return None

    text = match.group(1)
    params = match.group(2).strip()

    seg = Segment(text=text)

    # Try to identify annotation type
    # Audio (URL or file extension)
    if _is_audio_annotation(params):
        seg.audio = _parse_audio_params(params)
        return seg

    # Extension: ext: name
    ext_match = re.match(r"^ext:\s*(\w+)$", params)
    if ext_match:
        seg.extension = ext_match.group(1)
        return seg

    # Voice: voice: name or voice: lang, gender: X
    if params.startswith("voice:"):
        seg.voice = _parse_voice_annotation(params[6:].strip())
        return seg

    # Say-as: as: type or say-as: type
    sayas_match = re.match(
        r"^(?:say-as|as):\s*(\w+)"
        r'(?:\s*,\s*format:\s*["\']?([^"\']+)["\']?)?'
        r"(?:\s*,\s*detail:\s*(\d+))?$",
        params,
    )
    if sayas_match:
        seg.say_as = SayAsAttrs(
            interpret_as=sayas_match.group(1),
            format=sayas_match.group(2),
            detail=sayas_match.group(3),
        )
        return seg

    # Phoneme: ph: or ipa: or sampa:
    # Stop at comma to allow combined annotations like "ph: value, alphabet: ipa"
    ph_match = re.match(r"^(ph|ipa|sampa):\s*([^,]+)", params)
    if ph_match:
        alphabet_type = ph_match.group(1)
        phonemes = ph_match.group(2).strip()

        # Map shorthand alphabet names
        if alphabet_type == "sampa":
            alphabet_type = "x-sampa"
        elif alphabet_type == "ph":
            # Default to ipa when using generic "ph:"
            alphabet_type = "ipa"

        # Check for explicit alphabet specification in remaining params
        remaining = params[ph_match.end() :].strip()
        if remaining.startswith(","):
            remaining = remaining[1:].strip()
            alph_match = re.match(r"^alphabet:\s*([^,]+)", remaining)
            if alph_match:
                specified_alphabet = alph_match.group(1).strip().lower()
                if specified_alphabet in ("ipa", "x-sampa", "sampa"):
                    # Normalize sampa to x-sampa
                    alphabet_type = (
                        "x-sampa"
                        if specified_alphabet == "sampa"
                        else specified_alphabet
                    )

        # Store phonemes as-is - conversion to IPA happens at SSML render time
        seg.phoneme = PhonemeAttrs(ph=phonemes, alphabet=alphabet_type)
        return seg

    # Substitution: sub: alias
    sub_match = re.match(r"^sub:\s*(.+)$", params)
    if sub_match:
        seg.substitution = sub_match.group(1).strip()
        return seg

    # Emphasis: emphasis: level
    emph_match = re.match(
        r"^emphasis:\s*(none|reduced|moderate|strong)$", params, re.IGNORECASE
    )
    if emph_match:
        level = emph_match.group(1).lower()
        seg.emphasis = level if level != "moderate" else True
        return seg

    # Prosody: vrp:, v:, r:, p:, volume:, rate:, pitch:
    if _is_prosody_annotation(params):
        seg.prosody = _parse_prosody_annotation(params)
        return seg

    # Language code: en, en-US, fr-FR, etc.
    lang_match = re.match(r"^(?:lang:\s*)?([a-z]{2}(?:-[A-Z]{2})?)$", params)
    if lang_match:
        seg.language = lang_match.group(1)
        return seg

    # Combined annotations (comma-separated)
    if "," in params:
        _parse_combined_annotations(seg, params, extensions)

    return seg


def _is_audio_annotation(params: str) -> bool:
    """Check if params represent an audio annotation."""
    audio_extensions = (".mp3", ".ogg", ".wav", ".m4a", ".aac", ".flac")
    first_part = params.split()[0] if params else ""
    return first_part.startswith(("http://", "https://", "file://")) or any(
        first_part.lower().endswith(ext) for ext in audio_extensions
    )


def _parse_audio_params(params: str) -> AudioAttrs:
    """Parse audio annotation parameters."""
    parts = params.split()
    url = parts[0]

    audio = AudioAttrs(src=url)

    remaining = " ".join(parts[1:]) if len(parts) > 1 else ""

    # Parse clip: start-end
    clip_match = re.search(
        r"clip:\s*(\d+(?:\.\d+)?[ms]+)-(\d+(?:\.\d+)?[ms]+)", remaining
    )
    if clip_match:
        audio.clip_begin = clip_match.group(1)
        audio.clip_end = clip_match.group(2)
        remaining = remaining[: clip_match.start()] + remaining[clip_match.end() :]

    # Parse speed: percent
    speed_match = re.search(r"speed:\s*(\d+(?:\.\d+)?%)", remaining)
    if speed_match:
        audio.speed = speed_match.group(1)
        remaining = remaining[: speed_match.start()] + remaining[speed_match.end() :]

    # Parse repeat: count
    repeat_match = re.search(r"repeat:\s*(\d+)", remaining)
    if repeat_match:
        audio.repeat_count = int(repeat_match.group(1))
        remaining = remaining[: repeat_match.start()] + remaining[repeat_match.end() :]

    # Parse level: dB
    level_match = re.search(r"level:\s*([+-]?\d+(?:\.\d+)?dB)", remaining)
    if level_match:
        audio.sound_level = level_match.group(1)
        remaining = remaining[: level_match.start()] + remaining[level_match.end() :]

    # Remaining text is alt text
    remaining = re.sub(r"[,\s]+", " ", remaining).strip()
    if remaining:
        audio.alt_text = remaining

    return audio


def _parse_voice_annotation(params: str) -> VoiceAttrs:
    """Parse voice annotation parameters."""
    voice = VoiceAttrs()

    # Check for complex params (with gender/variant)
    if "," in params:
        parts = [p.strip() for p in params.split(",")]
        first = parts[0]

        # First part is name or language
        if re.match(r"^[a-z]{2}(-[A-Z]{2})?$", first):
            voice.language = first
        else:
            voice.name = first

        # Parse remaining parts
        for part in parts[1:]:
            if part.startswith("gender:"):
                voice.gender = part[7:].strip().lower()  # type: ignore
            elif part.startswith("variant:"):
                voice.variant = int(part[8:].strip())
    else:
        # Simple name or language
        if re.match(r"^[a-z]{2}(-[A-Z]{2})?$", params):
            voice.language = params
        else:
            voice.name = params

    return voice


def _is_prosody_annotation(params: str) -> bool:
    """Check if params represent a prosody annotation."""
    return bool(re.match(r"^(?:vrp:|[vrp]:|volume:|rate:|pitch:)", params))


def _parse_prosody_annotation(params: str) -> ProsodyAttrs:
    """Parse prosody annotation parameters."""
    prosody = ProsodyAttrs()

    volume_map = {
        "0": "silent",
        "1": "x-soft",
        "2": "soft",
        "3": "medium",
        "4": "loud",
        "5": "x-loud",
    }
    rate_map = {"1": "x-slow", "2": "slow", "3": "medium", "4": "fast", "5": "x-fast"}
    pitch_map = {"1": "x-low", "2": "low", "3": "medium", "4": "high", "5": "x-high"}

    # VRP shorthand: vrp: 555
    vrp_match = re.match(r"^vrp:\s*(\d{1,3})$", params)
    if vrp_match:
        vrp = vrp_match.group(1)
        if len(vrp) >= 1:
            prosody.volume = volume_map.get(vrp[0])
        if len(vrp) >= 2:
            prosody.rate = rate_map.get(vrp[1])
        if len(vrp) >= 3:
            prosody.pitch = pitch_map.get(vrp[2])
        return prosody

    # Individual parameters
    for part in params.split(","):
        part = part.strip()
        if ":" not in part:
            continue

        key, value = part.split(":", 1)
        key = key.strip().lower()
        value = value.strip()

        # Normalize key names
        if key in ("v", "volume"):
            if value.startswith(("+", "-")) or value.endswith(("dB", "%")):
                prosody.volume = value
            else:
                prosody.volume = volume_map.get(value, value)
        elif key in ("r", "rate"):
            if value.endswith("%"):
                prosody.rate = value
            else:
                prosody.rate = rate_map.get(value, value)
        elif key in ("p", "pitch"):
            if value.startswith(("+", "-")) or value.endswith("%"):
                prosody.pitch = value
            else:
                prosody.pitch = pitch_map.get(value, value)

    return prosody


def _parse_prosody_shorthand(markup: str) -> Segment | None:
    """Parse prosody shorthand markup like ++loud++ or <<slow<<.

    Also handles nested emphasis inside prosody, e.g., +**WARNING**+
    """
    # Volume: ~~silent~~, --x-soft--, -soft-, +loud+, ++x-loud++
    # Order by length (longest first) to ensure ++ matches before +
    volume_patterns = [
        ("++", "x-loud"),
        ("~~", "silent"),
        ("--", "x-soft"),
        ("+", "loud"),
        ("-", "soft"),
    ]

    # Rate: <<x-slow<<, <slow<, >fast>, >>x-fast>>
    rate_patterns = [
        ("<<", "x-slow"),
        (">>", "x-fast"),
        ("<", "slow"),
        (">", "fast"),
    ]

    # Pitch: __x-low__, _low_ (single _ handled by emphasis), ^high^, ^^x-high^^
    pitch_patterns = [
        ("^^", "x-high"),
        ("__", "x-low"),
        ("^", "high"),
    ]

    # Try to match each pattern type
    for marker, value in volume_patterns:
        pattern = re.compile(rf"^{re.escape(marker)}(.+?){re.escape(marker)}$")
        match = pattern.match(markup)
        if match:
            inner_text = match.group(1)
            emphasis = _check_inner_emphasis(inner_text)
            if emphasis:
                return Segment(
                    text=emphasis[0],
                    emphasis=emphasis[1],
                    prosody=ProsodyAttrs(volume=value),
                )
            return Segment(text=inner_text, prosody=ProsodyAttrs(volume=value))

    for marker, value in rate_patterns:
        pattern = re.compile(rf"^{re.escape(marker)}(.+?){re.escape(marker)}$")
        match = pattern.match(markup)
        if match:
            inner_text = match.group(1)
            emphasis = _check_inner_emphasis(inner_text)
            if emphasis:
                return Segment(
                    text=emphasis[0],
                    emphasis=emphasis[1],
                    prosody=ProsodyAttrs(rate=value),
                )
            return Segment(text=inner_text, prosody=ProsodyAttrs(rate=value))

    for marker, value in pitch_patterns:
        pattern = re.compile(rf"^{re.escape(marker)}(.+?){re.escape(marker)}$")
        match = pattern.match(markup)
        if match:
            inner_text = match.group(1)
            emphasis = _check_inner_emphasis(inner_text)
            if emphasis:
                return Segment(
                    text=emphasis[0],
                    emphasis=emphasis[1],
                    prosody=ProsodyAttrs(pitch=value),
                )
            return Segment(text=inner_text, prosody=ProsodyAttrs(pitch=value))

    return None


def _check_inner_emphasis(text: str) -> tuple[str, str | bool] | None:
    """Check if text is wrapped in emphasis markers.

    Returns (inner_text, emphasis_level) or None if no emphasis found.
    """
    # Strong emphasis: **text**
    strong_match = STRONG_EMPHASIS_PATTERN.fullmatch(text)
    if strong_match:
        return (strong_match.group(1), "strong")

    # Moderate emphasis: *text*
    moderate_match = MODERATE_EMPHASIS_PATTERN.fullmatch(text)
    if moderate_match:
        return (moderate_match.group(1), True)

    # Reduced emphasis: _text_
    reduced_match = REDUCED_EMPHASIS_PATTERN.fullmatch(text)
    if reduced_match:
        return (reduced_match.group(1), "reduced")

    return None


def _parse_combined_annotations(
    seg: Segment,
    params: str,
    extensions: dict | None = None,
) -> None:
    """Parse combined comma-separated annotations."""
    # Split by comma, but be careful with quoted values
    parts = _smart_split(params, ",")

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Language code
        if re.match(r"^[a-z]{2}(-[A-Z]{2})?$", part):
            if not seg.language:
                seg.language = part
            continue

        # Prosody
        if re.match(r"^[vrp]:\s*", part) or re.match(r"^(volume|rate|pitch):", part):
            prosody = _parse_prosody_annotation(part)
            if seg.prosody:
                # Merge
                if prosody.volume and not seg.prosody.volume:
                    seg.prosody.volume = prosody.volume
                if prosody.rate and not seg.prosody.rate:
                    seg.prosody.rate = prosody.rate
                if prosody.pitch and not seg.prosody.pitch:
                    seg.prosody.pitch = prosody.pitch
            else:
                seg.prosody = prosody


def _smart_split(s: str, delimiter: str) -> list[str]:
    """Split string by delimiter, respecting quoted strings."""
    parts = []
    current = ""
    in_quotes = False
    quote_char = None

    for char in s:
        if char in ('"', "'") and not in_quotes:
            in_quotes = True
            quote_char = char
            current += char
        elif char == quote_char and in_quotes:
            in_quotes = False
            quote_char = None
            current += char
        elif char == delimiter and not in_quotes:
            parts.append(current)
            current = ""
        else:
            current += char

    if current:
        parts.append(current)

    return parts


# ═══════════════════════════════════════════════════════════════════════════════
# BACKWARD COMPATIBILITY
# ═══════════════════════════════════════════════════════════════════════════════

# Re-export old names for compatibility
SSMDSegment = Segment
SSMDSentence = Sentence


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
) -> list[Sentence]:
    """Parse SSMD text into sentences (backward compatible API).

    This is an alias for parse_ssmd() with the old parameter names.

    Args:
        ssmd_text: SSMD formatted text to parse
        capabilities: TTS capabilities or preset name
        include_default_voice: If False, exclude sentences without voice context
        sentence_detection: Enable/disable sentence splitting
        language: Language code for sentence detection
        model_size: Size of spacy model (sm/md/lg)
        spacy_model: Full spacy model name (deprecated, use model_size)
        use_spacy: Force use of spacy for sentence detection

    Returns:
        List of Sentence objects
    """
    sentences = parse_ssmd(
        ssmd_text,
        capabilities=capabilities,
        sentence_detection=sentence_detection,
        language=language,
        model_size=model_size or (spacy_model.split("_")[-1] if spacy_model else None),
        use_spacy=use_spacy,
    )

    # Filter out sentences without voice if requested
    if not include_default_voice:
        sentences = [s for s in sentences if s.voice is not None]

    return sentences


def parse_segments(
    ssmd_text: str,
    *,
    capabilities: "TTSCapabilities | str | None" = None,
    voice_context: VoiceAttrs | None = None,
) -> list[Segment]:
    """Parse SSMD text into segments (backward compatible API)."""
    caps = _resolve_capabilities(capabilities)
    return _parse_segments(ssmd_text, capabilities=caps)


def parse_voice_blocks(ssmd_text: str) -> list[tuple[VoiceAttrs | None, str]]:
    """Parse SSMD text into voice blocks (backward compatible API)."""
    return _split_voice_blocks(ssmd_text)
