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

        @voice: fr-FR, gender: female
        Bonjour! Comment allez-vous?

        @voice: en-GB, gender: male, variant: 1
        Hello from England!
    """

    name = "voice_directive"

    def regex(self) -> re.Pattern:
        """Match @voice: name or @voice(name) at start of line.

        Returns:
            Pattern matching voice directive
        """
        # Match @voice: followed by parameters (name or attributes)
        # Parameters can include: name, language codes, gender, variant
        # Examples:
        #   @voice: sarah
        #   @voice: fr-FR, gender: female
        #   @voice(en-US, gender: male, variant: 1)
        return re.compile(
            r"^@voice(?::\s*|\()"
            r"([a-zA-Z0-9_-]+(?:\s*,\s*(?:gender|variant):\s*[a-zA-Z0-9]+)*)"
            r"\)?\s*\n"
            r"((?:(?!^@voice)(?:.*\n?))+?)(?=\n\n|^@voice|\Z)",
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

        params_str = match.group(1)
        content = match.group(2)

        # Strip content but preserve trailing newlines for paragraph structure
        stripped_content = content.strip()
        trailing_newlines = len(content) - len(content.rstrip("\n"))

        if not stripped_content:
            # No content after directive, skip
            return ""

        # Parse voice parameters
        # Can be: "name", "lang", or "lang, gender: X, variant: Y"
        name = None
        language = None
        gender = None
        variant = None

        # Check for gender or variant attributes
        has_gender = "gender:" in params_str
        has_variant = "variant:" in params_str

        # Extract the first parameter (voice name or language)
        voice_match = re.match(r"([a-zA-Z0-9_-]+)", params_str)
        if voice_match:
            voice_value = voice_match.group(1)

            # If gender or variant specified, or if it looks like a language code,
            # treat as language
            if (
                has_gender
                or has_variant
                or re.match(r"^[a-z]{2}(-[A-Z]{2})?$", voice_value)
            ):
                language = voice_value
            else:
                # Otherwise it's a voice name
                name = voice_value

        # Parse gender if present
        gender_match = re.search(r"gender:\s*([a-zA-Z]+)", params_str)
        if gender_match:
            gender = gender_match.group(1)

        # Parse variant if present
        variant_match = re.search(r"variant:\s*(\d+)", params_str)
        if variant_match:
            variant = variant_match.group(1)

        # Build SSML attributes
        attrs = []
        if name:
            attrs.append(f'name="{name}"')
        else:
            if language:
                attrs.append(f'language="{language}"')
            if gender:
                attrs.append(f'gender="{gender}"')
            if variant:
                attrs.append(f'variant="{variant}"')

        attrs_str = " ".join(attrs)
        return f"<voice {attrs_str}>{stripped_content}</voice>" + (
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
