"""Audio annotation: [desc](url.mp3 alt) → <audio>desc</audio>"""

import re

from ssmd.annotations.base import BaseAnnotation


class AudioAnnotation(BaseAnnotation):
    """Process audio file annotations.

    Examples:
        Basic:
            [boing](https://example.com/sounds/boing.mp3) →
                <audio src="..."><desc>boing</desc></audio>
            [purr](cat.ogg Sound didn't load) →
                <audio src="cat.ogg"><desc>purr</desc>Sound didn't load</audio>
            [](miaou.mp3) → <audio src="miaou.mp3"></audio>

        Advanced attributes:
            [music](song.mp3 clip: 0s-10s) →
                <audio src="song.mp3" clipBegin="0s" clipEnd="10s">
                <desc>music</desc></audio>
            [fast](speech.mp3 speed: 150%) →
                <audio src="speech.mp3" speed="150%"><desc>fast</desc></audio>
            [jingle](ad.mp3 repeat: 3) →
                <audio src="ad.mp3" repeatCount="3"><desc>jingle</desc></audio>
            [alarm](alert.mp3 level: +6dB) →
                <audio src="alert.mp3" soundLevel="+6dB"><desc>alarm</desc></audio>
            [bg](music.mp3 clip: 5s-30s, speed: 120%, level: -3dB Fallback text) →
                <audio ... ><desc>bg</desc>Fallback text</audio>
    """

    def __init__(self, match: re.Match):
        """Initialize with URL and optional attributes/alt text.

        Args:
            match: Regex match containing URL, attributes, and alt text
        """
        self.url = match.group(1).strip()
        attrs_and_alt = match.group(2).strip() if match.group(2) else ""

        # Parse attributes and alt text
        # Attributes come first, alt text comes after
        self.clip_begin = None
        self.clip_end = None
        self.speed = None
        self.repeat_count = None
        self.sound_level = None
        self.alt_text = ""

        if attrs_and_alt:
            # Split by comma to find individual attributes
            # But be careful: alt text might contain commas!
            # Strategy: parse known attribute patterns first, rest is alt text
            remaining = attrs_and_alt

            # Parse clip: 0s-10s or clip: 5s-30s
            clip_match = re.search(
                r"clip:\s*(\d+(?:\.\d+)?[ms])-(\d+(?:\.\d+)?[ms])", remaining
            )
            if clip_match:
                self.clip_begin = clip_match.group(1)
                self.clip_end = clip_match.group(2)
                remaining = (
                    remaining[: clip_match.start()] + remaining[clip_match.end() :]
                )

            # Parse speed: 150%
            speed_match = re.search(r"speed:\s*(\d+(?:\.\d+)?%)", remaining)
            if speed_match:
                self.speed = speed_match.group(1)
                remaining = (
                    remaining[: speed_match.start()] + remaining[speed_match.end() :]
                )

            # Parse repeat: 3 or repeat: 2
            repeat_match = re.search(r"repeat:\s*(\d+)", remaining)
            if repeat_match:
                self.repeat_count = repeat_match.group(1)
                remaining = (
                    remaining[: repeat_match.start()] + remaining[repeat_match.end() :]
                )

            # Parse level: +6dB or level: -3dB
            level_match = re.search(r"level:\s*([+-]?\d+(?:\.\d+)?dB)", remaining)
            if level_match:
                self.sound_level = level_match.group(1)
                remaining = (
                    remaining[: level_match.start()] + remaining[level_match.end() :]
                )

            # Clean up remaining text (remove commas, extra spaces)
            remaining = re.sub(
                r"^[,\s]+|[,\s]+$", "", remaining
            )  # Strip leading/trailing
            remaining = re.sub(
                r"\s*,\s*,\s*", ", ", remaining
            )  # Collapse double commas
            remaining = re.sub(
                r"^,\s*|,\s*$", "", remaining
            )  # Strip leading/trailing commas

            # What's left is alt text
            self.alt_text = remaining.strip()

    @classmethod
    def regex(cls) -> re.Pattern:
        """Match audio file URLs with optional attributes.

        Returns:
            Pattern matching audio file extensions with optional attributes and alt text
        """
        # Match URL (anything starting with http/https or ending in audio extension)
        # Followed by optional attributes/alt text
        return re.compile(
            r"^((?:https?://)?[^\s]+\.(?:mp3|ogg|wav|m4a|aac|flac))(?:\s+(.+))?$",
            re.IGNORECASE,
        )

    def wrap(self, text: str) -> str:
        """Wrap in audio tag with description, attributes, and alt text.

        Args:
            text: Description text (used in <desc>)

        Returns:
            SSML <audio> element
        """
        # Build attributes
        attrs = [f'src="{self.url}"']

        if self.clip_begin:
            attrs.append(f'clipBegin="{self.clip_begin}"')
        if self.clip_end:
            attrs.append(f'clipEnd="{self.clip_end}"')
        if self.speed:
            attrs.append(f'speed="{self.speed}"')
        if self.repeat_count:
            attrs.append(f'repeatCount="{self.repeat_count}"')
        if self.sound_level:
            attrs.append(f'soundLevel="{self.sound_level}"')

        attrs_str = " ".join(attrs)

        # Build content
        desc = f"<desc>{text}</desc>" if text else ""

        return f"<audio {attrs_str}>{desc}{self.alt_text}</audio>"
