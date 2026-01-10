"""Heading processor: # text → <emphasis>text</emphasis> <break/>"""

import re
from typing import Any

from ssmd.processors.base import BaseProcessor


class HeadingProcessor(BaseProcessor):
    """Process markdown-style headings (# ## ###).

    By default:
    - # Heading 1 → strong emphasis + 100ms pause
    - ## Heading 2 → moderate emphasis + 75ms pause
    - ### Heading 3 → reduced emphasis + 50ms pause

    Can be customized via config['heading_levels'].
    """

    name = "heading"

    DEFAULT_LEVELS = {
        1: [("emphasis", "strong"), ("pause", "100ms")],
        2: [("emphasis", "moderate"), ("pause", "75ms")],
        3: [("emphasis", "reduced"), ("pause", "50ms")],
    }

    def __init__(self, config: dict[str, Any]):
        """Initialize with custom heading configurations.

        Args:
            config: Configuration dict with optional 'heading_levels'
        """
        super().__init__(config)
        self.heading_levels = config.get("heading_levels", self.DEFAULT_LEVELS)

    def regex(self) -> re.Pattern:
        """Match heading patterns at start of line.

        Returns:
            Pattern matching # text
        """
        return re.compile(r"^\s*(#+)\s*(.+)", re.MULTILINE)

    def result(self, match: re.Match) -> str:
        """Convert to SSML with emphasis and breaks.

        Args:
            match: Regex match object

        Returns:
            SSML with heading styling
        """
        level = len(match.group(1))
        text = match.group(2)

        if level not in self.heading_levels:
            # No config for this level, return unchanged
            return match.group(0)

        # Apply each tag in sequence
        result = text
        for tag, value in self.heading_levels[level]:
            if tag == "emphasis":
                result = f'<emphasis level="{value}">{result}</emphasis>'
            elif tag == "pause":
                result = f'{result} <break time="{value}"/>'
            elif tag == "prosody":
                # value is dict like {rate: 'slow'}
                if isinstance(value, dict):
                    attrs = " ".join(f'{k}="{v}"' for k, v in value.items())
                    result = f"<prosody {attrs}>{result}</prosody>"

        return result

    def text(self, match: re.Match) -> str:
        """Extract heading text without # markers.

        Args:
            match: Regex match object

        Returns:
            Heading text
        """
        return match.group(2)
