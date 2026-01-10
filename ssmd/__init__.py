"""SSMD - Speech Synthesis Markdown to SSML converter.

SSMD provides a lightweight markdown-like syntax for creating SSML
(Speech Synthesis Markup Language) documents. It's designed to be
more human-friendly than raw SSML while maintaining full compatibility.

Example:
    Basic usage::

        import ssmd

        # Convert SSMD to SSML
        ssml = ssmd.to_ssml("Hello *world*!")
        # Output: <speak>Hello <emphasis>world</emphasis>!</speak>

        # Strip SSMD markup for plain text
        plain = ssmd.strip_ssmd("Hello *world* @marker!")
        # Output: Hello world!

    Advanced usage with configuration::

        # Create parser with custom config
        parser = ssmd.SSMD({
            'auto_sentence_tags': True,
            'pretty_print': True
        })

        # Convert to SSML
        ssml = parser.to_ssml("# Hello\\nThis is a test.")

        # Load document for sentence-by-sentence TTS
        doc = parser.load("Long document here...")
        for sentence in doc:
            # tts_engine.speak(sentence)
            pass
"""

from typing import Any, Optional
from collections.abc import Iterator

from ssmd.converter import Converter
from ssmd.document import SSMDDocument

try:
    from ssmd._version import version as __version__
except ImportError:
    __version__ = "unknown"


class SSMD:
    """Main SSMD converter class with TTS streaming support.

    This class provides both traditional conversion (SSMD -> SSML)
    and streaming capabilities for TTS applications that process
    text sentence-by-sentence.

    Attributes:
        config: Configuration dictionary
        converter: Internal converter instance
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize SSMD converter with optional configuration.

        Args:
            config: Configuration options:
                - skip (list): Processor names to skip
                - output_speak_tag (bool): Wrap in <speak> tags (default: True)
                - pretty_print (bool): Format XML output (default: False)
                - auto_sentence_tags (bool): Auto-wrap sentences in <s> (default: False)
                - heading_levels (dict): Custom heading configurations
                - extensions (dict): Registered extension handlers

        Example:
            >>> parser = SSMD({
            ...     'auto_sentence_tags': True,
            ...     'heading_levels': {
            ...         1: [('emphasis', 'strong'), ('pause', '300ms')]
            ...     }
            ... })
        """
        self.config = config or {}
        self.converter = Converter(self.config)

    def to_ssml(self, ssmd_text: str) -> str:
        """Convert SSMD markdown to SSML.

        Args:
            ssmd_text: SSMD markdown text

        Returns:
            SSML string

        Example:
            >>> parser = SSMD()
            >>> parser.to_ssml("Hello *world*!")
            '<speak>Hello <emphasis>world</emphasis>!</speak>'
        """
        return self.converter.convert(ssmd_text)

    def strip(self, ssmd_text: str) -> str:
        """Remove SSMD annotations, returning plain text.

        Args:
            ssmd_text: SSMD markdown text

        Returns:
            Plain text with markup removed

        Example:
            >>> parser = SSMD()
            >>> parser.strip("Hello *world* @marker!")
            'Hello world!'
        """
        return self.converter.strip(ssmd_text)

    def load(self, ssmd_text: str) -> SSMDDocument:
        """Load SSMD document for sentence-by-sentence processing.

        This is useful for TTS applications that need to process
        long documents incrementally.

        Args:
            ssmd_text: SSMD markdown text

        Returns:
            SSMDDocument instance that can be iterated

        Example:
            >>> parser = SSMD({'auto_sentence_tags': True})
            >>> doc = parser.load("Hello!\\nWorld!")
            >>> for sentence in doc:
            ...     print(sentence)
            ...     # tts_engine.speak(sentence)
        """
        return SSMDDocument(ssmd_text, self.converter)

    def sentences(self, ssmd_text: str) -> Iterator[str]:
        """Generator yielding SSML sentences one at a time.

        Convenience method that combines load() and iteration.

        Args:
            ssmd_text: SSMD markdown text

        Yields:
            SSML sentence strings

        Example:
            >>> parser = SSMD()
            >>> for sentence in parser.sentences("Hello!\\nWorld!"):
            ...     print(sentence)
        """
        doc = self.load(ssmd_text)
        yield from doc.sentences()


# Convenience functions for simple use cases
def to_ssml(ssmd_text: str, **config) -> str:
    """Convert SSMD to SSML (convenience function).

    Args:
        ssmd_text: SSMD markdown text
        **config: Optional configuration parameters

    Returns:
        SSML string

    Example:
        >>> ssmd.to_ssml("Hello *world*!")
        '<speak>Hello <emphasis>world</emphasis>!</speak>'
    """
    return SSMD(config).to_ssml(ssmd_text)


def strip_ssmd(ssmd_text: str, **config) -> str:
    """Strip SSMD annotations (convenience function).

    Args:
        ssmd_text: SSMD markdown text
        **config: Optional configuration parameters

    Returns:
        Plain text with markup removed

    Example:
        >>> ssmd.strip_ssmd("Hello *world* @marker!")
        'Hello world!'
    """
    return SSMD(config).strip(ssmd_text)


__all__ = [
    "SSMD",
    "SSMDDocument",
    "to_ssml",
    "strip_ssmd",
    "__version__",
]
