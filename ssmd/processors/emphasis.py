"""Emphasis processor: *text* → <emphasis>text</emphasis>"""

import re

from ssmd.processors.base import BaseProcessor


class EmphasisProcessor(BaseProcessor):
    """Process emphasis markup.

    Supports:
    - **text** for strong emphasis
    - *text* for moderate emphasis (default)
    - _text_ for reduced emphasis
    """

    name = "emphasis"

    def regex(self) -> re.Pattern:
        """Match text wrapped in asterisks or underscores.

        Matches:
        - **text** for strong emphasis
        - *text* for moderate emphasis
        - _text_ for reduced emphasis

        Returns:
            Pattern matching emphasis patterns
        """
        # Match in order: ** (strong), * (moderate), _ (reduced)
        # Need to avoid matching __ (pitch) or ___ patterns
        # Use negative lookahead/lookbehind to prevent double underscores
        return re.compile(
            r"\*\*([^\*]+)\*\*|"  # **strong**
            r"\*([^\*]+)\*|"  # *moderate*
            r"(?<!_)_(?!_)([^_]+?)(?<!_)_(?!_)"  # _reduced_ (not __ or ___)
        )

    def result(self, match: re.Match) -> str:
        """Convert to SSML emphasis element.

        Args:
            match: Regex match object

        Returns:
            SSML <emphasis> tag with appropriate level
        """
        # Group 1 is **text**, group 2 is *text*, group 3 is _text_
        if match.group(1):  # Strong emphasis **text**
            text = match.group(1)
            return f'<emphasis level="strong">{text}</emphasis>'
        elif match.group(2):  # Moderate emphasis *text*
            text = match.group(2)
            return f"<emphasis>{text}</emphasis>"
        else:  # Reduced emphasis _text_
            text = match.group(3)
            return f'<emphasis level="reduced">{text}</emphasis>'

    def text(self, match: re.Match) -> str:
        """Extract plain text without markers.

        Args:
            match: Regex match object

        Returns:
            Plain text content
        """
        # Return whichever group matched
        return match.group(1) or match.group(2) or match.group(3)
