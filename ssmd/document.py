"""SSMD Document - Main document container with rich TTS features."""

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, overload

from ssmd.formatter import format_ssmd
from ssmd.parser import parse_sentences
from ssmd.utils import extract_sentences, format_xml

if TYPE_CHECKING:
    from ssmd.capabilities import TTSCapabilities


class Document:
    """Main SSMD document container with incremental building and editing.

    This is the primary interface for working with SSMD documents. It provides
    a clean, document-centric API for creating, editing, and exporting TTS content.

    The Document stores content as fragments (pieces of text) with separators
    between them, allowing efficient incremental building and editing while
    preserving the document structure.

    Example:
        Basic usage::

            import ssmd

            # Create and build a document
            doc = ssmd.Document()
            doc.add_sentence("Hello world!")
            doc.add_sentence("This is SSMD.")

            # Export to different formats
            ssml = doc.to_ssml()
            text = doc.to_text()

            # Iterate for streaming TTS
            for sentence in doc.sentences():
                tts_engine.speak(sentence)

        Advanced usage::

            # Load from SSML
            doc = ssmd.Document.from_ssml("<speak>Hello</speak>")

            # Edit the document
            doc[0] = "Modified content"
            doc.add_paragraph("New paragraph")

            # Access raw content
            print(doc.ssmd)  # Raw SSMD markdown
    """

    def __init__(
        self,
        content: str = "",
        config: dict[str, Any] | None = None,
        capabilities: "TTSCapabilities | str | None" = None,
        escape_syntax: bool = False,
        escape_patterns: list[str] | None = None,
    ) -> None:
        """Initialize a new SSMD document.

        Args:
            content: Optional initial SSMD content
            config: Configuration dictionary with options:
                - skip (list): Processor names to skip
                - output_speak_tag (bool): Wrap in <speak> tags (default: True)
                - pretty_print (bool): Format XML output (default: False)
                - auto_sentence_tags (bool): Auto-wrap sentences (default: False)
                - heading_levels (dict): Custom heading configurations
                - extensions (dict): Registered extension handlers
                - sentence_model_size (str): spaCy model size for sentence
                  detection ("sm", "md", "lg", "trf"). Default: "sm"
                - sentence_spacy_model (str): Custom spaCy model name
                  (overrides sentence_model_size)
                - sentence_use_spacy (bool): If False, use fast regex splitting
                  instead of spaCy. Default: True
            capabilities: TTS capabilities (TTSCapabilities instance or
                preset name). Presets: 'espeak', 'pyttsx3', 'google',
                'polly', 'azure', 'minimal', 'full'
            escape_syntax: If True, escape SSMD-like syntax in content to
                prevent interpretation as markup. Useful for plain text or
                markdown that may coincidentally contain SSMD patterns.
            escape_patterns: List of specific pattern types to escape when
                escape_syntax=True. If None, escapes all patterns.
                Valid values: 'emphasis', 'annotations', 'breaks', 'marks',
                'headings', 'voice_directives', 'prosody_shorthand'

        Example:
            >>> doc = ssmd.Document("Hello *world*!")
            >>> doc = ssmd.Document(capabilities='pyttsx3')
            >>> doc = ssmd.Document("Text", config={'auto_sentence_tags': True})
            >>> # Fast sentence detection (no spaCy required)
            >>> doc = ssmd.Document(config={'sentence_use_spacy': False})
            >>> # High quality sentence detection
            >>> doc = ssmd.Document(config={'sentence_model_size': 'lg'})
            >>> # Escape SSMD syntax for plain text/markdown
            >>> doc = ssmd.Document(markdown, escape_syntax=True)
            >>> # Selective escaping
            >>> doc = ssmd.Document(
            ...     text,
            ...     escape_syntax=True,
            ...     escape_patterns=['emphasis', 'annotations']
            ... )
        """
        self._fragments: list[str] = []
        self._separators: list[str] = []
        self._config = config or {}
        self._capabilities = capabilities
        self._capabilities_obj: TTSCapabilities | None = None  # Resolved capabilities
        self._cached_ssml: str | None = None
        self._cached_sentences: list[str] | None = None
        self._escape_syntax = escape_syntax
        self._escape_patterns = escape_patterns

        # Add initial content if provided
        if content:
            if escape_syntax:
                from ssmd.utils import escape_ssmd_syntax

                content = escape_ssmd_syntax(content, patterns=escape_patterns)
            self._fragments.append(content)

    @classmethod
    def from_ssml(
        cls,
        ssml: str,
        config: dict[str, Any] | None = None,
        capabilities: "TTSCapabilities | str | None" = None,
    ) -> "Document":
        """Create a Document from SSML string.

        Args:
            ssml: SSML XML string
            config: Optional configuration parameters
            capabilities: Optional TTS capabilities

        Returns:
            New Document instance with converted content

        Example:
            >>> ssml = '<speak><emphasis>Hello</emphasis> world</speak>'
            >>> doc = ssmd.Document.from_ssml(ssml)
            >>> doc.ssmd
            '*Hello* world'
        """
        from ssmd.ssml_parser import SSMLParser

        parser = SSMLParser(config or {})
        ssmd_content = parser.to_ssmd(ssml)
        return cls(ssmd_content, config, capabilities)

    @classmethod
    def from_text(
        cls,
        text: str,
        config: dict[str, Any] | None = None,
        capabilities: "TTSCapabilities | str | None" = None,
    ) -> "Document":
        """Create a Document from plain text.

        This is essentially the same as Document(text), but provides
        a symmetric API with from_ssml().

        Args:
            text: Plain text or SSMD content
            config: Optional configuration parameters
            capabilities: Optional TTS capabilities

        Returns:
            New Document instance

        Example:
            >>> doc = ssmd.Document.from_text("Hello world")
            >>> doc.ssmd
            'Hello world'
        """
        return cls(text, config, capabilities)

    # ═══════════════════════════════════════════════════════════
    # BUILDING METHODS
    # ═══════════════════════════════════════════════════════════

    def add(self, text: str) -> "Document":
        """Append text without separator.

        Use this when you want to append content immediately after
        the previous content with no spacing.

        Args:
            text: SSMD text to append

        Returns:
            Self for method chaining

        Example:
            >>> doc = ssmd.Document("Hello")
            >>> doc.add(" world")
            >>> doc.ssmd
            'Hello world'
        """
        if not text:
            return self

        self._invalidate_cache()

        if not self._fragments:
            self._fragments.append(text)
        else:
            self._separators.append("")
            self._fragments.append(text)

        return self

    def add_sentence(self, text: str) -> "Document":
        """Append text with newline separator.

        Use this to add a new sentence on a new line.

        Args:
            text: SSMD text to append

        Returns:
            Self for method chaining

        Example:
            >>> doc = ssmd.Document("First sentence.")
            >>> doc.add_sentence("Second sentence.")
            >>> doc.ssmd
            'First sentence.\\nSecond sentence.'
        """
        if not text:
            return self

        self._invalidate_cache()

        if not self._fragments:
            self._fragments.append(text)
        else:
            self._separators.append("\n")
            self._fragments.append(text)

        return self

    def add_paragraph(self, text: str) -> "Document":
        """Append text with double newline separator.

        Use this to start a new paragraph.

        Args:
            text: SSMD text to append

        Returns:
            Self for method chaining

        Example:
            >>> doc = ssmd.Document("First paragraph.")
            >>> doc.add_paragraph("Second paragraph.")
            >>> doc.ssmd
            'First paragraph.\\n\\nSecond paragraph.'
        """
        if not text:
            return self

        self._invalidate_cache()

        if not self._fragments:
            self._fragments.append(text)
        else:
            self._separators.append("\n\n")
            self._fragments.append(text)

        return self

    # ═══════════════════════════════════════════════════════════
    # EXPORT METHODS
    # ═══════════════════════════════════════════════════════════

    def to_ssml(self) -> str:
        """Export document to SSML format.

        Returns:
            SSML XML string

        Example:
            >>> doc = ssmd.Document("Hello *world*!")
            >>> doc.to_ssml()
            '<speak>Hello <emphasis>world</emphasis>!</speak>'
        """
        if self._cached_ssml is None:
            ssmd_content = self.ssmd

            # Get resolved capabilities
            capabilities = self._get_capabilities()

            # Get config options
            output_speak_tag = self._config.get("output_speak_tag", True)
            auto_sentence_tags = self._config.get("auto_sentence_tags", False)
            pretty_print = self._config.get("pretty_print", False)
            extensions = self._config.get("extensions")
            heading_levels = self._config.get("heading_levels")

            # Get sentence detection config
            model_size = self._config.get("sentence_model_size")
            spacy_model = self._config.get("sentence_spacy_model")
            use_spacy = self._config.get("sentence_use_spacy")

            # Parse SSMD into sentences (with placeholders if escape_syntax=True)
            sentences = parse_sentences(
                ssmd_content,
                capabilities=capabilities,
                model_size=model_size,
                spacy_model=spacy_model,
                use_spacy=use_spacy,
                heading_levels=heading_levels,
                extensions=extensions,
            )

            # Build SSML from sentences
            ssml_parts = []
            for sentence in sentences:
                ssml_parts.append(
                    sentence.to_ssml(
                        capabilities=capabilities,
                        extensions=extensions,
                        wrap_sentence=auto_sentence_tags,
                    )
                )

            ssml = "".join(ssml_parts)

            # Wrap in <speak> tags if configured
            if output_speak_tag:
                ssml = f"<speak>{ssml}</speak>"

            # Unescape placeholders AFTER generating SSML
            # (restore original characters in output)
            if self._escape_syntax:
                from ssmd.utils import unescape_ssmd_syntax

                ssml = unescape_ssmd_syntax(ssml)

            # Pretty print if configured
            if pretty_print:
                ssml = format_xml(ssml, pretty=True)

            self._cached_ssml = ssml
        return self._cached_ssml

    def to_ssmd(self) -> str:
        """Export document to SSMD format with proper formatting.

        Returns SSMD with proper line breaks (each sentence on a new line).

        Returns:
            SSMD markdown string with proper formatting

        Example:
            >>> doc = ssmd.Document.from_ssml('<speak><emphasis>Hi</emphasis></speak>')
            >>> doc.to_ssmd()
            '*Hi*'
        """
        raw_ssmd = self.ssmd
        if not raw_ssmd.strip():
            return raw_ssmd

        # Parse into sentences and format with proper line breaks
        sentences = parse_sentences(raw_ssmd)
        return format_ssmd(sentences).rstrip("\n")

    def to_text(self) -> str:
        """Export document to plain text (strips all markup).

        Returns:
            Plain text string with all SSMD markup removed

        Example:
            >>> doc = ssmd.Document("Hello *world* @marker!")
            >>> doc.to_text()
            'Hello world!'
        """
        ssmd_content = self.ssmd
        sentences = parse_sentences(ssmd_content)
        text_parts = []
        for sentence in sentences:
            text_parts.append(sentence.to_text())
        return " ".join(text_parts)

    # ═══════════════════════════════════════════════════════════
    # PROPERTIES
    # ═══════════════════════════════════════════════════════════

    @property
    def ssmd(self) -> str:
        """Get raw SSMD content.

        Returns the complete SSMD document by joining all fragments
        with their separators.

        Returns:
            SSMD markdown string
        """
        if not self._fragments:
            return ""

        if len(self._fragments) == 1:
            return self._fragments[0]

        result = self._fragments[0]
        for i, separator in enumerate(self._separators):
            result += separator + self._fragments[i + 1]
        return result

    @property
    def config(self) -> dict[str, Any]:
        """Get configuration dictionary.

        Returns:
            Configuration dict
        """
        return self._config

    @config.setter
    def config(self, value: dict[str, Any]) -> None:
        """Set configuration dictionary.

        Args:
            value: New configuration dict
        """
        self._config = value
        self._capabilities_obj = None  # Reset resolved capabilities
        self._invalidate_cache()

    @property
    def capabilities(self) -> "TTSCapabilities | str | None":
        """Get TTS capabilities.

        Returns:
            TTSCapabilities instance, preset name, or None
        """
        return self._capabilities

    @capabilities.setter
    def capabilities(self, value: "TTSCapabilities | str | None") -> None:
        """Set TTS capabilities.

        Args:
            value: TTSCapabilities instance, preset name, or None
        """
        self._capabilities = value
        self._capabilities_obj = None  # Reset resolved capabilities
        self._invalidate_cache()

    # ═══════════════════════════════════════════════════════════
    # ITERATION
    # ═══════════════════════════════════════════════════════════

    def sentences(self, as_documents: bool = False) -> "Iterator[str | Document]":
        """Iterate through sentences.

        Yields SSML sentences one at a time, which is useful for
        streaming TTS applications.

        Args:
            as_documents: If True, yield Document objects instead of strings.
                Each sentence will be wrapped in its own Document instance.

        Yields:
            SSML sentence strings (str), or Document objects if as_documents=True

        Example:
            >>> doc = ssmd.Document("First. Second. Third.")
            >>> for sentence in doc.sentences():
            ...     tts_engine.speak(sentence)

            >>> for sentence_doc in doc.sentences(as_documents=True):
            ...     ssml = sentence_doc.to_ssml()
            ...     ssmd = sentence_doc.to_ssmd()
        """
        if self._cached_sentences is None:
            ssml = self.to_ssml()
            self._cached_sentences = extract_sentences(ssml)

        for sentence in self._cached_sentences:
            if as_documents:
                # Create a Document from this SSML sentence
                yield Document.from_ssml(
                    sentence,
                    config=self._config,
                    capabilities=self._capabilities,
                )
            else:
                yield sentence

    # ═══════════════════════════════════════════════════════════
    # LIST-LIKE INTERFACE (operates on SSML sentences)
    # ═══════════════════════════════════════════════════════════

    def __len__(self) -> int:
        """Return number of sentences in the document.

        Returns:
            Number of sentences

        Example:
            >>> doc = ssmd.Document("First. Second. Third.")
            >>> len(doc)
            3
        """
        if self._cached_sentences is None:
            ssml = self.to_ssml()
            self._cached_sentences = extract_sentences(ssml)
        return len(self._cached_sentences)

    @overload
    def __getitem__(self, index: int) -> str: ...

    @overload
    def __getitem__(self, index: slice) -> list[str]: ...

    def __getitem__(self, index: int | slice) -> str | list[str]:
        """Get sentence(s) by index.

        Args:
            index: Sentence index or slice

        Returns:
            SSML sentence string or list of strings

        Raises:
            IndexError: If index is out of range

        Example:
            >>> doc = ssmd.Document("First. Second. Third.")
            >>> doc[0]  # First sentence SSML
            >>> doc[-1]  # Last sentence SSML
            >>> doc[0:2]  # First two sentences
        """
        if self._cached_sentences is None:
            ssml = self.to_ssml()
            self._cached_sentences = extract_sentences(ssml)
        return self._cached_sentences[index]

    def __setitem__(self, index: int, value: str) -> None:
        """Replace sentence at index.

        This reconstructs the document with the modified sentence.

        Args:
            index: Sentence index
            value: New SSMD content for this sentence

        Raises:
            IndexError: If index is out of range

        Example:
            >>> doc = ssmd.Document("First. Second. Third.")
            >>> doc[0] = "Modified first sentence."
        """
        if self._cached_sentences is None:
            ssml = self.to_ssml()
            self._cached_sentences = extract_sentences(ssml)

        # Convert sentence to SSMD
        from ssmd.ssml_parser import SSMLParser

        parser = SSMLParser(self._config)

        # Build new fragments list
        new_fragments: list[str] = []
        new_separators: list[str] = []

        for i, sentence_ssml in enumerate(self._cached_sentences):
            if i == index:
                # Replace with new value
                new_fragments.append(value)
            else:
                # Convert existing SSML to SSMD
                sentence_ssmd = parser.to_ssmd(sentence_ssml)
                new_fragments.append(sentence_ssmd)

            # Add separator (newline between sentences)
            if i < len(self._cached_sentences) - 1:
                new_separators.append("\n")

        self._fragments = new_fragments
        self._separators = new_separators
        self._invalidate_cache()

    def __delitem__(self, index: int) -> None:
        """Delete sentence at index.

        Args:
            index: Sentence index

        Raises:
            IndexError: If index is out of range

        Example:
            >>> doc = ssmd.Document("First. Second. Third.")
            >>> del doc[1]  # Remove second sentence
        """
        if self._cached_sentences is None:
            ssml = self.to_ssml()
            self._cached_sentences = extract_sentences(ssml)

        from ssmd.ssml_parser import SSMLParser

        parser = SSMLParser(self._config)

        # Build new fragments list (excluding deleted index)
        new_fragments: list[str] = []
        new_separators: list[str] = []

        for i, sentence_ssml in enumerate(self._cached_sentences):
            if i == index:
                continue  # Skip this sentence

            sentence_ssmd = parser.to_ssmd(sentence_ssml)
            new_fragments.append(sentence_ssmd)

            # Add separator (newline between sentences)
            if len(new_fragments) > 1:
                if len(new_separators) < len(new_fragments) - 1:
                    new_separators.append("\n")

        self._fragments = new_fragments
        self._separators = new_separators
        self._invalidate_cache()

    def __iter__(self) -> "Iterator[str | Document]":
        """Iterate through sentences.

        Yields:
            SSML sentence strings

        Example:
            >>> doc = ssmd.Document("First. Second.")
            >>> for sentence in doc:
            ...     print(sentence)
        """
        return self.sentences(as_documents=False)

    def __iadd__(self, other: "str | Document") -> "Document":
        """Support += operator for appending content.

        Args:
            other: String or Document to append

        Returns:
            Self for chaining

        Example:
            >>> doc = ssmd.Document("Hello")
            >>> doc += " world"
            >>> other = ssmd.Document("More")
            >>> doc += other
        """
        if isinstance(other, Document):
            # Append another document's content
            return self.add(other.ssmd)
        else:
            # Append string
            return self.add(other)

    # ═══════════════════════════════════════════════════════════
    # EDITING METHODS
    # ═══════════════════════════════════════════════════════════

    def insert(self, index: int, text: str, separator: str = "") -> "Document":
        """Insert text at specific fragment index.

        Args:
            index: Position to insert (0 = beginning)
            text: SSMD text to insert
            separator: Separator to use ("", "\\n", or "\\n\\n")

        Returns:
            Self for method chaining

        Example:
            >>> doc = ssmd.Document("Hello world")
            >>> doc.insert(0, "Start: ", "")
            >>> doc.ssmd
            'Start: Hello world'
        """
        if not text:
            return self

        self._invalidate_cache()

        if not self._fragments:
            self._fragments.append(text)
        elif index == 0:
            # Insert at beginning
            self._fragments.insert(0, text)
            if len(self._fragments) > 1:
                self._separators.insert(0, separator)
        elif index >= len(self._fragments):
            # Append at end
            self._separators.append(separator)
            self._fragments.append(text)
        else:
            # Insert in middle
            self._fragments.insert(index, text)
            self._separators.insert(index, separator)

        return self

    def remove(self, index: int) -> "Document":
        """Remove fragment at index.

        This is the same as `del doc[index]` but returns self for chaining.

        Args:
            index: Fragment index to remove

        Returns:
            Self for method chaining

        Raises:
            IndexError: If index is out of range

        Example:
            >>> doc = ssmd.Document("First. Second. Third.")
            >>> doc.remove(1)
        """
        del self[index]
        return self

    def clear(self) -> "Document":
        """Remove all content from the document.

        Returns:
            Self for method chaining

        Example:
            >>> doc = ssmd.Document("Hello world")
            >>> doc.clear()
            >>> doc.ssmd
            ''
        """
        self._fragments.clear()
        self._separators.clear()
        self._invalidate_cache()
        return self

    def replace(self, old: str, new: str, count: int = -1) -> "Document":
        """Replace text across all fragments.

        Args:
            old: Text to find
            new: Text to replace with
            count: Maximum replacements (-1 = all)

        Returns:
            Self for method chaining

        Example:
            >>> doc = ssmd.Document("Hello world. Hello again.")
            >>> doc.replace("Hello", "Hi")
            >>> doc.ssmd
            'Hi world. Hi again.'
        """
        self._invalidate_cache()

        replacements_made = 0
        for i, fragment in enumerate(self._fragments):
            if count == -1:
                self._fragments[i] = fragment.replace(old, new)
            else:
                remaining = count - replacements_made
                if remaining <= 0:
                    break
                self._fragments[i] = fragment.replace(old, new, remaining)
                replacements_made += self._fragments[i].count(new) - fragment.count(new)

        return self

    # ═══════════════════════════════════════════════════════════
    # ADVANCED METHODS
    # ═══════════════════════════════════════════════════════════

    def merge(self, other: "Document", separator: str = "\n\n") -> "Document":
        """Merge another document into this one.

        Args:
            other: Document to merge
            separator: Separator to use between documents

        Returns:
            Self for method chaining

        Example:
            >>> doc1 = ssmd.Document("First document.")
            >>> doc2 = ssmd.Document("Second document.")
            >>> doc1.merge(doc2)
            >>> doc1.ssmd
            'First document.\\n\\nSecond document.'
        """
        if not other._fragments:
            return self

        self._invalidate_cache()

        if not self._fragments:
            self._fragments = other._fragments.copy()
            self._separators = other._separators.copy()
        else:
            self._separators.append(separator)
            self._fragments.extend(other._fragments)
            self._separators.extend(other._separators)

        return self

    def split(self) -> list["Document"]:
        """Split document into individual sentence Documents.

        Returns:
            List of Document objects, one per sentence

        Example:
            >>> doc = ssmd.Document("First. Second. Third.")
            >>> sentences = doc.split()
            >>> len(sentences)
            3
            >>> sentences[0].ssmd
            'First.'
        """
        return [
            Document.from_ssml(
                str(sentence_ssml),  # Ensure it's a string
                config=self._config,
                capabilities=self._capabilities,
            )
            for sentence_ssml in self.sentences(as_documents=False)
        ]

    def get_fragment(self, index: int) -> str:
        """Get raw fragment by index (not sentence).

        This accesses the internal fragment storage directly,
        which may be different from sentence boundaries.

        Args:
            index: Fragment index

        Returns:
            Raw SSMD fragment string

        Raises:
            IndexError: If index is out of range

        Example:
            >>> doc = ssmd.Document()
            >>> doc.add("First")
            >>> doc.add_sentence("Second")
            >>> doc.get_fragment(0)
            'First'
            >>> doc.get_fragment(1)
            'Second'
        """
        return self._fragments[index]

    # ═══════════════════════════════════════════════════════════
    # INTERNAL HELPERS
    # ═══════════════════════════════════════════════════════════

    def _get_capabilities(self) -> "TTSCapabilities | None":
        """Get resolved TTSCapabilities object.

        Returns:
            TTSCapabilities instance or None
        """
        if self._capabilities_obj is None and self._capabilities is not None:
            from ssmd.capabilities import TTSCapabilities, get_preset

            if isinstance(self._capabilities, str):
                self._capabilities_obj = get_preset(self._capabilities)
            elif isinstance(self._capabilities, TTSCapabilities):
                self._capabilities_obj = self._capabilities
        return self._capabilities_obj

    def _invalidate_cache(self) -> None:
        """Invalidate cached SSML and sentences."""
        self._cached_ssml = None
        self._cached_sentences = None

    def __repr__(self) -> str:
        """String representation of document.

        Returns:
            Representation string

        Example:
            >>> doc = ssmd.Document("Hello. World.")
            >>> repr(doc)
            'Document(2 sentences, 13 chars)'
        """
        try:
            num_sentences = len(self)
            return f"Document({num_sentences} sentences, {len(self.ssmd)} chars)"
        except Exception:
            return f"Document({len(self.ssmd)} chars)"

    def __str__(self) -> str:
        """String conversion returns SSMD content.

        Returns:
            SSMD string

        Example:
            >>> doc = ssmd.Document("Hello *world*")
            >>> str(doc)
            'Hello *world*'
        """
        return self.ssmd
