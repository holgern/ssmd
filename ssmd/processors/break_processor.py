"""Break processor: ...500ms, ...2s, ...n, ...c → <break/>"""

import re

from ssmd.processors.base import BaseProcessor


class BreakProcessor(BaseProcessor):
    """Process break/pause markup (...n, ...500ms, ...2s, etc.).

    Note: Bare '...' is NOT supported to avoid conflicts with ellipsis.
    """

    name = "break"

    def regex(self) -> re.Pattern:
        """Match break patterns.

        Supports:
        - ...5s (5 seconds)
        - ...100ms (100 milliseconds)
        - ...100 (100 milliseconds)
        - ...n (none)
        - ...w (weak/x-weak)
        - ...c (medium/comma)
        - ...s (strong/sentence)
        - ...p (x-strong/paragraph)

        Note: Bare '...' is NOT supported (conflicts with ellipsis in text)

        Returns:
            Pattern matching break syntax
        """
        return re.compile(r"\.\.\.(\d+(?:s|ms)|[nwcsp])")

    def result(self, match: re.Match) -> str:
        """Convert to SSML break element.

        Args:
            match: Regex match object

        Returns:
            SSML <break/> tag
        """
        modifier = match.group(1)

        if modifier == "n":
            # None/no break
            return '<break strength="none"/>'
        elif modifier == "w":
            # Weak (x-weak)
            return '<break strength="x-weak"/>'
        elif modifier == "c":
            # Comma (medium)
            return '<break strength="medium"/>'
        elif modifier == "s":
            # Sentence (strong)
            return '<break strength="strong"/>'
        elif modifier == "p":
            # Paragraph (x-strong)
            return '<break strength="x-strong"/>'
        elif modifier.endswith("s") or modifier.endswith("ms"):
            # Explicit time
            return f'<break time="{modifier}"/>'
        else:
            # Number without unit = milliseconds
            return f'<break time="{modifier}ms"/>'

    def text(self, match: re.Match) -> str:
        """Extract plain text (breaks have no text content).

        Args:
            match: Regex match object

        Returns:
            Empty string (breaks are removed in plain text)
        """
        return ""

    def is_no_content(self) -> bool:
        """Breaks have no content output.

        Returns:
            True (remove adjacent whitespace)
        """
        return True
