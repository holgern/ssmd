"""Voice directive processor: @voice: name → <voice>text</voice>"""

import re

from ssmd.processors.base import BaseProcessor


class VoiceDirectiveProcessor(BaseProcessor):
    """Process voice directive blocks (@voice: name or @voice(name)).

    The directive applies to text on the same line and/or following lines
    until another voice directive or paragraph break.

    Examples:
        @voice: Joanna
        Hello from Joanna!

        @voice(am_michael)
        And this is Michael speaking.

        @voice: af_sarah
        Back to Sarah. This can span
        multiple lines in the same paragraph.
    """

    name = "voice_directive"

    def regex(self) -> re.Pattern:
        """Match @voice: name or @voice(name) at start of line.

        Returns:
            Pattern matching voice directive
        """
        # Match @voice: name or @voice(name) followed by content until:
        # - Double newline (paragraph break)
        # - Another @voice directive
        # - End of string
        return re.compile(
            r"^@voice(?::\s*|\()([a-zA-Z0-9_-]+)\)?\s*\n((?:(?!^@voice)(?:.*\n?))+?)(?=\n\n|^@voice|\Z)",
            re.MULTILINE,
        )

    def result(self, match: re.Match) -> str:
        """Convert to SSML voice element.

        Args:
            match: Regex match object

        Returns:
            SSML <voice> tag wrapping the content
        """
        capabilities = self.config.get("capabilities")
        if capabilities and not getattr(capabilities, "voice", True):
            # Voice not supported, return plain text
            content = match.group(2)
            # Preserve trailing newlines for paragraph breaks
            trailing_newlines = len(content) - len(content.rstrip("\n"))
            return content.strip() + ("\n" * trailing_newlines)

        voice_name = match.group(1)
        content = match.group(2)

        # Strip content but preserve trailing newlines for paragraph structure
        stripped_content = content.strip()
        trailing_newlines = len(content) - len(content.rstrip("\n"))

        if not stripped_content:
            # No content after directive, skip
            return ""

        return f'<voice name="{voice_name}">{stripped_content}</voice>' + (
            "\n" * trailing_newlines
        )

    def text(self, match: re.Match) -> str:
        """Extract plain text without voice directive.

        Args:
            match: Regex match object

        Returns:
            Text content without directive marker
        """
        content = match.group(2)
        # Preserve trailing newlines for paragraph structure
        trailing_newlines = len(content) - len(content.rstrip("\n"))
        return content.strip() + ("\n" * trailing_newlines)
