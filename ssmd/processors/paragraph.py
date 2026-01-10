"""Paragraph processor: \\n\\n → <p>...</p>"""

import re

from ssmd.processors.base import BaseProcessor


class ParagraphProcessor(BaseProcessor):
    """Process paragraph breaks (double newlines)."""

    name = "paragraph"

    # Flag to tell converter not to process recursively
    _process_all_at_once = True

    def regex(self) -> re.Pattern:
        """Match double newlines (paragraph breaks).

        Returns:
            Pattern matching two or more newlines
        """
        return re.compile(r"\n\n+")

    def result(self, match: re.Match) -> str:
        """Convert to paragraph boundaries.

        Args:
            match: Regex match object

        Returns:
            Paragraph closing and opening tags
        """
        return "</p><p>"

    def text(self, match: re.Match) -> str:
        """Keep paragraph breaks in plain text.

        Args:
            match: Regex match object

        Returns:
            Double newline
        """
        return "\n\n"

    def substitute(self, text: str) -> str:
        """Replace paragraph breaks and wrap in <p> tags.

        Overridden to handle wrapping the entire text in <p> tags.

        Args:
            text: Input text

        Returns:
            Text with paragraphs wrapped in <p> tags
        """
        # First, replace all double newlines with </p><p>
        result = self.regex().sub("</p><p>", text)

        # Then wrap the entire result in <p>...</p>
        if result and not result.startswith("<p>"):
            result = "<p>" + result
        if result and not result.endswith("</p>"):
            result = result + "</p>"

        return result

    def strip_ssmd(self, text: str) -> str:
        """Keep paragraph breaks in plain text.

        Overridden to avoid infinite recursion by replacing all at once.

        Args:
            text: Input text with paragraph breaks

        Returns:
            Text with paragraph breaks preserved
        """
        # Just replace all double+ newlines with double newlines (normalize)
        return self.regex().sub("\n\n", text)
