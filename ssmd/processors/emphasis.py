"""Emphasis processor: *text* → <emphasis>text</emphasis>"""

import re

from ssmd.processors.base import BaseProcessor


class EmphasisProcessor(BaseProcessor):
    """Process emphasis markup (*text* and **text**)."""

    name = "emphasis"

    def regex(self) -> re.Pattern:
        """Match text wrapped in asterisks.

        Matches both:
        - **text** for strong emphasis
        - *text* for moderate emphasis

        Returns:
            Pattern matching *text* or **text**
        """
        # Match ** first (longer pattern), then single *
        # Use negative lookbehind/lookahead to avoid matching *** as both
        return re.compile(r"\*\*([^\*]+)\*\*|\*([^\*]+)\*")

    def result(self, match: re.Match) -> str:
        """Convert to SSML emphasis element.

        Args:
            match: Regex match object

        Returns:
            SSML <emphasis> tag with appropriate level
        """
        # Group 1 is **text**, group 2 is *text*
        if match.group(1):  # Strong emphasis **text**
            text = match.group(1)
            return f'<emphasis level="strong">{text}</emphasis>'
        else:  # Moderate emphasis *text*
            text = match.group(2)
            return f"<emphasis>{text}</emphasis>"

    def text(self, match: re.Match) -> str:
        """Extract plain text without asterisks.

        Args:
            match: Regex match object

        Returns:
            Plain text content
        """
        # Return whichever group matched
        return match.group(1) if match.group(1) else match.group(2)
