"""Say-as annotation: [text](as: telephone) → <say-as>text</say-as>"""

import re

from ssmd.annotations.base import BaseAnnotation


class SayAsAnnotation(BaseAnnotation):
    """Process say-as annotations.

    Examples:
        [+49 123456](as: telephone) → <say-as interpret-as="telephone">+49 123456</say-as>
        [fuck](as: expletive) → <say-as interpret-as="expletive">fuck</say-as>
        [29.12.2017](as: date, format: "dd.mm.yyyy") → <say-as interpret-as="date" format="dd.mm.yyyy">

    Supported interpret-as values:
        - character, number, ordinal, digits, fraction, unit
        - date, time, address, telephone, expletive
    """

    def __init__(self, match: re.Match):
        """Initialize with interpret-as value and optional format.

        Args:
            match: Regex match containing interpret-as and format
        """
        self.interpret_as = match.group(1).strip()
        self.format = match.group(2).strip() if match.group(2) else None

    @classmethod
    def regex(cls) -> re.Pattern:
        """Match say-as annotations.

        Returns:
            Pattern matching as: annotations with optional format
        """
        # Match "as: type" or "as: type, format: value"
        return re.compile(r'^as:\s*(\w+)(?:,\s*format:\s*["\']?([^"\']+)["\']?)?$')

    def wrap(self, text: str) -> str:
        """Wrap text in say-as tag.

        Args:
            text: Content to wrap

        Returns:
            SSML <say-as> element
        """
        if self.format:
            return (
                f'<say-as interpret-as="{self.interpret_as}" '
                f'format="{self.format}">{text}</say-as>'
            )
        else:
            return f'<say-as interpret-as="{self.interpret_as}">{text}</say-as>'
