"""Phoneme annotation: [text](ph: dIC) → <phoneme>text</phoneme>"""

import re
from pathlib import Path

from ssmd.annotations.base import BaseAnnotation


class PhonemeAnnotation(BaseAnnotation):
    """Process phoneme annotations.

    Supports both X-SAMPA and IPA notation:
        [text](ph: dIC) → <phoneme alphabet="ipa" ph="dɪç">text</phoneme>
        [text](ipa: dɪç) → <phoneme alphabet="ipa" ph="dɪç">text</phoneme>
    """

    # Lazy-loaded X-SAMPA to IPA conversion table
    _XSAMPA_TABLE: dict[str, str] | None = None

    def __init__(self, match: re.Match):
        """Initialize with phoneme data.

        Args:
            match: Regex match containing alphabet type and phonemes
        """
        alphabet = match.group(1)  # 'ph' or 'ipa'
        phonemes = match.group(2).strip()

        # Convert X-SAMPA to IPA if needed
        if alphabet == "ph":
            self.phonemes = self._xsampa_to_ipa(phonemes)
        else:
            self.phonemes = phonemes

    @classmethod
    def regex(cls) -> re.Pattern:
        """Match phoneme annotations.

        Returns:
            Pattern matching ph: or ipa: annotations
        """
        return re.compile(r"^(ph|ipa):\s*(.+)$")

    def wrap(self, text: str) -> str:
        """Wrap text in phoneme tag.

        Args:
            text: Content to wrap

        Returns:
            SSML <phoneme> element
        """
        return f'<phoneme alphabet="ipa" ph="{self.phonemes}">{text}</phoneme>'

    @classmethod
    def _load_xsampa_table(cls) -> dict[str, str]:
        """Load X-SAMPA to IPA conversion table.

        Returns:
            Dictionary mapping X-SAMPA to IPA
        """
        if cls._XSAMPA_TABLE is not None:
            return cls._XSAMPA_TABLE

        table = {}
        table_file = Path(__file__).parent / "xsampa_to_ipa.txt"

        if table_file.exists():
            with open(table_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        parts = line.split(maxsplit=1)
                        if len(parts) == 2:
                            xsampa, ipa = parts
                            table[xsampa] = ipa

        cls._XSAMPA_TABLE = table
        return table

    @classmethod
    def _xsampa_to_ipa(cls, xsampa: str) -> str:
        """Convert X-SAMPA notation to IPA.

        Args:
            xsampa: X-SAMPA phoneme string

        Returns:
            IPA phoneme string
        """
        table = cls._load_xsampa_table()

        # Sort by length (longest first) for proper replacement
        sorted_keys = sorted(table.keys(), key=len, reverse=True)

        result = xsampa
        for x in sorted_keys:
            result = result.replace(x, table[x])

        return result
