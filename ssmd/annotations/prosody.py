"""Prosody annotation: [text](vrp: 555) → <prosody>text</prosody>"""

import re

from ssmd.annotations.base import BaseAnnotation


class ProsodyAnnotation(BaseAnnotation):
    """Process prosody annotations.

    Supports:
        [text](vrp: 555) → <prosody volume="x-loud" rate="x-fast" pitch="x-high">
        [text](v: 5, r: 3, p: 1) → <prosody volume="x-loud" rate="medium" pitch="x-low">
        [text](v: +10dB) → <prosody volume="+10dB">
        [text](p: -4%) → <prosody pitch="-4%">
    """

    # Mapping from numeric values to SSML values
    VOLUME_MAP = {
        "0": "silent",
        "1": "x-soft",
        "2": "soft",
        "3": "medium",
        "4": "loud",
        "5": "x-loud",
    }

    RATE_MAP = {
        "1": "x-slow",
        "2": "slow",
        "3": "medium",
        "4": "fast",
        "5": "x-fast",
    }

    PITCH_MAP = {
        "1": "x-low",
        "2": "low",
        "3": "medium",
        "4": "high",
        "5": "x-high",
    }

    def __init__(self, match: re.Match):
        """Initialize with prosody values.

        Args:
            match: Regex match containing prosody parameters
        """
        self.volume: str | None = None
        self.rate: str | None = None
        self.pitch: str | None = None

        # Check if it's VRP shorthand (vrp: 555)
        vrp = match.group(1)
        if vrp:
            self.volume = self.VOLUME_MAP.get(vrp[0])
            self.rate = self.RATE_MAP.get(vrp[1]) if len(vrp) > 1 else None
            self.pitch = self.PITCH_MAP.get(vrp[2]) if len(vrp) > 2 else None
        else:
            # Individual parameters (v: 5, r: 3, p: 1 or volume: loud, etc.)
            attr = match.group(2)  # v, r, p, volume, rate, or pitch
            value = match.group(3).strip()

            # Normalize attribute name to short form
            if attr == "volume":
                attr = "v"
            elif attr == "rate":
                attr = "r"
            elif attr == "pitch":
                attr = "p"

            # Check if it's a relative value (+10dB, -4%)
            if value.startswith(("+", "-")) or value.endswith(("dB", "%")):
                # Relative value, use as-is
                if attr == "v":
                    self.volume = value
                elif attr == "r":
                    self.rate = value
                elif attr == "p":
                    self.pitch = value
            else:
                # Could be numeric value (map to SSML) or named value (use as-is)
                if attr == "v":
                    self.volume = self.VOLUME_MAP.get(value, value)
                elif attr == "r":
                    self.rate = self.RATE_MAP.get(value, value)
                elif attr == "p":
                    self.pitch = self.PITCH_MAP.get(value, value)

    @classmethod
    def regex(cls) -> re.Pattern:
        """Match prosody annotations.

        Returns:
            Pattern matching vrp shorthand, individual parameters (v/r/p),
            or full names (volume/rate/pitch)
        """
        # Match either:
        # - "vrp: 555"
        # - "v: 5" or "r: 3" or "p: 1"
        # - "volume: loud" or "rate: fast" or "pitch: high"
        return re.compile(r"^(?:vrp:\s*(\d{1,3})|([vrp]|volume|rate|pitch):\s*(.+))$")

    def wrap(self, text: str) -> str:
        """Wrap text in prosody tag.

        Args:
            text: Content to wrap

        Returns:
            SSML <prosody> element
        """
        attrs = []
        if self.volume:
            attrs.append(f'volume="{self.volume}"')
        if self.rate:
            attrs.append(f'rate="{self.rate}"')
        if self.pitch:
            attrs.append(f'pitch="{self.pitch}"')

        if attrs:
            attrs_str = " ".join(attrs)
            return f"<prosody {attrs_str}>{text}</prosody>"

        return text  # No valid attributes, return unchanged

    def combine(self, other: "BaseAnnotation") -> None:
        """Combine with another prosody annotation (first wins).

        Args:
            other: Another prosody annotation
        """
        if not isinstance(other, ProsodyAnnotation):
            return

        # Keep existing values, don't overwrite
        if self.volume is None:
            self.volume = other.volume
        if self.rate is None:
            self.rate = other.rate
        if self.pitch is None:
            self.pitch = other.pitch
