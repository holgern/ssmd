"""SSMD parser - Parse SSMD text into structured Sentence/Segment objects.

This module provides functions to parse SSMD markdown into structured data
that can be used for TTS processing or conversion to SSML.
"""

import re
from typing import TYPE_CHECKING

from ssmd.segment import Segment
from ssmd.sentence import Sentence
from ssmd.ssml_conversions import (
    PROSODY_PITCH_MAP,
    PROSODY_RATE_MAP,
    PROSODY_VOLUME_MAP,
    SSMD_BREAK_MARKER_TO_STRENGTH,
)
from ssmd.types import (
    DEFAULT_HEADING_LEVELS,
    AudioAttrs,
    BreakAttrs,
    DirectiveAttrs,
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

# Directive blocks: <div key="value"> ... </div>
DIV_DIRECTIVE_START = re.compile(r"^\s*<div\s+([^>]+)>\s*$", re.IGNORECASE)
DIV_DIRECTIVE_END = re.compile(r"^\s*</div>\s*$", re.IGNORECASE)

# Emphasis patterns
STRONG_EMPHASIS_PATTERN = re.compile(r"\*\*([^\*]+)\*\*")
MODERATE_EMPHASIS_PATTERN = re.compile(r"\*([^\*]+)\*")
REDUCED_EMPHASIS_PATTERN = re.compile(r"(?<!_)_(?!_)([^_]+?)(?<!_)_(?!_)")

# Annotation pattern: [text]{key="value"}
ANNOTATION_PATTERN = re.compile(r"\[([^\]]*)\]\{([^}]*)\}")

# Break pattern: ...500ms, ...2s, ...n, ...w, ...c, ...s, ...p
BREAK_PATTERN = re.compile(r"\.\.\.(\d+(?:s|ms)|[nwcsp])")

# Mark pattern: @name
MARK_PATTERN = re.compile(r"@(\w+)")

# Heading pattern: # ## ###
HEADING_PATTERN = re.compile(r"^\s*(#{1,6})\s*(.+)$", re.MULTILINE)

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
    parse_yaml_header: bool = False,
) -> list[Sentence]:
    """Parse SSMD text into a list of Sentences.

    This is the main parsing function. It handles:
    - Directive blocks (<div ...> ... </div>)
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
        parse_yaml_header: If True, parse YAML front matter and apply
            heading/extensions config while stripping it from the body.

    Returns:
        List of Sentence objects
    """
    if not text or not text.strip():
        return []

    from ssmd.utils import (
        build_config_from_header,
    )
    from ssmd.utils import (
        parse_yaml_header as parse_yaml_front_matter,
    )

    header, text = parse_yaml_front_matter(text)
    if header and parse_yaml_header:
        header_config = build_config_from_header(header)
        heading_levels = header_config.get("heading_levels", heading_levels)
        extensions = header_config.get("extensions", extensions)

    # Resolve capabilities
    caps = _resolve_capabilities(capabilities)

    # Split text into directive blocks
    directive_blocks = _split_directive_blocks(text)

    sentences = []

    for directive, block_text in directive_blocks:
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
                        voice=directive.voice,
                        language=directive.language,
                        prosody=directive.prosody,
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


def _split_directive_blocks(text: str) -> list[tuple[DirectiveAttrs, str]]:
    """Split text into directive blocks defined by <div ...> tags."""
    blocks: list[tuple[DirectiveAttrs, str]] = []
    stack: list[DirectiveAttrs] = [DirectiveAttrs()]
    current_lines: list[str] = []

    def flush_block() -> None:
        if not current_lines:
            return
        block_text = "\n".join(current_lines)
        if block_text.strip():
            blocks.append((stack[-1], block_text))
        current_lines.clear()

    for line in text.split("\n"):
        start_match = DIV_DIRECTIVE_START.match(line)
        if start_match:
            flush_block()
            attrs = _parse_div_attrs(start_match.group(1))
            stack.append(_merge_directives(stack[-1], attrs))
            continue

        if DIV_DIRECTIVE_END.match(line):
            if len(stack) > 1:
                flush_block()
                stack.pop()
                continue
            current_lines.append(line)
            continue

        current_lines.append(line)

    flush_block()

    if not blocks and text.strip():
        blocks.append((DirectiveAttrs(), text.strip()))

    return blocks


def _parse_div_attrs(params: str) -> DirectiveAttrs:
    """Parse <div ...> attribute params into directive attrs."""
    params_map = _parse_annotation_params(params)
    directive = DirectiveAttrs()

    language = params_map.get("lang") or params_map.get("language")
    if language:
        directive.language = language

    voice = _parse_voice_annotation_params(params_map)
    if voice:
        directive.voice = voice

    if "voice" in params_map and directive.voice:
        directive.voice.name = params_map["voice"]

    prosody = _parse_prosody_params(params_map)
    if prosody:
        directive.prosody = prosody

    return directive


def _merge_directives(base: DirectiveAttrs, update: DirectiveAttrs) -> DirectiveAttrs:
    """Merge directive attributes for nested <div> blocks."""
    return DirectiveAttrs(
        voice=update.voice or base.voice,
        language=update.language or base.language,
        prosody=update.prosody or base.prosody,
    )


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

        should_escape = use_spacy is not False
        escaped_text = text
        annotation_placeholders: list[str] = []
        placeholder_tokens: list[str] = []
        if should_escape:
            placeholder_base = 0xF100

            def _replace_annotation(match: re.Match[str]) -> str:
                annotation_placeholders.append(match.group(0))
                placeholder = chr(placeholder_base + len(annotation_placeholders) - 1)
                placeholder_tokens.append(placeholder)
                return placeholder

            escaped_text = re.sub(r"\[[^\]]*\]\{[^}]*\}", _replace_annotation, text)

        segments = split_text(
            escaped_text,
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

        if not should_escape:
            return sentences if sentences else [text]

        if not sentences:
            return [text]

        restored_sentences: list[str] = []
        for idx, sentence in enumerate(sentences):
            restored = sentence
            for placeholder_index, annotation in enumerate(annotation_placeholders):
                restored = restored.replace(
                    placeholder_tokens[placeholder_index], annotation
                )
            if idx < len(sentences) - 1:
                restored = restored.rstrip() + "\n"
            restored_sentences.append(restored)

        return restored_sentences

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
        r"|\[[^\]]*\]\{[^}]+\}"  # [text]{annotation}
        r"|\.\.\.(?:\d+(?:s|ms)|[nwcsp])"  # breaks
        r"|@(?!voice[:(])\w+"  # marks
        r")"
    )

    pending_breaks: list[BreakAttrs] = []
    pending_marks: list[str] = []

    for match in combined.finditer(text):
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
        pending_breaks, pending_marks, markup_seg = _handle_markup(
            markup,
            segments,
            pending_breaks,
            pending_marks,
            extensions,
        )
        if markup_seg:
            segments.append(markup_seg)

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


def _handle_markup(
    markup: str,
    segments: list[Segment],
    pending_breaks: list[BreakAttrs],
    pending_marks: list[str],
    extensions: dict | None,
) -> tuple[list[BreakAttrs], list[str], Segment | None]:
    """Handle a single markup token and return any segment."""
    if markup.startswith("..."):
        brk = _parse_break(markup[3:])
        if segments:
            segments[-1].breaks_after.append(brk)
        else:
            pending_breaks.append(brk)
        return pending_breaks, pending_marks, None

    if markup.startswith("@"):
        mark_name = markup[1:]
        if segments:
            segments[-1].marks_after.append(mark_name)
        else:
            pending_marks.append(mark_name)
        return pending_breaks, pending_marks, None

    seg = _segment_from_markup(markup, extensions)
    if seg:
        _apply_pending(seg, pending_breaks, pending_marks)
        return [], [], seg

    return pending_breaks, pending_marks, None


def _segment_from_markup(markup: str, extensions: dict | None) -> Segment | None:
    """Build a segment from emphasis, annotation, or prosody markup."""
    if markup.startswith("**"):
        inner = STRONG_EMPHASIS_PATTERN.match(markup)
        if inner:
            return Segment(text=inner.group(1), emphasis="strong")
        return None

    if markup.startswith("*"):
        inner = MODERATE_EMPHASIS_PATTERN.match(markup)
        if inner:
            return Segment(text=inner.group(1), emphasis=True)
        return None

    if markup.startswith("_") and not markup.startswith("__"):
        inner = REDUCED_EMPHASIS_PATTERN.match(markup)
        if inner:
            return Segment(text=inner.group(1), emphasis="reduced")
        return None

    if markup.startswith("["):
        return _parse_annotation(markup, extensions)

    return None


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
        elif effect_type == "pause_before":
            seg.breaks_before.append(BreakAttrs(time=value))
        elif effect_type == "prosody" and isinstance(value, dict):
            seg.prosody = ProsodyAttrs(
                volume=value.get("volume"),
                rate=value.get("rate"),
                pitch=value.get("pitch"),
            )

    return [seg]


def _parse_break(modifier: str) -> BreakAttrs:
    """Parse break modifier into BreakAttrs."""
    if modifier in SSMD_BREAK_MARKER_TO_STRENGTH:
        return BreakAttrs(strength=SSMD_BREAK_MARKER_TO_STRENGTH[modifier])
    elif modifier.endswith("s") or modifier.endswith("ms"):
        return BreakAttrs(time=modifier)
    else:
        return BreakAttrs(time=f"{modifier}ms")


def _parse_annotation(markup: str, extensions: dict | None = None) -> Segment | None:
    """Parse [text]{key="value"} markup."""
    match = ANNOTATION_PATTERN.match(markup)
    if not match:
        return None

    text = match.group(1)
    params = match.group(2).strip()

    seg = Segment(text=text)
    params_map = _parse_annotation_params(params)

    if not params_map:
        return seg

    if "src" in params_map:
        seg.audio = _parse_audio_annotation_params(params_map)
        return seg

    if "lang" in params_map:
        seg.language = params_map["lang"]
    elif "language" in params_map:
        seg.language = params_map["language"]

    voice = _parse_voice_annotation_params(params_map)
    if voice:
        seg.voice = voice

    say_as = _parse_say_as_params(params_map)
    if say_as:
        seg.say_as = say_as

    phoneme = _parse_phoneme_params(params_map)
    if phoneme:
        seg.phoneme = phoneme

    if "sub" in params_map:
        seg.substitution = params_map["sub"]

    if "emphasis" in params_map:
        level = params_map["emphasis"].lower()
        if level in ("none", "reduced", "moderate", "strong"):
            seg.emphasis = level if level != "moderate" else True

    if "ext" in params_map:
        seg.extension = params_map["ext"]

    prosody = _parse_prosody_params(params_map)
    if prosody:
        seg.prosody = prosody

    return seg


def _parse_annotation_params(params: str) -> dict[str, str]:
    """Parse key="value" pairs from annotation params."""
    if not params:
        return {}

    pattern = re.compile(r"([a-zA-Z][\w-]*)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|(\S+))")
    values: dict[str, str] = {}

    for match in pattern.finditer(params):
        key = match.group(1).lower()
        if match.group(2) is not None:
            value = match.group(2)
        elif match.group(3) is not None:
            value = match.group(3)
        else:
            value = match.group(4) or ""
        values[key] = value

    return values


def _parse_audio_annotation_params(params_map: dict[str, str]) -> AudioAttrs:
    """Parse audio parameters from annotation map."""
    audio = AudioAttrs(src=params_map["src"])

    clip = params_map.get("clip")
    if clip and "-" in clip:
        clip_begin, clip_end = clip.split("-", 1)
        audio.clip_begin = clip_begin.strip()
        audio.clip_end = clip_end.strip()

    if params_map.get("speed"):
        audio.speed = params_map["speed"]

    repeat = params_map.get("repeat")
    if repeat:
        try:
            audio.repeat_count = int(repeat)
        except ValueError:
            pass

    if params_map.get("repeatdur"):
        audio.repeat_dur = params_map["repeatdur"]

    if params_map.get("level"):
        audio.sound_level = params_map["level"]

    if params_map.get("alt"):
        audio.alt_text = params_map["alt"]

    return audio


def _parse_voice_annotation_params(params_map: dict[str, str]) -> VoiceAttrs | None:
    """Parse voice params from annotation map."""
    if not any(
        key in params_map
        for key in ("voice", "voice-lang", "voice_lang", "gender", "variant")
    ):
        return None

    voice = VoiceAttrs()
    voice_name = params_map.get("voice")
    voice_lang = params_map.get("voice-lang") or params_map.get("voice_lang")

    if voice_name:
        voice.name = voice_name

    if voice_lang:
        voice.language = voice_lang

    if "gender" in params_map:
        voice.gender = params_map["gender"].lower()  # type: ignore[assignment]

    if "variant" in params_map:
        try:
            voice.variant = int(params_map["variant"])
        except ValueError:
            pass

    return voice


def _parse_say_as_params(params_map: dict[str, str]) -> SayAsAttrs | None:
    """Parse say-as params from annotation map."""
    interpret_as = params_map.get("as") or params_map.get("say-as")
    if not interpret_as:
        return None

    return SayAsAttrs(
        interpret_as=interpret_as,
        format=params_map.get("format"),
        detail=params_map.get("detail"),
    )


def _parse_phoneme_params(params_map: dict[str, str]) -> PhonemeAttrs | None:
    """Parse phoneme params from annotation map."""
    if "ipa" in params_map:
        return PhonemeAttrs(ph=params_map["ipa"], alphabet="ipa")

    if "sampa" in params_map:
        return PhonemeAttrs(ph=params_map["sampa"], alphabet="x-sampa")

    if "ph" in params_map:
        alphabet = params_map.get("alphabet", "ipa").lower()
        if alphabet == "sampa":
            alphabet = "x-sampa"
        return PhonemeAttrs(ph=params_map["ph"], alphabet=alphabet)

    return None


def _parse_prosody_params(params_map: dict[str, str]) -> ProsodyAttrs | None:
    """Parse prosody params from annotation map."""
    volume = params_map.get("volume") or params_map.get("v")
    rate = params_map.get("rate") or params_map.get("r")
    pitch = params_map.get("pitch") or params_map.get("p")

    if not any([volume, rate, pitch]):
        return None

    prosody = ProsodyAttrs()

    if volume:
        prosody.volume = _normalize_prosody_value(volume, PROSODY_VOLUME_MAP)
    if rate:
        prosody.rate = _normalize_prosody_value(rate, PROSODY_RATE_MAP)
    if pitch:
        prosody.pitch = _normalize_prosody_value(pitch, PROSODY_PITCH_MAP)

    return prosody


def _normalize_prosody_value(value: str, mapping: dict[str, str]) -> str:
    """Normalize prosody values to named levels where possible."""
    stripped = value.strip()
    if stripped.isdigit() and stripped in mapping:
        return mapping[stripped]

    lowered = stripped.lower()
    if lowered in mapping.values():
        return lowered

    return stripped


def _is_language_code(value: str) -> bool:
    return bool(re.match(r"^[a-z]{2}(-[A-Z]{2})?$", value))


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
                voice.gender = part[7:].strip().lower()  # type: ignore[assignment]
            elif part.startswith("variant:"):
                voice.variant = int(part[8:].strip())
    else:
        # Simple name or language
        if re.match(r"^[a-z]{2}(-[A-Z]{2})?$", params):
            voice.language = params
        else:
            voice.name = params

    return voice


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
    heading_levels: dict | None = None,
    extensions: dict | None = None,
    parse_yaml_header: bool = False,
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
        heading_levels: Custom heading configurations
        extensions: Custom extension handlers
        parse_yaml_header: If True, parse YAML front matter and apply
            heading/extensions config while stripping it from the body.

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
        heading_levels=heading_levels,
        extensions=extensions,
        parse_yaml_header=parse_yaml_header,
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
    if voice_context is not None:
        _ = voice_context
    caps = _resolve_capabilities(capabilities)
    return _parse_segments(ssmd_text, capabilities=caps)


def parse_voice_blocks(ssmd_text: str) -> list[tuple[DirectiveAttrs, str]]:
    """Parse SSMD text into directive blocks (backward compatible API).

    Returns list of (DirectiveAttrs, text) tuples.
    """
    return _split_directive_blocks(ssmd_text)
