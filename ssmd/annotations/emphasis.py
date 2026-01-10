"""Emphasis annotation: [text](emphasis: level) → <emphasis>text</emphasis>"""

import re

from ssmd.annotations.base import BaseAnnotation


class EmphasisAnnotation(BaseAnnotation):
    """Process explicit emphasis annotations.

    Examples:
        [text](emphasis: none) → <emphasis level="none">text</emphasis>
        [text](emphasis: reduced) → <emphasis level="reduced">text</emphasis>
        [text](emphasis: moderate) → <emphasis>text</emphasis>
        [text](emphasis: strong) → <emphasis level="strong">text</emphasis>

    Note: This is for explicit emphasis levels. Most cases use shorthand:
        *text* for moderate, **text** for strong, _text_ for reduced
    """

    VALID_LEVELS = {"none", "reduced", "moderate", "strong"}

    def __init__(self, match: re.Match):
        """Initialize with emphasis level.

        Args:
            match: Regex match containing emphasis level
        """
        self.level = match.group(1).strip().lower()

        # Validate level
        if self.level not in self.VALID_LEVELS:
            # Default to moderate if invalid
            self.level = "moderate"

    @classmethod
    def regex(cls) -> re.Pattern:
        """Match emphasis annotations.

        Returns:
            Pattern matching emphasis: level
        """
        return re.compile(
            r"^emphasis:\s*(none|reduced|moderate|strong)$", re.IGNORECASE
        )

    def wrap(self, text: str) -> str:
        """Wrap text in emphasis tag.

        Args:
            text: Content to wrap

        Returns:
            SSML <emphasis> element
        """
        if self.level == "moderate":
            # Default level - no level attribute needed
            return f"<emphasis>{text}</emphasis>"
        else:
            return f'<emphasis level="{self.level}">{text}</emphasis>'
