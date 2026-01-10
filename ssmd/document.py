"""SSMD document container with sentence iteration for TTS."""

from collections.abc import Iterator

from ssmd.utils import extract_sentences


class SSMDDocument:
    """Container for parsed SSMD with sentence iteration support.

    This class provides a convenient way to load an SSMD document
    and iterate through its sentences one at a time, which is useful
    for streaming TTS applications.

    Example:
        >>> from ssmd import SSMD
        >>> parser = SSMD({'auto_sentence_tags': True})
        >>> doc = parser.load("Hello world!\\nThis is a test.")
        >>> for sentence in doc:
        ...     print(sentence)
        ...     # tts_engine.speak(sentence)
    """

    def __init__(self, ssmd_text: str, converter):
        """Initialize document with SSMD text.

        Args:
            ssmd_text: SSMD markdown text
            converter: Converter instance for processing
        """
        self.ssmd_text = ssmd_text
        self.converter = converter
        self._ssml: str | None = None
        self._sentences: list[str] | None = None

    @property
    def ssml(self) -> str:
        """Get full SSML output (lazy loaded).

        Returns:
            Complete SSML string
        """
        if self._ssml is None:
            self._ssml = self.converter.convert(self.ssmd_text)
        return self._ssml

    @property
    def plain_text(self) -> str:
        """Get plain text with markup stripped.

        Returns:
            Plain text string
        """
        return self.converter.strip(self.ssmd_text)

    def sentences(self) -> Iterator[str]:
        """Yield SSML sentences one at a time.

        Yields:
            SSML sentence strings
        """
        if self._sentences is None:
            self._sentences = extract_sentences(self.ssml)

        for sentence in self._sentences:
            yield sentence

    def get_sentence(self, index: int) -> str | None:
        """Get a specific sentence by index.

        Args:
            index: Zero-based sentence index

        Returns:
            SSML sentence string or None if index out of range
        """
        if self._sentences is None:
            self._sentences = extract_sentences(self.ssml)

        if 0 <= index < len(self._sentences):
            return self._sentences[index]
        return None

    def __iter__(self) -> Iterator[str]:
        """Make document iterable.

        Yields:
            SSML sentence strings
        """
        return self.sentences()

    def __len__(self) -> int:
        """Return total number of sentences.

        Returns:
            Number of sentences in document
        """
        if self._sentences is None:
            self._sentences = extract_sentences(self.ssml)
        return len(self._sentences)

    def __getitem__(self, index: int) -> str:
        """Get sentence by index (supports indexing).

        Args:
            index: Sentence index

        Returns:
            SSML sentence string

        Raises:
            IndexError: If index is out of range
        """
        if self._sentences is None:
            self._sentences = extract_sentences(self.ssml)
        return self._sentences[index]

    def __repr__(self) -> str:
        """String representation of document.

        Returns:
            Representation string
        """
        return f"SSMDDocument({len(self)} sentences)"
