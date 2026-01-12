"""SSMD formatting utilities for properly formatted output.

This module provides utilities to format parsed SSMD sentences with proper
line breaks, paragraph spacing, and structural elements according to SSMD
formatting conventions.
"""

from ssmd.segment import Segment
from ssmd.sentence import Sentence
from ssmd.types import BreakAttrs, VoiceAttrs

# Backward compatibility aliases
SSMDSentence = Sentence
SSMDSegment = Segment


def _format_segment(segment: Segment) -> str:
    """Format a single segment to SSMD (backward compatibility wrapper).

    Args:
        segment: Segment object to format

    Returns:
        Formatted SSMD string for this segment
    """
    return segment.to_ssmd().strip()


def _format_sentence(sentence: Sentence) -> str:
    """Format a sentence's content (backward compatibility wrapper).

    This is an alias for _format_sentence_content.

    Args:
        sentence: Sentence object to format

    Returns:
        Formatted sentence text
    """
    return _format_sentence_content(sentence)


def format_ssmd(sentences: list[Sentence]) -> str:
    """Format parsed SSMD sentences with proper line breaks.

    This function takes a list of parsed Sentence objects and formats them
    according to SSMD formatting conventions:

    - Each sentence on a new line (after . ? !)
    - Break markers at sentence boundaries: end of previous line
    - Break markers mid-sentence: stay inline between segments
    - Paragraph breaks: double newline
    - Voice directives: separate line with blank line after
    - Headings: blank lines before and after

    Args:
        sentences: List of parsed Sentence objects

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
        # Check if voice changed - output directive on its own line
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

        # Format the sentence using to_ssmd() but without voice directive
        # (we handle voice directives separately above)
        sentence_text = _format_sentence_content(sentence)

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


def _format_sentence_content(sentence: Sentence) -> str:
    """Format a single sentence's content (segments only, no voice directive).

    Args:
        sentence: Sentence object to format

    Returns:
        Formatted sentence text with inline and trailing breaks
    """
    if not sentence.segments:
        return ""

    # Build segments using their to_ssmd() method
    result_parts: list[str] = []

    for i, segment in enumerate(sentence.segments):
        # Format the segment using its to_ssmd() method
        segment_text = segment.to_ssmd()

        # Preserve the trailing space if segment has breaks_after
        if segment.breaks_after:
            segment_text = segment_text.rstrip() + " "
        else:
            segment_text = segment_text.strip()

        if not segment_text.strip():
            continue

        # Add this segment
        result_parts.append(segment_text)

    # Join segments intelligently
    sentence_text = ""
    for i, part in enumerate(result_parts):
        if i == 0:
            sentence_text = part
        elif part.startswith("..."):
            # This is a break marker - append without extra space
            sentence_text += part
        elif i > 0 and _ends_with_break_marker(result_parts[i - 1]):
            # Previous part ends with break marker, already has space
            sentence_text += part
        elif i > 0 and result_parts[i - 1].endswith((" ", "\n")):
            # Previous part ends with whitespace
            sentence_text += part
        else:
            # Normal text segment - add space
            sentence_text += " " + part

    # Add sentence-level breaks at end of line
    if sentence.breaks_after:
        break_marker = _format_breaks(sentence.breaks_after)
        sentence_text += " " + break_marker

    return sentence_text.strip()


def _ends_with_break_marker(text: str) -> bool:
    """Check if text ends with a break marker like ...s, ...500ms, etc."""
    import re

    # Break marker pattern: ... followed by strength letter or time
    return bool(re.search(r"\.\.\.[swcpn]$|\.\.\.\d+(ms|s)$", text.rstrip()))


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


def _format_voice_directive(voice: VoiceAttrs) -> str:
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
    if voice.name:
        parts.append(voice.name)
    elif voice.language:
        parts.append(voice.language)

    # Add optional attributes
    if voice.gender:
        parts.append(f"gender: {voice.gender}")
    if voice.variant:
        parts.append(f"variant: {voice.variant}")

    if parts:
        return f"@voice: {', '.join(parts)}"

    return ""
