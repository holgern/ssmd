"""Paragraph - A collection of sentences with shared boundaries."""

from dataclasses import dataclass, field

from ssmd.sentence import Sentence


@dataclass
class Paragraph:
    """A paragraph containing sentences.

    Paragraphs group sentences separated by blank lines in SSMD.
    """

    sentences: list[Sentence] = field(default_factory=list)

    def to_text(self) -> str:
        """Convert paragraph to plain text.

        Returns:
            Plain text with sentence text joined by spaces
        """
        parts: list[str] = []
        for sentence in self.sentences:
            text = sentence.to_text()
            if text:
                parts.append(text)
        return " ".join(parts)

    @property
    def text(self) -> str:
        """Plain text representation of the paragraph."""
        return self.to_text()

    def __iter__(self):
        """Iterate over sentences."""
        return iter(self.sentences)

    def __len__(self) -> int:
        """Return number of sentences in the paragraph."""
        return len(self.sentences)

    def __str__(self) -> str:
        """String representation returns plain text."""
        return self.to_text()
