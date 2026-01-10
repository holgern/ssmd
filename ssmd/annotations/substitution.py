"""Substitution annotation: [H2O](sub: water) → <sub alias="water">H2O</sub>"""

import re

from ssmd.annotations.base import BaseAnnotation


class SubstitutionAnnotation(BaseAnnotation):
    """Process substitution annotations.

    Example:
        [H2O](sub: water) → <sub alias="water">H2O</sub>
    """

    def __init__(self, match: re.Match):
        """Initialize with alias value.

        Args:
            match: Regex match containing alias
        """
        self.alias = match.group(1).strip()

    @classmethod
    def regex(cls) -> re.Pattern:
        """Match substitution annotations.

        Returns:
            Pattern matching sub: annotations
        """
        return re.compile(r"^sub:\s*(.+)$")

    def wrap(self, text: str) -> str:
        """Wrap text in sub tag.

        Args:
            text: Content to wrap

        Returns:
            SSML <sub> element
        """
        return f'<sub alias="{self.alias}">{text}</sub>'
