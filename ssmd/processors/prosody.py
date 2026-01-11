"""Prosody shorthand processor: ++loud++, >>fast>>, ^^high^^"""

import re

from ssmd.processors.base import BaseProcessor


class ProsodyProcessor(BaseProcessor):
    """Process prosody shorthand markup.

    Supports:
    - Volume: ~silent~, --x-soft--, -soft-, +loud+, ++x-loud++
    - Rate: <<x-slow<<, <slow<, >fast>, >>x-fast>>
    - Pitch: __x-low__, _low_, ^high^, ^^x-high^^
    """

    name = "prosody"

    # Mapping from markers to SSML values
    VOLUME_MAP = {
        "~": "silent",
        "--": "x-soft",
        "-": "soft",
        "+": "loud",
        "++": "x-loud",
    }

    RATE_MAP = {
        "&lt;&lt;": "x-slow",  # << (XML escaped)
        "&lt;": "slow",  # <
        "&gt;": "fast",  # >
        "&gt;&gt;": "x-fast",  # >>
    }

    PITCH_MAP = {
        "__": "x-low",
        "_": "low",
        "^": "high",
        "^^": "x-high",
    }

    def regex(self) -> re.Pattern:
        """Match prosody shorthand patterns.

        Note: Uses XML-escaped entities for < and > since
        we process after XML escaping.

        Returns:
            Pattern matching all prosody shortcuts
        """
        # Combine all patterns (order matters: longer patterns first!)
        # Must not be preceded/followed by alphanumeric to avoid matching
        # hyphens in words/numbers like "555-1234" or "say-as"
        return re.compile(
            r"(?<![a-zA-Z0-9])"  # Not preceded by alphanumeric
            r"(~~|--|\+\+|-|\+|"  # Volume
            r"&lt;&lt;|&lt;|&gt;&gt;|&gt;|"  # Rate (XML escaped)
            r"__|\^\^|_|\^)"  # Pitch
            r"([^~\-+<>_^]+?)"  # Content (non-greedy)
            r"\1"  # Same closing marker
            r"(?![a-zA-Z0-9])"  # Not followed by alphanumeric
        )

    def result(self, match: re.Match) -> str:
        """Convert to SSML prosody element.

        Args:
            match: Regex match object

        Returns:
            SSML <prosody> tag
        """
        marker = match.group(1)
        text = match.group(2)

        # Determine attribute and value
        attr = None
        value = None

        if marker in self.VOLUME_MAP:
            attr = "volume"
            value = self.VOLUME_MAP[marker]
        elif marker in self.RATE_MAP:
            attr = "rate"
            value = self.RATE_MAP[marker]
        elif marker in self.PITCH_MAP:
            attr = "pitch"
            value = self.PITCH_MAP[marker]

        if attr and value:
            return f'<prosody {attr}="{value}">{text}</prosody>'

        return match.group(0)  # Return unchanged if no match

    def substitute(self, text: str) -> str:
        """Replace SSMD with SSML, skipping matches inside XML attributes.

        Args:
            text: Input text with SSMD markup

        Returns:
            Text with SSMD replaced by SSML
        """
        match = self.regex().search(text)
        if not match:
            return text

        # Check if match is inside an XML attribute (between =" and ")
        # by looking backwards from match start to find if we're in an attribute
        pre_text = text[: match.start()]

        # Count unmatched quotes in attribute context
        # Find the last < before our position
        last_tag_start = pre_text.rfind("<")
        if last_tag_start != -1:
            # Get text between last < and our match
            between = pre_text[last_tag_start:]
            # Check if we're inside an attribute by counting unmatched quotes
            # after an = sign
            in_attr = False
            i = 0
            while i < len(between):
                if between[i] == "=" and i + 1 < len(between) and between[i + 1] == '"':
                    # Start of attribute value
                    in_attr = True
                    i += 2
                elif in_attr and between[i] == '"':
                    # End of attribute value
                    in_attr = False
                    i += 1
                else:
                    i += 1

            if in_attr:
                # We're inside an XML attribute, skip this match
                # Try to find next match after this one
                post = text[match.end() :]
                return text[: match.end()] + self.substitute(post)

        # Not in attribute, proceed with normal substitution
        pre = text[: match.start()]
        post = text[match.end() :]
        ssml_result = self.result(match)

        return pre + ssml_result + post

    def text(self, match: re.Match) -> str:
        """Extract plain text without markers.

        Args:
            match: Regex match object

        Returns:
            Plain text content
        """
        return match.group(2)
