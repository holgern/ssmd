"""Sentence processor: Auto-wrap sentences in <s> tags"""

import re
from typing import Any

from ssmd.processors.base import BaseProcessor


class SentenceProcessor(BaseProcessor):
    """Automatically wrap sentences in <s> tags.

    This processor is optional and controlled by the
    'auto_sentence_tags' configuration option.
    """

    name = "sentence"

    def __init__(self, config: dict[str, Any]):
        """Initialize with configuration.

        Args:
            config: Configuration dict with optional 'auto_sentence_tags'
        """
        super().__init__(config)
        self.enabled = config.get("auto_sentence_tags", False)

    def regex(self) -> re.Pattern:
        """Match lines within paragraphs.

        Returns:
            Pattern matching sentence boundaries
        """
        # Match text within <p> tags followed by newline
        return re.compile(r"<p>([^<>]+)(?:\n([^<>\n]+))*</p>")

    def result(self, match: re.Match) -> str:
        """Wrap each line in <s> tags.

        Args:
            match: Regex match object

        Returns:
            SSML with sentences wrapped
        """
        if not self.enabled:
            return match.group(0)

        # Get the content between <p> tags
        content = match.group(0)[3:-4]  # Remove <p> and </p>

        # Split by newlines and wrap each in <s>
        lines = content.split("\n")
        sentences = [f"<s>{line.strip()}</s>" for line in lines if line.strip()]

        return f"<p>{' '.join(sentences)}</p>"

    def matches(self, text: str) -> bool:
        """Only match if enabled.

        Args:
            text: Input text

        Returns:
            True if enabled and pattern matches
        """
        if not self.enabled:
            return False
        return super().matches(text)

    def text(self, match: re.Match) -> str:
        """Extract plain text unchanged.

        Args:
            match: Regex match object

        Returns:
            Original content
        """
        return match.group(0)
