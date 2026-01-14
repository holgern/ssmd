"""Segment - A piece of text with SSMD attributes.

A Segment represents a portion of text with specific formatting and processing
attributes. Segments are combined to form sentences.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from ssmd.ssml_conversions import (
    PROSODY_PITCH_MAP as PITCH_MAP,
)
from ssmd.ssml_conversions import (
    PROSODY_RATE_MAP as RATE_MAP,
)
from ssmd.ssml_conversions import (
    PROSODY_VOLUME_MAP as VOLUME_MAP,
)
from ssmd.ssml_conversions import (
    SSMD_BREAK_STRENGTH_MAP,
)
from ssmd.ssml_conversions import (
    SSMD_PITCH_SHORTHAND as PITCH_TO_SSMD,
)
from ssmd.ssml_conversions import (
    SSMD_RATE_SHORTHAND as RATE_TO_SSMD,
)
from ssmd.ssml_conversions import (
    SSMD_VOLUME_SHORTHAND as VOLUME_TO_SSMD,
)
from ssmd.types import (
    AudioAttrs,
    BreakAttrs,
    PhonemeAttrs,
    ProsodyAttrs,
    SayAsAttrs,
    VoiceAttrs,
)

if TYPE_CHECKING:
    from ssmd.capabilities import TTSCapabilities


# Language code defaults (2-letter code -> full locale)
LANGUAGE_DEFAULTS = {
    "en": "en-US",
    "de": "de-DE",
    "fr": "fr-FR",
    "es": "es-ES",
    "it": "it-IT",
    "pt": "pt-PT",
    "ru": "ru-RU",
    "zh": "zh-CN",
    "ja": "ja-JP",
    "ko": "ko-KR",
    "ar": "ar-SA",
    "hi": "hi-IN",
    "nl": "nl-NL",
    "pl": "pl-PL",
    "sv": "sv-SE",
    "da": "da-DK",
    "no": "no-NO",
    "fi": "fi-FI",
}


# Default extension handlers
DEFAULT_EXTENSIONS = {
    "whisper": lambda text: f'<amazon:effect name="whispered">{text}</amazon:effect>',
    "drc": lambda text: f'<amazon:effect name="drc">{text}</amazon:effect>',
}


def _escape_xml_attr(value: str) -> str:
    """Escape a value for use in an XML attribute.

    Args:
        value: The attribute value to escape

    Returns:
        Escaped string safe for XML attribute
    """
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _escape_xml_text(value: str) -> str:
    """Escape a value for use in XML text content.

    Args:
        value: The text content to escape

    Returns:
        Escaped string safe for XML text
    """
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# X-SAMPA to IPA conversion table (lazy-loaded)
_XSAMPA_TABLE: dict[str, str] | None = None


def _load_xsampa_table() -> dict[str, str]:
    """Load X-SAMPA to IPA conversion table."""
    global _XSAMPA_TABLE
    if _XSAMPA_TABLE is not None:
        return _XSAMPA_TABLE

    table = {}
    # Try both old and new locations
    table_paths = [
        Path(__file__).parent / "xsampa_to_ipa.txt",
        Path(__file__).parent / "annotations" / "xsampa_to_ipa.txt",
    ]

    for table_file in table_paths:
        if table_file.exists():
            with open(table_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        parts = line.split(maxsplit=1)
                        if len(parts) == 2:
                            xsampa, ipa = parts
                            table[xsampa] = ipa
            break

    _XSAMPA_TABLE = table
    return table


def xsampa_to_ipa(xsampa: str) -> str:
    """Convert X-SAMPA notation to IPA.

    Args:
        xsampa: X-SAMPA phoneme string

    Returns:
        IPA phoneme string
    """
    table = _load_xsampa_table()

    # Sort by length (longest first) for proper replacement
    sorted_keys = sorted(table.keys(), key=len, reverse=True)

    result = xsampa
    for x in sorted_keys:
        result = result.replace(x, table[x])

    return result


def expand_language_code(code: str) -> str:
    """Expand 2-letter language code to full BCP-47 locale.

    Args:
        code: Language code (e.g., "en", "en-US")

    Returns:
        Full locale code (e.g., "en-US")
    """
    if code in LANGUAGE_DEFAULTS:
        return LANGUAGE_DEFAULTS[code]
    return code


@dataclass
class Segment:
    """A segment of text with SSMD features.

    Represents a portion of text with specific formatting and processing attributes.
    Segments are the atomic units of SSMD content.

    Attributes:
        text: Raw text content
        emphasis: Emphasis level (True/"moderate", "strong", "reduced", "none", False)
        prosody: Volume, rate, pitch settings
        language: Language code for this segment
        voice: Voice settings for this segment
        say_as: Text interpretation hints
        substitution: Replacement text (alias)
        phoneme: IPA pronunciation
        audio: Audio file to play
        extension: Platform-specific extension name
        breaks_before: Pauses before this segment
        breaks_after: Pauses after this segment
        marks_before: Event markers before this segment
        marks_after: Event markers after this segment
    """

    text: str

    # Styling features
    emphasis: bool | str = False  # True/"moderate", "strong", "reduced", "none"
    prosody: ProsodyAttrs | None = None
    language: str | None = None
    voice: VoiceAttrs | None = None

    # Text transformation features
    say_as: SayAsAttrs | None = None
    substitution: str | None = None
    phoneme: PhonemeAttrs | None = None

    # Media
    audio: AudioAttrs | None = None

    # Platform-specific
    extension: str | None = None

    # Breaks and marks
    breaks_before: list[BreakAttrs] = field(default_factory=list)
    breaks_after: list[BreakAttrs] = field(default_factory=list)
    marks_before: list[str] = field(default_factory=list)
    marks_after: list[str] = field(default_factory=list)

    def to_ssml(
        self,
        capabilities: "TTSCapabilities | None" = None,
        extensions: dict | None = None,
    ) -> str:
        """Convert segment to SSML.

        Args:
            capabilities: TTS engine capabilities for filtering
            extensions: Custom extension handlers

        Returns:
            SSML string
        """
        result = ""

        # Add marks before
        if not capabilities or capabilities.mark:
            for mark in self.marks_before:
                mark_escaped = _escape_xml_attr(mark)
                result += f'<mark name="{mark_escaped}"/>'

        # Add breaks before
        if not capabilities or capabilities.break_tags:
            for brk in self.breaks_before:
                result += self._break_to_ssml(brk)

        # Build content with wrappers
        content = self._build_content_ssml(capabilities, extensions)
        result += content

        # Add breaks after
        if not capabilities or capabilities.break_tags:
            for brk in self.breaks_after:
                result += self._break_to_ssml(brk)

        # Add marks after
        if not capabilities or capabilities.mark:
            for mark in self.marks_after:
                mark_escaped = _escape_xml_attr(mark)
                result += f'<mark name="{mark_escaped}"/>'

        return result

    def _build_content_ssml(
        self,
        capabilities: "TTSCapabilities | None",
        extensions: dict | None,
    ) -> str:
        """Build the main content SSML with all wrappers.

        Args:
            capabilities: TTS capabilities for filtering
            extensions: Custom extension handlers

        Returns:
            SSML content string
        """
        # Handle audio (replaces text)
        if self.audio:
            if capabilities and not capabilities.audio:
                return _escape_xml_text(self.text)  # Fallback to description
            return self._audio_to_ssml(self.audio)

        # Start with escaped text
        content = _escape_xml_text(self.text)

        # Apply substitution
        if self.substitution:
            if not capabilities or capabilities.substitution:
                alias = _escape_xml_attr(self.substitution)
                content = f'<sub alias="{alias}">{content}</sub>'

        # Apply phoneme
        elif self.phoneme:
            if not capabilities or capabilities.phoneme:
                ph = self.phoneme.ph
                # Convert X-SAMPA to IPA if needed
                if self.phoneme.alphabet.lower() in ("x-sampa", "sampa"):
                    ph = xsampa_to_ipa(ph)
                ph = _escape_xml_attr(ph)
                content = f'<phoneme alphabet="ipa" ph="{ph}">{content}</phoneme>'

        # Apply say-as
        elif self.say_as:
            if not capabilities or capabilities.say_as:
                content = self._say_as_to_ssml(self.say_as, content)

        # Apply emphasis
        if self.emphasis:
            if not capabilities or capabilities.emphasis:
                content = self._emphasis_to_ssml(content)

        # Apply prosody
        if self.prosody:
            if not capabilities or capabilities.prosody:
                content = self._prosody_to_ssml(self.prosody, content, capabilities)

        # Apply language
        if self.language:
            if not capabilities or capabilities.language:
                lang = expand_language_code(self.language)
                content = f'<lang xml:lang="{lang}">{content}</lang>'

        # Apply voice (inline) - note: TTSCapabilities doesn't have voice attr
        # Voice is always enabled as it's fundamental to TTS
        if self.voice:
            content = self._voice_to_ssml(self.voice, content)

        # Apply extension
        if self.extension:
            ext_handlers = {**DEFAULT_EXTENSIONS, **(extensions or {})}
            handler = ext_handlers.get(self.extension)
            if handler:
                content = handler(content)

        return content

    def _emphasis_to_ssml(self, content: str) -> str:
        """Convert emphasis to SSML."""
        if self.emphasis is True or self.emphasis == "moderate":
            return f"<emphasis>{content}</emphasis>"
        elif self.emphasis == "strong":
            return f'<emphasis level="strong">{content}</emphasis>'
        elif self.emphasis == "reduced":
            return f'<emphasis level="reduced">{content}</emphasis>'
        elif self.emphasis == "none":
            return f'<emphasis level="none">{content}</emphasis>'
        return content

    def _prosody_to_ssml(
        self,
        prosody: ProsodyAttrs,
        content: str,
        capabilities: "TTSCapabilities | None",
    ) -> str:
        """Convert prosody to SSML."""
        attrs = []

        if prosody.volume and (not capabilities or capabilities.prosody_volume):
            # Map numeric to named if needed
            vol = VOLUME_MAP.get(prosody.volume, prosody.volume)
            vol = _escape_xml_attr(vol)
            attrs.append(f'volume="{vol}"')

        if prosody.rate and (not capabilities or capabilities.prosody_rate):
            rate = RATE_MAP.get(prosody.rate, prosody.rate)
            rate = _escape_xml_attr(rate)
            attrs.append(f'rate="{rate}"')

        if prosody.pitch and (not capabilities or capabilities.prosody_pitch):
            pitch = PITCH_MAP.get(prosody.pitch, prosody.pitch)
            pitch = _escape_xml_attr(pitch)
            attrs.append(f'pitch="{pitch}"')

        if attrs:
            return f"<prosody {' '.join(attrs)}>{content}</prosody>"
        return content

    def _voice_to_ssml(self, voice: VoiceAttrs, content: str) -> str:
        """Convert voice to SSML."""
        attrs = []

        if voice.name:
            name = _escape_xml_attr(voice.name)
            attrs.append(f'name="{name}"')
        else:
            if voice.language:
                lang = _escape_xml_attr(voice.language)
                attrs.append(f'language="{lang}"')
            if voice.gender:
                gender = _escape_xml_attr(voice.gender)
                attrs.append(f'gender="{gender}"')
            if voice.variant:
                variant = _escape_xml_attr(str(voice.variant))
                attrs.append(f'variant="{variant}"')

        if attrs:
            return f"<voice {' '.join(attrs)}>{content}</voice>"
        return content

    def _say_as_to_ssml(self, say_as: SayAsAttrs, content: str) -> str:
        """Convert say-as to SSML."""
        interpret = _escape_xml_attr(say_as.interpret_as)
        attrs = [f'interpret-as="{interpret}"']

        if say_as.format:
            fmt = _escape_xml_attr(say_as.format)
            attrs.append(f'format="{fmt}"')
        if say_as.detail:
            detail = _escape_xml_attr(str(say_as.detail))
            attrs.append(f'detail="{detail}"')

        return f"<say-as {' '.join(attrs)}>{content}</say-as>"

    def _audio_to_ssml(self, audio: AudioAttrs) -> str:
        """Convert audio to SSML."""
        src = _escape_xml_attr(audio.src)
        attrs = [f'src="{src}"']

        if audio.clip_begin:
            cb = _escape_xml_attr(audio.clip_begin)
            attrs.append(f'clipBegin="{cb}"')
        if audio.clip_end:
            ce = _escape_xml_attr(audio.clip_end)
            attrs.append(f'clipEnd="{ce}"')
        if audio.speed:
            speed = _escape_xml_attr(audio.speed)
            attrs.append(f'speed="{speed}"')
        if audio.repeat_count:
            rc = _escape_xml_attr(str(audio.repeat_count))
            attrs.append(f'repeatCount="{rc}"')
        if audio.repeat_dur:
            rd = _escape_xml_attr(audio.repeat_dur)
            attrs.append(f'repeatDur="{rd}"')
        if audio.sound_level:
            sl = _escape_xml_attr(audio.sound_level)
            attrs.append(f'soundLevel="{sl}"')

        desc = f"<desc>{self.text}</desc>" if self.text else ""
        alt = _escape_xml_text(audio.alt_text) if audio.alt_text else ""

        return f"<audio {' '.join(attrs)}>{desc}{alt}</audio>"

    def _break_to_ssml(self, brk: BreakAttrs) -> str:
        """Convert break to SSML."""
        if brk.time:
            time = _escape_xml_attr(brk.time)
            return f'<break time="{time}"/>'
        elif brk.strength:
            strength = _escape_xml_attr(brk.strength)
            return f'<break strength="{strength}"/>'
        return "<break/>"

    def to_ssmd(self) -> str:
        """Convert segment to SSMD markdown.

        Returns:
            SSMD string
        """
        result = ""

        # Add marks before
        for mark in self.marks_before:
            result += f"@{mark} "

        # Add breaks before
        for brk in self.breaks_before:
            result += self._break_to_ssmd(brk) + " "

        # Build content
        content = self._build_content_ssmd()
        result += content

        # Add breaks after
        for brk in self.breaks_after:
            result += " " + self._break_to_ssmd(brk)

        # Add marks after
        for mark in self.marks_after:
            result += f" @{mark}"

        return result

    def _build_content_ssmd(self) -> str:  # noqa: C901
        """Build SSMD content with markup."""
        text = self.text

        # Handle audio
        if self.audio:
            return self._audio_to_ssmd(self.audio)

        # Collect annotations
        annotations = []

        # Language
        if self.language:
            annotations.append(self.language)

        # Voice
        if self.voice:
            voice_str = self._voice_to_ssmd_annotation(self.voice)
            if voice_str:
                annotations.append(voice_str)

        # Say-as
        if self.say_as:
            sa_str = f"as: {self.say_as.interpret_as}"
            if self.say_as.format:
                sa_str += f', format: "{self.say_as.format}"'
            if self.say_as.detail:
                sa_str += f", detail: {self.say_as.detail}"
            annotations.append(sa_str)

        # Substitution
        if self.substitution:
            annotations.append(f"sub: {self.substitution}")

        # Phoneme - include alphabet
        if self.phoneme:
            annotations.append(
                f"ph: {self.phoneme.ph}, alphabet: {self.phoneme.alphabet}"
            )

        # Extension
        if self.extension:
            annotations.append(f"ext: {self.extension}")

        # Determine if we can use prosody shorthand
        # Shorthand is only used when: single prosody attr AND no other annotations
        use_prosody_shorthand = False
        if self.prosody and not annotations:
            # Check if only one prosody attribute is set
            attrs_set = sum(
                [
                    1 if self.prosody.volume else 0,
                    1 if self.prosody.rate else 0,
                    1 if self.prosody.pitch else 0,
                ]
            )
            if attrs_set == 1:
                # Check if the value has a shorthand
                if self.prosody.volume and self.prosody.volume in VOLUME_TO_SSMD:
                    use_prosody_shorthand = True
                elif self.prosody.rate and self.prosody.rate in RATE_TO_SSMD:
                    use_prosody_shorthand = True
                elif self.prosody.pitch and self.prosody.pitch in PITCH_TO_SSMD:
                    use_prosody_shorthand = True

        # Add prosody to annotations if not using shorthand
        if self.prosody and not use_prosody_shorthand:
            prosody_str = self._prosody_to_ssmd_annotation(self.prosody)
            if prosody_str:
                annotations.append(prosody_str)

        # Apply emphasis shorthand or include in annotations
        if self.emphasis:
            if annotations:
                # Use annotation form
                if self.emphasis == "none":
                    annotations.append("emphasis: none")
                # Other emphasis levels handled by shorthand below
            else:
                # Use shorthand
                if self.emphasis is True or self.emphasis == "moderate":
                    text = f"*{text}*"
                elif self.emphasis == "strong":
                    text = f"**{text}**"
                elif self.emphasis == "reduced":
                    text = f"_{text}_"
                elif self.emphasis == "none":
                    annotations.append("emphasis: none")

        # If we have annotations, wrap in [text](annotations)
        if annotations:
            # If we also have emphasis shorthand, wrap the emphasized text
            if (
                self.emphasis
                and self.emphasis != "none"
                and not any("emphasis:" in a for a in annotations)
            ):
                if self.emphasis is True or self.emphasis == "moderate":
                    text = f"*{text}*"
                elif self.emphasis == "strong":
                    text = f"**{text}**"
                elif self.emphasis == "reduced":
                    text = f"_{text}_"
            return f"[{text}]({', '.join(annotations)})"

        # Apply prosody shorthand if no annotations
        if use_prosody_shorthand and self.prosody:
            text = self._apply_prosody_shorthand(self.prosody, text)

        return text

    def _prosody_to_ssmd_annotation(self, prosody: ProsodyAttrs) -> str:
        """Convert prosody to SSMD annotation format."""
        parts = []

        if prosody.volume:
            # Check if it's a relative value
            if prosody.volume.startswith(("+", "-")) or prosody.volume.endswith("dB"):
                parts.append(f"v: {prosody.volume}")
            else:
                # Map to numeric
                vol_map = {v: k for k, v in VOLUME_MAP.items()}
                num = vol_map.get(prosody.volume, prosody.volume)
                parts.append(f"v: {num}")

        if prosody.rate:
            if prosody.rate.endswith("%"):
                parts.append(f"r: {prosody.rate}")
            else:
                rate_map = {v: k for k, v in RATE_MAP.items()}
                num = rate_map.get(prosody.rate, prosody.rate)
                parts.append(f"r: {num}")

        if prosody.pitch:
            if prosody.pitch.startswith(("+", "-")) or prosody.pitch.endswith("%"):
                parts.append(f"p: {prosody.pitch}")
            else:
                pitch_map = {v: k for k, v in PITCH_MAP.items()}
                num = pitch_map.get(prosody.pitch, prosody.pitch)
                parts.append(f"p: {num}")

        return ", ".join(parts)

    def _apply_prosody_shorthand(self, prosody: ProsodyAttrs, text: str) -> str:
        """Apply prosody shorthand notation."""
        # Only one attribute at a time for shorthand
        attrs_set = sum(
            [
                1 if prosody.volume else 0,
                1 if prosody.rate else 0,
                1 if prosody.pitch else 0,
            ]
        )

        if attrs_set != 1:
            # Multiple attrs, use annotation
            ann = self._prosody_to_ssmd_annotation(prosody)
            if ann:
                return f"[{text}]({ann})"
            return text

        if prosody.volume:
            wrap = VOLUME_TO_SSMD.get(prosody.volume)
            if wrap:
                return f"{wrap[0]}{text}{wrap[1]}"

        if prosody.rate:
            wrap = RATE_TO_SSMD.get(prosody.rate)
            if wrap:
                return f"{wrap[0]}{text}{wrap[1]}"

        if prosody.pitch:
            wrap = PITCH_TO_SSMD.get(prosody.pitch)
            if wrap:
                return f"{wrap[0]}{text}{wrap[1]}"

        return text

    def _voice_to_ssmd_annotation(self, voice: VoiceAttrs) -> str:
        """Convert voice to SSMD annotation format."""
        if voice.name:
            return f"voice: {voice.name}"
        else:
            parts = []
            if voice.language:
                parts.append(f"voice: {voice.language}")
            if voice.gender:
                parts.append(f"gender: {voice.gender}")
            if voice.variant:
                parts.append(f"variant: {voice.variant}")
            return ", ".join(parts)

    def _audio_to_ssmd(self, audio: AudioAttrs) -> str:
        """Convert audio to SSMD format."""
        parts = [audio.src]

        # Add attributes
        if audio.clip_begin and audio.clip_end:
            parts.append(f"clip: {audio.clip_begin}-{audio.clip_end}")
        if audio.speed:
            parts.append(f"speed: {audio.speed}")
        if audio.repeat_count:
            parts.append(f"repeat: {audio.repeat_count}")
        if audio.repeat_dur:
            parts.append(f"repeatDur: {audio.repeat_dur}")
        if audio.sound_level:
            parts.append(f"level: {audio.sound_level}")

        # Add alt text
        if audio.alt_text:
            parts.append(audio.alt_text)

        # Use self.text as description (can be empty)
        # Audio attributes are space-separated per spec
        return f"[{self.text}]({' '.join(parts)})"

    def _break_to_ssmd(self, brk: BreakAttrs) -> str:
        """Convert break to SSMD format."""
        if brk.time:
            return f"...{brk.time}"
        elif brk.strength:
            return SSMD_BREAK_STRENGTH_MAP.get(brk.strength, "...s")
        return "...s"

    def to_text(self) -> str:
        """Convert segment to plain text.

        Returns:
            Plain text with all markup removed
        """
        if self.audio:
            return self.text  # Return description
        if self.substitution:
            return self.substitution  # Return the spoken alias
        return self.text
