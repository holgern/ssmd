"""Base processor class for SSMD conversion."""

import re
from abc import ABC, abstractmethod
from typing import Any


class BaseProcessor(ABC):
    """Abstract base class for all SSMD processors.

    A processor is responsible for matching a specific SSMD pattern
    and converting it to SSML or stripping it for plain text.
    """

    name: str = "base"

    def __init__(self, config: dict[str, Any]):
        """Initialize processor with configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config

    @abstractmethod
    def regex(self) -> re.Pattern:
        """Return the regex pattern for matching.

        Returns:
            Compiled regex pattern
        """
        pass

    @abstractmethod
    def result(self, match: re.Match) -> str:
        """Generate SSML output from match.

        Args:
            match: Regex match object

        Returns:
            SSML string
        """
        pass

    def matches(self, text: str) -> bool:
        """Check if the pattern matches the text.

        Args:
            text: Input text to check

        Returns:
            True if pattern matches
        """
        return self.regex().search(text) is not None

    def substitute(self, text: str) -> str:
        """Replace SSMD with SSML.

        Args:
            text: Input text with SSMD markup

        Returns:
            Text with SSMD replaced by SSML
        """
        match = self.regex().search(text)
        if not match:
            return text

        pre = text[: match.start()]
        post = text[match.end() :]
        ssml_result = self.result(match)

        return pre + ssml_result + post

    def strip_ssmd(self, text: str) -> str:
        """Remove SSMD annotations, keep text.

        Args:
            text: Input text with SSMD markup

        Returns:
            Plain text with markup removed
        """
        match = self.regex().search(text)
        if not match:
            return text

        pre = text[: match.start()]
        post = text[match.end() :]
        plain_text = self.text(match)

        # Handle whitespace for no-content markers
        if self.is_no_content():
            # Remove one adjacent space
            if pre and pre.endswith(" "):
                pre = pre[:-1]
            elif post and post.startswith(" "):
                post = post[1:]

        return pre + plain_text + post

    def text(self, match: re.Match) -> str:
        """Extract plain text from match.

        Override this method to customize text extraction.

        Args:
            match: Regex match object

        Returns:
            Plain text content
        """
        return match.group(1) if match.groups() else match.group(0)

    def is_no_content(self) -> bool:
        """Check if this processor produces no content output.

        Override to True for markers like @mark and ...0 that should
        not leave extra whitespace when stripped.

        Returns:
            True if processor has no content
        """
        return False
