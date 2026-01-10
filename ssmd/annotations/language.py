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

    def __init__(self, match: re.Match):
        """Initialize with language code.

        Args:
            match: Regex match containing language code
        """
        lang_code = match.group(1)
        # Auto-complete if only 2-letter code
        self.lang = self.DEFAULTS.get(lang_code, lang_code)

    @classmethod
    def regex(cls) -> re.Pattern:
        """Match language codes.

        Returns:
            Pattern matching 2-letter or full locale codes
        """
        return re.compile(r"^([a-z]{2}(?:-[A-Z]{2})?)$")

    def wrap(self, text: str) -> str:
        """Wrap text in lang tag.

        Args:
            text: Content to wrap

        Returns:
            SSML <lang> element
        """
        return f'<lang xml:lang="{self.lang}">{text}</lang>'
