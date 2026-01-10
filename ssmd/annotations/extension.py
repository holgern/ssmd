"""Extension annotation: [text](ext: whisper) → platform-specific SSML"""

import re
from collections.abc import Callable

from ssmd.annotations.base import BaseAnnotation


class ExtensionAnnotation(BaseAnnotation):
    """Process platform-specific extension annotations.

    Examples:
        [whispers](ext: whisper) →
            <amazon:effect name="whispered">whispers</amazon:effect>
        [url](ext: audio) → <audio src="url"/>

    Extensions can be registered via config['extensions'].
    """

    # Built-in extensions
    DEFAULT_EXTENSIONS: dict[str, Callable[[str], str]] = {
        "whisper": lambda text: (
            f'<amazon:effect name="whispered">{text}</amazon:effect>'
        ),
        "audio": lambda text: f'<audio src="{text}"/>',
    }

    def __init__(
        self, match: re.Match, custom_extensions: dict[str, Callable] | None = None
    ):
        """Initialize with extension name.

        Args:
            match: Regex match containing extension name
            custom_extensions: Optional custom extension handlers
        """
        self.extension_name = match.group(1).strip()
        self.extensions = {**self.DEFAULT_EXTENSIONS, **(custom_extensions or {})}

    @classmethod
    def regex(cls) -> re.Pattern:
        """Match extension annotations.

        Returns:
            Pattern matching ext: annotations
        """
        return re.compile(r"^ext:\s*(\w+)$")

    @classmethod
    def try_create(cls, annotation_str: str):
        """Try to create annotation with custom extensions from config.

        Note: This override is needed to pass custom extensions from config.
        In practice, the AnnotationProcessor should handle this.

        Args:
            annotation_str: Annotation string

        Returns:
            ExtensionAnnotation instance or None
        """
        match = cls.regex().match(annotation_str.strip())
        if match:
            return cls(match)
        return None

    def wrap(self, text: str) -> str:
        """Wrap text using extension handler.

        Args:
            text: Content to wrap

        Returns:
            Platform-specific SSML
        """
        handler = self.extensions.get(self.extension_name)
        if handler:
            return handler(text)

        # Unknown extension, return unchanged
        return text
