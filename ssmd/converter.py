"""Main SSMD to SSML conversion engine."""

from typing import TYPE_CHECKING, Any

from ssmd.processors import get_all_processors
from ssmd.utils import escape_xml, format_xml, unescape_xml

if TYPE_CHECKING:
    from ssmd.processors.base import BaseProcessor


class Converter:
    """Main SSMD to SSML conversion engine using processor pipeline.

    The converter applies a series of processors to transform SSMD
    markup into SSML. Each processor is applied recursively until
    no more matches are found.
    """

    def __init__(self, config: dict[str, Any]):
        """Initialize converter with configuration.

        Args:
            config: Configuration dictionary with options:
                - skip: List of processor names to skip
                - output_speak_tag: Wrap output in <speak> tags (default: True)
                - pretty_print: Format XML output (default: False)
                - auto_sentence_tags: Auto-wrap sentences in <s> (default: False)
                - heading_levels: Custom heading configurations
                - extensions: Registered extension handlers
        """
        self.config = config
        self.processors = self._init_processors()

    def _init_processors(self) -> list:
        """Initialize processor pipeline in correct order.

        Returns:
            List of processor instances
        """
        skip = self.config.get("skip", [])
        all_processors = get_all_processors(self.config)
        return [p for p in all_processors if p.name not in skip]

    def convert(self, ssmd_text: str) -> str:
        """Convert SSMD to SSML.

        Args:
            ssmd_text: Input SSMD markdown text

        Returns:
            SSML output string
        """
        # 1. Escape XML special characters
        result = escape_xml(ssmd_text)

        # 2. Apply each processor recursively
        for processor in self.processors:
            result = self._process_recursively(processor, result, strip=False)

        # 3. Unescape XML entities in final SSML
        result = unescape_xml(result)

        # 4. Wrap in <speak> tags if configured
        if self.config.get("output_speak_tag", True):
            result = f"<speak>{result}</speak>"

        # 5. Pretty print if configured
        if self.config.get("pretty_print", False):
            result = format_xml(result, pretty=True)

        return result

    def strip(self, ssmd_text: str) -> str:
        """Strip SSMD annotations, returning plain text.

        Args:
            ssmd_text: Input SSMD markdown text

        Returns:
            Plain text with all markup removed
        """
        result = escape_xml(ssmd_text)

        for processor in self.processors:
            result = self._process_recursively(processor, result, strip=True)

        return unescape_xml(result)

    def _process_recursively(
        self, processor: "BaseProcessor", text: str, strip: bool
    ) -> str:
        """Apply processor recursively until no more matches.

        Args:
            processor: Processor instance to apply
            text: Current text state
            strip: If True, strip markup; if False, convert to SSML

        Returns:
            Processed text
        """
        # Check if processor has overridden methods to avoid recursion
        # (e.g., ParagraphProcessor replaces all at once)
        if hasattr(processor, "_process_all_at_once"):
            if strip:
                return processor.strip_ssmd(text)
            else:
                return processor.substitute(text)

        # Standard recursive processing
        if processor.matches(text):
            result = processor.strip_ssmd(text) if strip else processor.substitute(text)
            # Only recurse if the text actually changed
            if result != text:
                return self._process_recursively(processor, result, strip)
        return text
