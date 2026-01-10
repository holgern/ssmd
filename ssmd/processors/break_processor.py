"""Break processor: ... → <break/>"""

import re

from ssmd.processors.base import BaseProcessor


class BreakProcessor(BaseProcessor):
    """Process break/pause markup (...)."""

    name = "break"

    def regex(self) -> re.Pattern:
        """Match break patterns.

        Supports:
        - ... (default 1000ms)
        - ...5s (5 seconds)
        - ...100ms (100 milliseconds)
        - ...100 (100 milliseconds)
        - ...c (medium/comma)
        - ...s (strong/sentence)
        - ...p (x-strong/paragraph)
        - ...0 (none/skip)

        Returns:
            Pattern matching break syntax
        """
        return re.compile(r"\.\.\.(\d+(?:s|ms)|[csps0])?")

    def result(self, match: re.Match) -> str:
        """Convert to SSML break element.

        Args:
            match: Regex match object

        Returns:
            SSML <break/> tag
        """
        modifier = match.group(1)

        if not modifier:
            # Default: 1000ms (x-strong)
            return '<break time="1000ms"/>'

        if modifier == "0":
            # No break
            return '<break strength="none"/>'
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
