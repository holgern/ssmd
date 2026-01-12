"""Language annotation: [text](en) → <lang xml:lang="en-US">text</lang>"""

import re

from ssmd.annotations.base import BaseAnnotation


class LanguageAnnotation(BaseAnnotation):
    """Process language code annotations.

    Examples:
        [text](en) → <lang xml:lang="en-US">text</lang>
        [text](en-GB) → <lang xml:lang="en-GB">text</lang>
        [text](de) → <lang xml:lang="de-DE">text</lang>
    """

    # Language code defaults (2-letter code → full locale)
    DEFAULTS = {
        "en": "en-US",
        "de": "de-DE",
        "fr": "fr-FR",
        "es": "es-ES",
        "it": "it-IT",
        "pt": "pt-PT",
        "ru": "ru-RU",
        "zh": "zh-CN",
        "ja": "ja-JP",
        "ko": "ko-KR",
        "ar": "ar-SA",
        "hi": "hi-IN",
        "nl": "nl-NL",
        "pl": "pl-PL",
        "sv": "sv-SE",
        "da": "da-DK",
        "no": "no-NO",
        "fi": "fi-FI",
    }

    lang: str  # Type annotation for mypy

    def __init__(self, match: re.Match):
        """Initialize with language code.

        Args:
            match: Regex match containing language code
        """
        # Group 1 is from "lang: xx" format, group 2 is from bare "xx" format
        lang_code = match.group(1) or match.group(2)
        assert lang_code is not None, "Language code is required"
        # Auto-complete if only 2-letter code
        if lang_code in self.DEFAULTS:
            self.lang = self.DEFAULTS[lang_code]
        else:
            self.lang = lang_code

    @classmethod
    def regex(cls) -> re.Pattern:
        """Match language codes.

        Returns:
            Pattern matching "lang: xx" or bare language codes
            (2-letter or full locale codes)
        """
        # Match either "lang: fr" format or bare "fr" or "en-US" format
        return re.compile(
            r"^(?:lang:\s*([a-z]{2}(?:-[A-Z]{2})?)|([a-z]{2}(?:-[A-Z]{2})?))$"
        )

    def wrap(self, text: str) -> str:
        """Wrap text in lang tag.

        Args:
            text: Content to wrap

        Returns:
            SSML <lang> element
        """
        return f'<lang xml:lang="{self.lang}">{text}</lang>'
