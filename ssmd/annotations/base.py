"""Base annotation class for SSMD conversion."""

import re
from abc import ABC, abstractmethod
from typing import Optional


class BaseAnnotation(ABC):
    """Abstract base class for annotations.

    Annotations are specified in the format [text](annotation)
    where annotation can be language codes, phonemes, prosody, etc.
    """

    @classmethod
    @abstractmethod
    def regex(cls) -> re.Pattern:
        """Pattern to match this annotation type.

        Returns:
            Compiled regex pattern
        """
        pass

    @classmethod
    def try_create(cls, annotation_str: str) -> Optional["BaseAnnotation"]:
        """Try to create annotation from string.

        Args:
            annotation_str: Annotation string to parse

        Returns:
            Annotation instance or None if no match
        """
        match = cls.regex().match(annotation_str.strip())
        if match:
            return cls(match)  # type: ignore[call-arg]
        return None

    @abstractmethod
    def wrap(self, text: str) -> str:
        """Wrap text in SSML element.

        Args:
            text: Content to wrap

        Returns:
            SSML string with text wrapped
        """
        pass

    def combine(self, other: "BaseAnnotation") -> None:  # noqa: B027
        """Combine with duplicate annotation.

        Default behavior: first annotation wins, ignore duplicates.
        Override this method to implement custom combining logic.

        Args:
            other: Another annotation of the same type
        """
        pass  # Default: ignore duplicate
