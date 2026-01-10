"""Emphasis processor: *text* → <emphasis>text</emphasis>"""

import re

from ssmd.processors.base import BaseProcessor


class EmphasisProcessor(BaseProcessor):
    """Process emphasis markup (*text*)."""

    name = "emphasis"

    def regex(self) -> re.Pattern:
        """Match text wrapped in single asterisks.

        Returns:
            Pattern matching *text*
        """
        return re.compile(r"\*([^\*]+)\*")

    def result(self, match: re.Match) -> str:
        """Convert to SSML emphasis element.

        Args:
            match: Regex match object

        Returns:
            SSML <emphasis> tag
        """
        text = match.group(1)
        return f"<emphasis>{text}</emphasis>"

    def text(self, match: re.Match) -> str:
        """Extract plain text without asterisks.

        Args:
            match: Regex match object

        Returns:
            Plain text content
        """
        return match.group(1)
