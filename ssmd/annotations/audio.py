"""Audio annotation: [desc](url.mp3 alt) → <audio>desc</audio>"""

import re

from ssmd.annotations.base import BaseAnnotation


class AudioAnnotation(BaseAnnotation):
    """Process audio file annotations.

    Examples:
        [boing](https://example.com/sounds/boing.mp3) → <audio src="..."><desc>boing</desc></audio>
        [purr](cat.ogg Sound didn't load) → <audio src="cat.ogg"><desc>purr</desc>Sound didn't load</audio>
        [](miaou.mp3) → <audio src="miaou.mp3"></audio>
    """

    def __init__(self, match: re.Match):
        """Initialize with URL and optional alt text.

        Args:
            match: Regex match containing URL and alt text
        """
        self.url = match.group(1).strip()
        self.alt_text = match.group(2).strip() if match.group(2) else ""

    @classmethod
    def regex(cls) -> re.Pattern:
        """Match audio file URLs.

        Returns:
            Pattern matching audio file extensions with optional alt text
        """
        # Match URL (anything starting with http/https or ending in audio extension)
        # Followed by optional alt text
        return re.compile(
            r"^((?:https?://)?[^\s]+\.(?:mp3|ogg|wav|m4a|aac|flac))(?:\s+(.+))?$",
            re.IGNORECASE,
        )

    def wrap(self, text: str) -> str:
        """Wrap in audio tag with description and alt text.

        Args:
            text: Description text (used in <desc>)

        Returns:
            SSML <audio> element
        """
        desc = f"<desc>{text}</desc>" if text else ""
        return f'<audio src="{self.url}">{desc}{self.alt_text}</audio>'
