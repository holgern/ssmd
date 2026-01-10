"""Voice annotation: [text](voice: name) → <voice name="...">text</voice>"""

import re

from ssmd.annotations.base import BaseAnnotation


class VoiceAnnotation(BaseAnnotation):
    """Process voice annotations.

    Examples:
        [text](voice: Joanna) →
            <voice name="Joanna">text</voice>
        [text](voice: en-US-Wavenet-A) →
            <voice name="en-US-Wavenet-A">text</voice>
        [text](voice: en-US, gender: female) →
            <voice language="en-US" gender="female">text</voice>
        [text](voice: en-GB, gender: male, variant: 1) →
            <voice language="en-GB" gender="male" variant="1">text</voice>

    Supported attributes:
        - name: Voice name (e.g., "Joanna", "en-US-Wavenet-A")
        - language: BCP-47 language code (e.g., "en-US", "fr-FR")
        - gender: "male", "female", or "neutral"
        - variant: Integer variant number for tiebreaking
    """

    def __init__(self, match: re.Match):
        """Initialize with voice parameters.

        Args:
            match: Regex match containing voice attributes
        """
        params_str = match.group(0)

        # Parse voice parameters
        self.name = None
        self.language = None
        self.gender = None
        self.variant = None

        # Check for gender or variant - if present, first param is language
        has_gender = "gender:" in params_str
        has_variant = "variant:" in params_str

        # Parse the voice/language value
        voice_match = re.search(r"voice:\s*([a-zA-Z0-9_-]+)", params_str)
        if voice_match:
            voice_value = voice_match.group(1)

            # If gender or variant is specified, treat as language
            # Or if it matches language code pattern (e.g., en-US, fr-FR)
            if (
                has_gender
                or has_variant
                or re.match(r"^[a-z]{2}(-[A-Z]{2})?$", voice_value)
            ):
                self.language = voice_value
            else:
                # Otherwise it's a voice name
                self.name = voice_value

        # Parse gender
        gender_match = re.search(r"gender:\s*(male|female|neutral)", params_str)
        if gender_match:
            self.gender = gender_match.group(1)

        # Parse variant
        variant_match = re.search(r"variant:\s*(\d+)", params_str)
        if variant_match:
            self.variant = variant_match.group(1)

    @classmethod
    def regex(cls) -> re.Pattern:
        """Match voice annotations.

        Returns:
            Pattern matching voice: annotations with optional attributes
        """
        # Match entire voice annotation including commas
        # Pattern: voice: NAME or voice: LANG, gender: X, variant: Y
        return re.compile(
            r"^voice:\s*[a-zA-Z0-9_-]+"
            r"(?:\s*,\s*(?:gender:\s*(?:male|female|neutral)|variant:\s*\d+))*$"
        )

    def wrap(self, text: str) -> str:
        """Wrap text in voice tag.

        Args:
            text: Content to wrap

        Returns:
            SSML <voice> element
        """
        attrs = []

        if self.name:
            attrs.append(f'name="{self.name}"')
        else:
            if self.language:
                attrs.append(f'language="{self.language}"')
            if self.gender:
                attrs.append(f'gender="{self.gender}"')
            if self.variant:
                attrs.append(f'variant="{self.variant}"')

        attrs_str = " ".join(attrs)
        return f"<voice {attrs_str}>{text}</voice>"
