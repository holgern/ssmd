"""Sentence - A collection of segments with voice context.

A Sentence represents a logical unit of speech that should be spoken together.
Sentences contain segments and have an optional voice context.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ssmd.segment import Segment
from ssmd.types import BreakAttrs, VoiceAttrs

if TYPE_CHECKING:
    from ssmd.capabilities import TTSCapabilities


@dataclass
class Sentence:
    """A sentence containing segments with voice context.

    Represents a logical sentence unit that should be spoken together.
    Sentences are split on:
    - Voice changes (@voice: directive)
    - Sentence boundaries (.!?) when sentence_detection=True
    - Paragraph breaks (\\n\\n)

    Attributes:
        segments: List of segments in the sentence
        voice: Voice context for entire sentence (from @voice: directive)
        is_paragraph_end: True if sentence ends with paragraph break
        breaks_after: Pauses after the sentence
    """

    segments: list[Segment] = field(default_factory=list)
    voice: VoiceAttrs | None = None
    is_paragraph_end: bool = False
    breaks_after: list[BreakAttrs] = field(default_factory=list)

    def to_ssml(
        self,
        capabilities: "TTSCapabilities | None" = None,
        extensions: dict | None = None,
        wrap_sentence: bool = False,
    ) -> str:
        """Convert sentence to SSML.

        Args:
            capabilities: TTS engine capabilities for filtering
            extensions: Custom extension handlers
            wrap_sentence: If True, wrap content in <s> tag

        Returns:
            SSML string
        """
        # Build segment content
        content_parts = []
        for segment in self.segments:
            content_parts.append(segment.to_ssml(capabilities, extensions))

        # Join segments with spaces, but handle punctuation intelligently
        content = self._join_segments(content_parts)

        # Wrap in <s> tag if requested
        if wrap_sentence:
            content = f"<s>{content}</s>"

        # Wrap in voice tag if voice is set
        # Voice is always enabled as it's fundamental to TTS
        if self.voice:
            content = self._wrap_voice(content)

        # Add breaks after sentence
        if not capabilities or capabilities.break_tags:
            for brk in self.breaks_after:
                content += self._break_to_ssml(brk)

        return content

    def _join_segments(self, parts: list[str]) -> str:
        """Join SSML segment parts with appropriate spacing.

        Adds spaces between segments but not before punctuation.

        Args:
            parts: List of SSML strings for each segment

        Returns:
            Joined SSML string
        """
        import re

        if not parts:
            return ""

        result = parts[0]
        for i in range(1, len(parts)):
            part = parts[i]
            # Don't add space before punctuation or if part starts with <break
            if part and (
                re.match(r'^[.!?,;:\'")\]}>]', part)
                or part.startswith("<break")
                or part.startswith("<mark")
            ):
                result += part
            # Don't add space if previous part ends with opening bracket/quote
            elif result and result[-1] in "([{<\"'":
                result += part
            else:
                result += " " + part

        return result

    def _wrap_voice(self, content: str) -> str:
        """Wrap content in voice tag."""
        if not self.voice:
            return content

        attrs = []
        if self.voice.name:
            attrs.append(f'name="{self.voice.name}"')
        else:
            if self.voice.language:
                attrs.append(f'language="{self.voice.language}"')
            if self.voice.gender:
                attrs.append(f'gender="{self.voice.gender}"')
            if self.voice.variant:
                attrs.append(f'variant="{self.voice.variant}"')

        if attrs:
            return f"<voice {' '.join(attrs)}>{content}</voice>"
        return content

    def _break_to_ssml(self, brk: BreakAttrs) -> str:
        """Convert break to SSML."""
        if brk.time:
            return f'<break time="{brk.time}"/>'
        elif brk.strength:
            return f'<break strength="{brk.strength}"/>'
        return "<break/>"

    def to_ssmd(self) -> str:
        """Convert sentence to SSMD markdown.

        Returns:
            SSMD string
        """
        result = ""

        # Add voice directive if set
        if self.voice:
            voice_directive = self._voice_to_directive()
            if voice_directive:
                result += voice_directive + "\n"

        # Build segment content
        content_parts = []
        for segment in self.segments:
            content_parts.append(segment.to_ssmd())

        content = "".join(content_parts)
        result += content

        # Add breaks after sentence
        for brk in self.breaks_after:
            result += " " + self._break_to_ssmd(brk)

        return result

    def _voice_to_directive(self) -> str:
        """Convert voice to @voice: directive."""
        if not self.voice:
            return ""

        if self.voice.name:
            return f"@voice: {self.voice.name}"
        else:
            parts = []
            if self.voice.language:
                parts.append(self.voice.language)
            if self.voice.gender:
                parts.append(f"gender: {self.voice.gender}")
            if self.voice.variant:
                parts.append(f"variant: {self.voice.variant}")
            if parts:
                return f"@voice: {', '.join(parts)}"
        return ""

    def _break_to_ssmd(self, brk: BreakAttrs) -> str:
        """Convert break to SSMD format."""
        if brk.time:
            return f"...{brk.time}"
        elif brk.strength:
            strength_map = {
                "none": "...n",
                "x-weak": "...w",
                "weak": "...w",
                "medium": "...c",
                "strong": "...s",
                "x-strong": "...p",
            }
            return strength_map.get(brk.strength, "...s")
        return "...s"

    def to_text(self) -> str:
        """Convert sentence to plain text.

        Returns:
            Plain text with all markup removed
        """
        text_parts = [segment.to_text() for segment in self.segments]
        return self._join_text_parts(text_parts)

    def _join_text_parts(self, parts: list[str]) -> str:
        """Join text parts with appropriate spacing.

        Adds spaces between parts but not before punctuation.

        Args:
            parts: List of text strings for each segment

        Returns:
            Joined text string
        """
        import re

        if not parts:
            return ""

        # Filter out empty parts
        parts = [p for p in parts if p]
        if not parts:
            return ""

        result = parts[0]
        for i in range(1, len(parts)):
            part = parts[i]
            # Don't add space before punctuation
            if part and re.match(r'^[.!?,;:\'")\]}>]', part):
                result += part
            # Don't add space if previous part ends with opening bracket/quote
            elif result and result[-1] in "([{<\"'":
                result += part
            else:
                result += " " + part

        return result

    @property
    def text(self) -> str:
        """Get plain text content of the sentence.

        Returns:
            Plain text string
        """
        return self.to_text()

    def __str__(self) -> str:
        """String representation returns plain text."""
        return self.to_text()

    def __len__(self) -> int:
        """Return number of segments."""
        return len(self.segments)

    def __iter__(self):
        """Iterate over segments."""
        return iter(self.segments)
