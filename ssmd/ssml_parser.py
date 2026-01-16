"""SSML to SSMD converter - reverse conversion."""

import re
import xml.etree.ElementTree as ET
from typing import Any

from ssmd.formatter import format_ssmd
from ssmd.parser import parse_sentences
from ssmd.ssml_conversions import SSML_BREAK_STRENGTH_MAP


class SSMLParser:
    """Convert SSML to SSMD markdown format.

    This class provides the reverse conversion from SSML XML to the more
    human-readable SSMD markdown syntax.

    Example:
        >>> parser = SSMLParser()
        >>> ssml = '<speak><emphasis>Hello</emphasis> world</speak>'
        >>> ssmd = parser.to_ssmd(ssml)
        >>> print(ssmd)
        '*Hello* world'
    """

    # Standard locales that can be simplified (locale -> language code)
    STANDARD_LOCALES = {
        "en-US": "en",
        "en-GB": "en-GB",  # Keep non-US English locales
        "de-DE": "de",
        "fr-FR": "fr",
        "es-ES": "es",
        "it-IT": "it",
        "pt-PT": "pt",
        "ru-RU": "ru",
        "zh-CN": "zh",
        "ja-JP": "ja",
        "ko-KR": "ko",
    }

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize SSML parser.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

    def to_ssmd(self, ssml: str) -> str:
        """Convert SSML to SSMD format.

        Args:
            ssml: SSML XML string

        Returns:
            SSMD markdown string with proper formatting (each sentence on new line)

        Example:
            >>> parser = SSMLParser()
            >>> parser.to_ssmd('<speak><emphasis>Hello</emphasis></speak>')
            '*Hello*'
        """
        # Wrap in <speak> if not already wrapped
        if not ssml.strip().startswith("<speak"):
            ssml = f"<speak>{ssml}</speak>"

        # Register common SSML namespaces
        try:
            ET.register_namespace("amazon", "https://amazon.com/ssml")
        except Exception:
            pass  # Namespace might already be registered

        try:
            root = ET.fromstring(ssml)
        except ET.ParseError as e:
            raise ValueError(f"Invalid SSML XML: {e}") from e

        # Process the root element
        result = self._process_element(root)

        # Clean up whitespace
        result = self._clean_whitespace(result)

        # Restore directive newlines (protected during whitespace cleaning)
        result = result.replace("{DIRECTIVE_NEWLINE}", "\n").strip()

        # Parse into sentences and format with proper line breaks
        sentences = parse_sentences(result.strip())
        return format_ssmd(sentences)

    def _process_element(self, element: ET.Element) -> str:
        """Process an XML element and its children recursively.

        Args:
            element: XML element to process

        Returns:
            SSMD formatted string
        """
        tag = element.tag.split("}")[-1]  # Remove namespace if present

        # Handle different SSML tags
        if tag == "speak":
            return self._process_children(element)
        elif tag == "p":
            content = self._process_children(element)
            # Paragraphs are separated by double newlines
            return f"\n\n{content}\n\n"
        elif tag == "s":
            # Sentences - just process children
            return self._process_children(element)
        elif tag == "emphasis":
            return self._process_emphasis(element)
        elif tag == "break":
            return self._process_break(element)
        elif tag == "prosody":
            return self._process_prosody(element)
        elif tag == "lang":
            return self._process_language(element)
        elif tag == "voice":
            return self._process_voice(element)
        elif tag == "phoneme":
            return self._process_phoneme(element)
        elif tag == "sub":
            return self._process_substitution(element)
        elif tag == "say-as":
            return self._process_say_as(element)
        elif tag == "audio":
            return self._process_audio(element)
        elif tag == "mark":
            return self._process_mark(element)
        elif "amazon:effect" in element.tag or tag == "effect":
            return self._process_amazon_effect(element)
        else:
            # Unknown tag - just process children
            return self._process_children(element)

    def _process_children(self, element: ET.Element) -> str:
        """Process all children of an element.

        Args:
            element: Parent element

        Returns:
            Combined SSMD string from all children
        """
        result = []

        # Add text before first child
        if element.text:
            result.append(element.text)

        # Process each child
        for child in element:
            result.append(self._process_element(child))
            # Add text after child
            if child.tail:
                result.append(child.tail)

        return "".join(result)

    def _process_emphasis(self, element: ET.Element) -> str:
        """Convert <emphasis> to *text*, **text**, or _text_.

        Args:
            element: emphasis element

        Returns:
            SSMD emphasis syntax
        """
        content = self._process_children(element)
        level = element.get("level", "moderate")

        if level in ("strong", "x-strong"):
            return f"**{content}**"
        elif level == "reduced":
            return f"_{content}_"
        elif level == "none":
            # Level "none" is rare - use explicit annotation
            return f'[{content}]{{emphasis="none"}}'
        else:  # moderate or default
            return f"*{content}*"

    def _process_break(self, element: ET.Element) -> str:
        """Convert <break> to ... notation.

        Args:
            element: break element

        Returns:
            SSMD break syntax with spaces
        """
        time = element.get("time")
        strength = element.get("strength")

        if time:
            # Parse time value (e.g., "500ms", "2s")
            match = re.match(r"(\d+)(ms|s)", time)
            if match:
                # Breaks have spaces before and after per SSMD spec
                return f" ...{time} "
            # Fallback to 1s if time format is invalid
            return " ...1s "

        elif strength:
            marker = SSML_BREAK_STRENGTH_MAP.get(strength, "...s")
            return f" {marker} "

        # Default to sentence break
        return " ...s "

    def _process_prosody(self, element: ET.Element) -> str:
        """Convert <prosody> to directive or inline annotation.

        Args:
            element: prosody element

        Returns:
            SSMD prosody syntax
        """
        content = self._process_children(element)
        volume = element.get("volume")
        rate = element.get("rate")
        pitch = element.get("pitch")

        # Filter out "medium" default values (ssml-maker adds these)
        if volume == "medium":
            volume = None
        if rate == "medium":
            rate = None
        if pitch == "medium":
            pitch = None

        if not any([volume, rate, pitch]):
            return content

        annotations = []

        if volume:
            annotations.append(f'volume="{volume}"')

        if rate:
            annotations.append(f'rate="{rate}"')

        if pitch:
            annotations.append(f'pitch="{pitch}"')

        if not annotations:
            return content

        is_multiline = "\n" in content.strip() or len(content.strip()) > 80
        if is_multiline:
            attrs = " ".join(annotations)
            return (
                f"<div {attrs}>{{DIRECTIVE_NEWLINE}}"
                f"{content.strip()}{{DIRECTIVE_NEWLINE}}</div>"
            )

        return f"[{content}]{{{' '.join(annotations)}}}"

    def _process_language(self, element: ET.Element) -> str:
        """Convert <lang> to directive or inline annotation.

        Args:
            element: lang element

        Returns:
            SSMD language syntax
        """
        from ssmd.segment import _escape_xml_attr

        content = self._process_children(element)
        lang = element.get("{http://www.w3.org/XML/1998/namespace}lang") or element.get(
            "lang"
        )

        if not lang:
            return content

        simplified = self.STANDARD_LOCALES.get(lang, lang)
        escaped_lang = _escape_xml_attr(simplified)
        is_multiline = "\n" in content.strip() or len(content.strip()) > 80
        if is_multiline:
            return (
                f'<div lang="{escaped_lang}">{{DIRECTIVE_NEWLINE}}'
                f"{content.strip()}{{DIRECTIVE_NEWLINE}}</div>"
            )

        return f'[{content}]{{lang="{escaped_lang}"}}'

    def _process_voice(self, element: ET.Element) -> str:
        """Convert <voice> to directive or annotation syntax.

        Uses directive syntax (<div ...>) for multi-line content,
        and annotation syntax ([text]{voice="name"}) for single-line content.

        Args:
            element: voice element

        Returns:
            SSMD voice syntax
        """
        content = self._process_children(element)

        # Get voice attributes
        name = element.get("name")
        language = element.get("language")
        gender = element.get("gender")
        variant = element.get("variant")

        # Check if content is multi-line (use directive syntax)
        # or single-line (use annotation)
        is_multiline = "\n" in content.strip() or len(content.strip()) > 80

        # Directive syntax can be used for both simple names and complex attrs
        use_directive = is_multiline

        if use_directive:
            # Use block directive syntax for multi-line voice blocks
            parts = []
            if name:
                parts.append(f'voice="{name}"')
            if language:
                parts.append(f'voice-lang="{language}"')
            if gender:
                parts.append(f'gender="{gender}"')
            if variant:
                parts.append(f'variant="{variant}"')

            if parts:
                attrs = " ".join(parts)
                content = content.strip()
                return (
                    f"<div {attrs}>{{DIRECTIVE_NEWLINE}}"
                    f"{content}{{DIRECTIVE_NEWLINE}}</div>"
                )

        # Use inline annotation syntax
        if name:
            # Simple name-only format
            return f'[{content}]{{voice="{name}"}}'
        else:
            # Complex format with language/gender/variant
            parts = []
            if language:
                parts.append(f'voice-lang="{language}"')
            if gender:
                parts.append(f'gender="{gender}"')
            if variant:
                parts.append(f'variant="{variant}"')

            if parts:
                annotation = " ".join(parts)
                return f"[{content}]{{{annotation}}}"

        return content

    def _process_phoneme(self, element: ET.Element) -> str:
        """Convert <phoneme> to [text]{ph="..." alphabet="..."}.

        Args:
            element: phoneme element

        Returns:
            SSMD phoneme syntax
        """
        content = self._process_children(element)
        alphabet = element.get("alphabet", "ipa")
        ph = element.get("ph", "")

        # Use explicit format: [text]{ph="value" alphabet="type"}
        return f'[{content}]{{ph="{ph}" alphabet="{alphabet}"}}'

    def _process_substitution(self, element: ET.Element) -> str:
        """Convert <sub> to [text]{sub="alias"}.

        Args:
            element: sub element

        Returns:
            SSMD substitution syntax
        """
        content = self._process_children(element)
        alias = element.get("alias", "")

        if alias:
            return f'[{content}]{{sub="{alias}"}}'

        return content

    def _process_say_as(self, element: ET.Element) -> str:
        """Convert <say-as> to [text]{as="type"}.

        Args:
            element: say-as element

        Returns:
            SSMD say-as syntax
        """
        content = self._process_children(element)
        interpret_as = element.get("interpret-as", "")
        format_attr = element.get("format")
        detail_attr = element.get("detail")

        # Build annotation string
        parts = [f'as="{interpret_as}"']

        if format_attr:
            parts.append(f'format="{format_attr}"')
        if detail_attr:
            parts.append(f'detail="{detail_attr}"')

        annotation = " ".join(parts)

        if interpret_as:
            return f"[{content}]{{{annotation}}}"

        return content

    def _process_audio(self, element: ET.Element) -> str:
        """Convert <audio> to [desc]{src="url" ...}.

        Args:
            element: audio element

        Returns:
            SSMD audio syntax with attributes
        """
        src = element.get("src", "")

        # Get advanced attributes
        clip_begin = element.get("clipBegin")
        clip_end = element.get("clipEnd")
        speed = element.get("speed")
        repeat_count = element.get("repeatCount")
        repeat_dur = element.get("repeatDur")
        sound_level = element.get("soundLevel")

        # Extract description and alt text
        description = ""
        has_desc_tag = False

        # Look for <desc> child element
        desc_elem = element.find("desc")
        if desc_elem is not None and desc_elem.text:
            description = desc_elem.text
            has_desc_tag = True

        # Get all text content (including text and tail from children)
        content_text = ""
        if element.text:
            content_text = element.text

        # Get tail text from children (after desc)
        for child in element:
            if child.tail:
                content_text += child.tail

        content_text = content_text.strip()

        # If there's no <desc> tag but there is text content,
        # treat the text as description
        if not has_desc_tag and content_text:
            description = content_text

        if not src:
            return description if description else content_text

        pairs = [("src", src)]

        if clip_begin and clip_end:
            pairs.append(("clip", f"{clip_begin}-{clip_end}"))
        if speed:
            pairs.append(("speed", speed))
        if repeat_count:
            pairs.append(("repeat", repeat_count))
        if repeat_dur:
            pairs.append(("repeatDur", repeat_dur))
        if sound_level:
            pairs.append(("level", sound_level))
        if has_desc_tag and content_text:
            pairs.append(("alt", content_text))

        annotation = " ".join([f'{key}="{value}"' for key, value in pairs])

        if description:
            return f"[{description}]{{{annotation}}}"
        return f"[]{{{annotation}}}"

    def _process_mark(self, element: ET.Element) -> str:
        """Convert <mark> to @name.

        Args:
            element: mark element

        Returns:
            SSMD mark syntax with spaces
        """
        name = element.get("name", "")

        if name:
            # Marks have space before and after
            return f" @{name} "

        return ""

    def _process_amazon_effect(self, element: ET.Element) -> str:
        """Convert Amazon effects to [text]{ext="name"}.

        Args:
            element: amazon:effect element

        Returns:
            SSMD extension syntax
        """
        content = self._process_children(element)
        name = element.get("name", "")

        # Map Amazon effect names to SSMD extensions
        effect_map = {
            "whispered": "whisper",
            "drc": "drc",
        }

        ext_name = effect_map.get(name, name)

        if ext_name:
            return f'[{content}]{{ext="{ext_name}"}}'

        return content

    def _clean_whitespace(self, text: str) -> str:
        """Clean up excessive whitespace while preserving paragraph breaks.

        Args:
            text: Text to clean

        Returns:
            Cleaned text
        """
        # Preserve paragraph breaks (double newlines)
        text = text.replace("{DIRECTIVE_NEWLINE}", "\n")
        parts = re.split(r"\n\n+", text)

        cleaned_parts = []
        for part in parts:
            # Collapse multiple spaces, tabs, and single newlines
            cleaned = re.sub(r"[ \t\n]+", " ", part)
            cleaned = cleaned.strip()
            if cleaned:
                cleaned_parts.append(cleaned)

        # Join with double newlines for paragraphs
        return "\n\n".join(cleaned_parts)
