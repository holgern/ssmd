"""SSMD formatting utilities for properly formatted output.

This module provides utilities to format parsed SSMD sentences with proper
line breaks, paragraph spacing, and structural elements according to SSMD
formatting conventions.
"""

from ssmd.parser_types import BreakAttrs, SSMDSegment, SSMDSentence


def format_ssmd(sentences: list[SSMDSentence]) -> str:
    """Format parsed SSMD sentences with proper line breaks.

    This function takes a list of parsed SSMDSentence objects and formats them
    according to SSMD formatting conventions:

    - Each sentence on a new line (after . ? !)
    - Break markers at sentence boundaries: end of previous line
    - Break markers mid-sentence: stay inline between segments
    - Paragraph breaks: double newline
    - Voice directives: separate line with blank line after
    - Headings: blank lines before and after

    Args:
        sentences: List of parsed SSMDSentence objects

    Returns:
        Properly formatted SSMD string

    Example:
        >>> from ssmd.parser import parse_sentences
        >>> sentences = parse_sentences("Hello. ...s How are you?")
        >>> formatted = format_ssmd(sentences)
        >>> print(formatted)
        Hello. ...s
        How are you?
    """
    if not sentences:
        return ""

    output_lines: list[str] = []
    previous_voice = None

    for i, sentence in enumerate(sentences):
        # Check if voice changed
        if sentence.voice != previous_voice and sentence.voice is not None:
            # Add voice directive
            voice_directive = _format_voice_directive(sentence.voice)
            if voice_directive:
                # Add blank line before voice directive if not first
                if output_lines and output_lines[-1] != "":
                    output_lines.append("")
                output_lines.append(voice_directive)
                output_lines.append("")  # Blank line after voice directive
            previous_voice = sentence.voice

        # Check if sentence has breaks_before (from previous sentence boundary)
        # These should be appended to the previous line
        if i > 0 and sentence.segments and sentence.segments[0].breaks_before:
            # Append break to previous line
            if output_lines:
                break_marker = _format_breaks(sentence.segments[0].breaks_before)
                output_lines[-1] += " " + break_marker

        # Format the sentence
        sentence_text = _format_sentence(sentence)

        if sentence_text:
            output_lines.append(sentence_text)

            # Add paragraph break if needed
            if sentence.is_paragraph_end:
                output_lines.append("")  # Extra blank line for paragraph

    # Join lines and ensure trailing newline
    result = "\n".join(output_lines)

    # Clean up multiple consecutive blank lines (max 1 blank line)
    while "\n\n\n" in result:
        result = result.replace("\n\n\n", "\n\n")

    return result.rstrip() + "\n" if result else ""


def _format_sentence(sentence: SSMDSentence) -> str:
    """Format a single sentence with its segments and breaks.

    Args:
        sentence: SSMDSentence object to format

    Returns:
        Formatted sentence text with inline and trailing breaks
    """
    if not sentence.segments:
        return ""

    # Build segments with inline breaks
    result_parts: list[str] = []

    for i, segment in enumerate(sentence.segments):
        # Format the segment text
        segment_text = _format_segment(segment)

        if not segment_text:
            continue

        # Add this segment
        result_parts.append(segment_text)

        # Add breaks after this segment (if not the last segment)
        if segment.breaks_after and i < len(sentence.segments) - 1:
            # Mid-sentence break - add inline without space
            break_marker = _format_breaks(segment.breaks_after)
            result_parts.append(break_marker)

    # Join segments intelligently
    sentence_text = ""
    for i, part in enumerate(result_parts):
        if i == 0:
            sentence_text = part
        elif part.startswith("..."):
            # This is a break marker - append without space
            sentence_text += part
        elif i > 0 and result_parts[i - 1].startswith("..."):
            # Previous part was a break marker - append without space
            sentence_text += part
        elif i > 0 and result_parts[i - 1].endswith((" ", "\n")):
            # Previous part ends with whitespace, append without extra space
            sentence_text += part
        else:
            # Normal text segment - add space
            sentence_text += " " + part

    # Add sentence-level breaks at end of line
    if sentence.breaks_after:
        break_marker = _format_breaks(sentence.breaks_after)
        sentence_text += " " + break_marker

    # Also check if last segment has breaks_after (sentence boundary)
    if sentence.segments and sentence.segments[-1].breaks_after:
        break_marker = _format_breaks(sentence.segments[-1].breaks_after)
        sentence_text += " " + break_marker

    return sentence_text.strip()


def _format_segment(segment: SSMDSegment) -> str:  # noqa: C901
    """Format a single segment, reconstructing markup from attributes.

    Reconstructs SSMD markup like *emphasis*, [language](lang: en),
    substitution, prosody, etc. from segment attributes.

    Args:
        segment: SSMDSegment object to format

    Returns:
        Formatted segment text with SSMD markup
    """
    text = segment.text.strip()

    if not text:
        return ""

    # Wrap with emphasis if needed
    if segment.emphasis:
        if segment.emphasis == "strong":
            text = f"**{text}**"
        elif segment.emphasis == "reduced":
            text = f"_{text}_"
        else:  # True or "moderate"
            text = f"*{text}*"

    # Add language annotation if needed
    if segment.language:
        text = f"[{text}](lang: {segment.language})"

    # Add substitution if needed
    if segment.substitution:
        text = f"[{text}](sub: {segment.substitution})"

    # Add phoneme if needed
    if segment.phoneme:
        alphabet = segment.phoneme.alphabet or "ipa"
        text = f"[{text}](ph: {segment.phoneme.ph}, alphabet: {alphabet})"

    # Add say-as if needed
    if segment.say_as:
        if segment.say_as.format:
            text = (
                f"[{text}](say-as: {segment.say_as.interpret_as}, "
                f"format: {segment.say_as.format})"
            )
        else:
            text = f"[{text}](say-as: {segment.say_as.interpret_as})"

    # Add prosody if needed
    if segment.prosody:
        props = []
        if segment.prosody.rate:
            props.append(f"rate: {segment.prosody.rate}")
        if segment.prosody.pitch:
            props.append(f"pitch: {segment.prosody.pitch}")
        if segment.prosody.volume:
            props.append(f"volume: {segment.prosody.volume}")
        if props:
            text = f"[{text}]({', '.join(props)})"

    # Add extension if needed
    if segment.extension:
        text = f"[{text}](ext: {segment.extension})"

    # Add voice if needed
    if segment.voice:
        # Build voice annotation: [text](voice: name)
        # or [text](voice: lang, gender: X, variant: Y)
        voice_parts = []
        if segment.voice.name:
            voice_parts.append(f"voice: {segment.voice.name}")
        elif segment.voice.language:
            voice_parts.append(f"voice: {segment.voice.language}")

        if segment.voice.gender:
            voice_parts.append(f"gender: {segment.voice.gender}")
        if segment.voice.variant:
            voice_parts.append(f"variant: {segment.voice.variant}")

        if voice_parts:
            text = f"[{text}]({', '.join(voice_parts)})"

    # Add audio if needed
    if segment.audio:
        # Build audio annotation: [text](url attrs alt)
        audio_parts = [segment.audio.src]

        # Add attributes if present
        if segment.audio.clip_begin and segment.audio.clip_end:
            audio_parts.append(
                f"clip: {segment.audio.clip_begin}-{segment.audio.clip_end}"
            )
        if segment.audio.speed:
            audio_parts.append(f"speed: {segment.audio.speed}")
        if segment.audio.repeat_count:
            audio_parts.append(f"repeat: {segment.audio.repeat_count}")
        if segment.audio.repeat_dur:
            audio_parts.append(f"repeatDur: {segment.audio.repeat_dur}")
        if segment.audio.sound_level:
            audio_parts.append(f"level: {segment.audio.sound_level}")

        # Add 'alt' marker if present
        if segment.audio.alt_text == "alt":
            audio_parts.append("alt")
        elif segment.audio.alt_text:
            audio_parts.append(segment.audio.alt_text)

        audio_annotation = " ".join(audio_parts)
        text = f"[{text}]({audio_annotation})"

    # Handle marks
    if segment.marks_before:
        for mark in segment.marks_before:
            text = f"@{mark}{text}"

    if segment.marks_after:
        for mark in segment.marks_after:
            text = f"{text}@{mark}"

    return text


def _format_breaks(breaks: list[BreakAttrs]) -> str:
    """Convert break attributes to SSMD break markers.

    Args:
        breaks: List of BreakAttrs objects

    Returns:
        SSMD break marker string (e.g., "...s", "...500ms")
    """
    if not breaks:
        return ""

    # Format each break
    break_markers = []
    for brk in breaks:
        if brk.time:
            # Time-based break: ...500ms or ...2s
            break_markers.append(f"...{brk.time}")
        elif brk.strength:
            # Strength-based break
            strength_map = {
                "none": "n",
                "x-weak": "w",
                "weak": "w",
                "medium": "c",
                "strong": "s",
                "x-strong": "p",
            }
            marker = strength_map.get(brk.strength, "s")
            break_markers.append(f"...{marker}")
        else:
            # Default to strong break
            break_markers.append("...s")

    return " ".join(break_markers)


def _format_voice_directive(voice) -> str:
    """Format a voice directive.

    Args:
        voice: VoiceAttrs object

    Returns:
        Voice directive string
        (e.g., "@voice: sarah" or "@voice: fr-FR, gender: female")
    """
    if not voice:
        return ""

    # Build parts for the directive
    parts = []

    # Add name or language as first part
    if hasattr(voice, "name") and voice.name:
        parts.append(voice.name)
    elif hasattr(voice, "language") and voice.language:
        parts.append(voice.language)

    # Add optional attributes
    if hasattr(voice, "gender") and voice.gender:
        parts.append(f"gender: {voice.gender}")
    if hasattr(voice, "variant") and voice.variant:
        parts.append(f"variant: {voice.variant}")

    if parts:
        return f"@voice: {', '.join(parts)}"

    return ""
