"""Mark processor: @mark → <mark name="mark"/>"""

import re

from ssmd.processors.base import BaseProcessor


class MarkProcessor(BaseProcessor):
    """Process mark annotations (@name)."""

    name = "mark"

    def regex(self) -> re.Pattern:
        """Match @ followed by identifier.

        Returns:
            Pattern matching @identifier
        """
        return re.compile(r"@(\w+)")

    def result(self, match: re.Match) -> str:
        """Convert to SSML mark element.

        Args:
            match: Regex match object

        Returns:
            SSML <mark/> tag
        """
        name = match.group(1)
        return f'<mark name="{name}"/>'

    def text(self, match: re.Match) -> str:
        """Extract plain text (marks have no text content).

        Args:
            match: Regex match object

        Returns:
            Empty string (marks are removed in plain text)
        """
        return ""

    def is_no_content(self) -> bool:
        """Marks have no content output.

        Returns:
            True (remove adjacent whitespace)
        """
        return True
