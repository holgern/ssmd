"""SSML to SSMD converter - reverse conversion."""

import re
import xml.etree.ElementTree as ET
from typing import Any


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

    # Prosody value mappings (reverse of SSMD to SSML)
    VOLUME_TO_SSMD = {
        "silent": ("~", "~"),
        "x-soft": ("--", "--"),
        "soft": ("-", "-"),
        "medium": ("", ""),  # Default, no markup
        "loud": ("+", "+"),
        "x-loud": ("++", "++"),
    }

    RATE_TO_SSMD = {
        "x-slow": ("<<", "<<"),
        "slow": ("<", "<"),
        "medium": ("", ""),  # Default
        "fast": (">", ">"),
        "x-fast": (">>", ">>"),
    }

    PITCH_TO_SSMD = {
        "x-low": ("vv", "vv"),
        "low": ("v", "v"),
        "medium": ("", ""),  # Default
        "high": ("^", "^"),
        "x-high": ("^^", "^^"),
    }

    # Break strength mappings
    BREAK_STRENGTH_TO_SSMD = {
        "none": "",
        "x-weak": ".",
        "weak": ".",
        "medium": "...",
        "strong": "...s",
        "x-strong": "...p",
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
            SSMD markdown string

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

        # Restore voice directive newlines (protected during whitespace cleaning)
        result = result.replace("{VOICE_NEWLINE}", "\n")

        return result.strip()

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
        """Convert <emphasis> to *text*.

        Args:
            element: emphasis element

        Returns:
            SSMD emphasis syntax
        """
        content = self._process_children(element)
        level = element.get("level", "moderate")

        if level in ("strong", "x-strong"):
            return f"**{content}**"
        else:
            return f"*{content}*"

    def _process_break(self, element: ET.Element) -> str:
        """Convert <break> to ... notation.

        Args:
            element: break element

        Returns:
            SSMD break syntax
        """
        time = element.get("time")
        strength = element.get("strength")

        if time:
            # Parse time value (e.g., "500ms", "2s")
            match = re.match(r"(\d+)(ms|s)", time)
            if match:
                value, unit = match.groups()
                # Always use explicit time notation
                return f"...{time}"
            # Fallback to 1s if time format is invalid
            return "...1s"

        elif strength:
            return self.BREAK_STRENGTH_TO_SSMD.get(strength, "...s")

        # Default to sentence break
        return "...s"

    def _process_prosody(self, element: ET.Element) -> str:
        """Convert <prosody> to SSMD prosody syntax.

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

        # Count non-default attributes
        attr_count = sum([1 for v in [volume, rate, pitch] if v is not None])

        # Try shorthand notation first (single non-default attribute)
        if attr_count == 1:
            if volume and not rate and not pitch:
                wrap = self.VOLUME_TO_SSMD.get(volume)
                if wrap and wrap[0]:  # Has shorthand
                    return f"{wrap[0]}{content}{wrap[1]}"

            if rate and not volume and not pitch:
                wrap = self.RATE_TO_SSMD.get(rate)
                if wrap and wrap[0]:
                    return f"{wrap[0]}{content}{wrap[1]}"

            if pitch and not volume and not rate:
                wrap = self.PITCH_TO_SSMD.get(pitch)
                if wrap and wrap[0]:
                    return f"{wrap[0]}{content}{wrap[1]}"

        # No attributes set - return plain content
        if attr_count == 0:
            return content

        # Multiple attributes or numeric values - use annotation syntax
        annotations = []

        if volume:
            # Map to numeric scale (1-5)
            volume_map = {
                "silent": 0,
                "x-soft": 1,
                "soft": 2,
                "medium": 3,
                "loud": 4,
                "x-loud": 5,
            }
            if volume in volume_map:
                annotations.append(f"v: {volume_map[volume]}")
            elif volume.startswith(("+", "-")) or volume.endswith("dB"):
                annotations.append(f"v: {volume}")

        if rate:
            rate_map = {"x-slow": 1, "slow": 2, "medium": 3, "fast": 4, "x-fast": 5}
            if rate in rate_map:
                annotations.append(f"r: {rate_map[rate]}")
            elif rate.endswith("%"):
                annotations.append(f"r: {rate}")

        if pitch:
            pitch_map = {"x-low": 1, "low": 2, "medium": 3, "high": 4, "x-high": 5}
            if pitch in pitch_map:
                annotations.append(f"p: {pitch_map[pitch]}")
            elif pitch.startswith(("+", "-")) or pitch.endswith("Hz"):
                annotations.append(f"p: {pitch}")

        if annotations:
            return f"[{content}]({', '.join(annotations)})"

        return content

    def _process_language(self, element: ET.Element) -> str:
        """Convert <lang> to [text](lang).

        Args:
            element: lang element

        Returns:
            SSMD language syntax
        """
        content = self._process_children(element)
        lang = element.get("{http://www.w3.org/XML/1998/namespace}lang") or element.get(
            "lang"
        )

        if lang:
            # Check if it's in our standard locales mapping
            simplified = self.STANDARD_LOCALES.get(lang)
            if simplified:
                return f"[{content}]({simplified})"
            # Otherwise use full locale
            return f"[{content}]({lang})"

        return content

    def _process_voice(self, element: ET.Element) -> str:
        """Convert <voice> to directive or annotation syntax.

        Uses directive syntax (@voice: name) for multi-line content,
        and annotation syntax ([text](voice: name)) for single-line content.

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
            # Use block directive syntax for cleaner multi-line voice blocks
            # Build parameter string
            if name:
                params = name
            else:
                # Build language, gender, variant params
                parts = []
                if language:
                    parts.append(language)
                if gender:
                    parts.append(f"gender: {gender}")
                if variant:
                    parts.append(f"variant: {variant}")
                params = ", ".join(parts) if parts else ""

            if params:
                # Use a placeholder to protect the newline from whitespace cleaning
                return f"@voice: {params}{{VOICE_NEWLINE}}{content.strip()}"

        # Use inline annotation syntax
        if name:
            # Simple name-only format
            return f"[{content}](voice: {name})"
        else:
            # Complex format with language/gender/variant
            parts = []
            if language:
                parts.append(f"voice: {language}")
            if gender:
                parts.append(f"gender: {gender}")
            if variant:
                parts.append(f"variant: {variant}")

            if parts:
                annotation = ", ".join(parts)
                return f"[{content}]({annotation})"

        return content

    def _process_phoneme(self, element: ET.Element) -> str:
        """Convert <phoneme> to [text](ph: ...).

        Args:
            element: phoneme element

        Returns:
            SSMD phoneme syntax
        """
        content = self._process_children(element)
        alphabet = element.get("alphabet", "ipa")
        ph = element.get("ph", "")

        if alphabet == "ipa":
            return f"[{content}](ipa: {ph})"
        elif alphabet == "x-sampa":
            return f"[{content}](ph: {ph})"
        else:
            return f"[{content}]({alphabet}: {ph})"

    def _process_substitution(self, element: ET.Element) -> str:
        """Convert <sub> to [text](sub: alias).

        Args:
            element: sub element

        Returns:
            SSMD substitution syntax
        """
        content = self._process_children(element)
        alias = element.get("alias", "")

        if alias:
            return f"[{content}](sub: {alias})"

        return content

    def _process_say_as(self, element: ET.Element) -> str:
        """Convert <say-as> to [text](as: type).

        Args:
            element: say-as element

        Returns:
            SSMD say-as syntax
        """
        content = self._process_children(element)
        interpret_as = element.get("interpret-as", "")
        format_attr = element.get("format")

        if format_attr:
            return f'[{content}](as: {interpret_as}, format: "{format_attr}")'
        elif interpret_as:
            return f"[{content}](as: {interpret_as})"

        return content

    def _process_audio(self, element: ET.Element) -> str:
        """Convert <audio> to [desc](url.mp3 alt).

        Args:
            element: audio element

        Returns:
            SSMD audio syntax
        """
        src = element.get("src", "")
        alt_text = self._process_children(element)

        if src:
            if alt_text:
                return f"[{alt_text}]({src} alt)"
            else:
                return f"[]({src})"

        return alt_text

    def _process_mark(self, element: ET.Element) -> str:
        """Convert <mark> to @name.

        Args:
            element: mark element

        Returns:
            SSMD mark syntax
        """
        name = element.get("name", "")

        if name:
            return f"@{name}"

        return ""

    def _process_amazon_effect(self, element: ET.Element) -> str:
        """Convert Amazon effects to [text](ext: name).

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
            return f"[{content}](ext: {ext_name})"

        return content

    def _clean_whitespace(self, text: str) -> str:
        """Clean up excessive whitespace while preserving paragraph breaks.

        Args:
            text: Text to clean

        Returns:
            Cleaned text
        """
        # Preserve paragraph breaks (double newlines)
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
