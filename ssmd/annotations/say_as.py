"""Say-as annotation: [text](as: telephone) → <say-as>text</say-as>"""

import re

from ssmd.annotations.base import BaseAnnotation


class SayAsAnnotation(BaseAnnotation):
    """Process say-as annotations.

    Examples:
        [+49 123456](as: telephone) →
            <say-as interpret-as="telephone">+49 123456</say-as>
        [fuck](as: expletive) →
            <say-as interpret-as="expletive">fuck</say-as>
        [29.12.2017](as: date, format: "dd.mm.yyyy") →
            <say-as interpret-as="date" format="dd.mm.yyyy">29.12.2017</say-as>
        [123](as: cardinal, detail: 2) →
            <say-as interpret-as="cardinal" detail="2">123</say-as>

    Supported interpret-as values:
        - character, number, ordinal, digits, fraction, unit
        - date, time, address, telephone, expletive
    """

    def __init__(self, match: re.Match):
        """Initialize with interpret-as value, optional format, and optional detail.

        Args:
            match: Regex match containing interpret-as, format, and detail
        """
        self.interpret_as = match.group(1).strip()
        self.format = match.group(2).strip() if match.group(2) else None
        self.detail = match.group(3).strip() if match.group(3) else None

    @classmethod
    def regex(cls) -> re.Pattern:
        """Match say-as annotations.

        Returns:
            Pattern matching as: annotations with optional format and detail
        """
        # Match "as: type" or "as: type, format: value" or "as: type, detail: N"
        # Or "as: type, format: value, detail: N"
        return re.compile(
            r"^as:\s*(\w+)"  # interpret-as (required)
            r'(?:\s*,\s*format:\s*["\']?([^"\']+)["\']?)?'  # format (optional)
            r"(?:\s*,\s*detail:\s*(\d+))?"  # detail (optional)
            r"$"
        )

    def wrap(self, text: str) -> str:
        """Wrap text in say-as tag.

        Args:
            text: Content to wrap

        Returns:
            SSML <say-as> element
        """
        attrs = [f'interpret-as="{self.interpret_as}"']

        if self.format:
            attrs.append(f'format="{self.format}"')
        if self.detail:
            attrs.append(f'detail="{self.detail}"')

        attrs_str = " ".join(attrs)
        return f"<say-as {attrs_str}>{text}</say-as>"
