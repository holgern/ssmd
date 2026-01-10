"""TTS capability definitions and presets.

This module defines which SSML features are supported by various TTS engines
and provides capability-based filtering for SSMD processing.
"""

from typing import Any


class TTSCapabilities:
    """Define TTS engine capabilities.

    This class allows you to specify which SSML features your TTS engine
    supports. Unsupported features will be automatically stripped to plain text.

    Example:
        >>> # Basic TTS with minimal support
        >>> caps = TTSCapabilities(
        ...     emphasis=False,
        ...     break_tags=True,
        ...     prosody=False
        ... )
        >>>
        >>> parser = SSMD(capabilities=caps)
        >>> ssml = parser.to_ssml("Hello *world*!")
        >>> # Output: <speak><p>Hello world!</p></speak>
        >>> # (emphasis stripped because not supported)
    """

    def __init__(
        self,
        # Core features
        emphasis: bool = True,
        break_tags: bool = True,
        paragraph: bool = True,
        # Language & pronunciation
        language: bool = True,
        phoneme: bool = True,
        substitution: bool = True,
        # Prosody (volume, rate, pitch)
        prosody: bool = True,
        prosody_volume: bool = True,
        prosody_rate: bool = True,
        prosody_pitch: bool = True,
        # Advanced features
        say_as: bool = True,
        audio: bool = True,
        mark: bool = True,
        # Extensions (platform-specific)
        extensions: dict[str, bool] | None = None,
        # Sentence and heading support
        sentence_tags: bool = True,
        heading_emphasis: bool = True,
    ):
        """Initialize TTS capabilities.

        Args:
            emphasis: Support for <emphasis> tags
            break_tags: Support for <break> tags
            paragraph: Support for <p> tags
            language: Support for <lang> tags
            phoneme: Support for <phoneme> tags
            substitution: Support for <sub> tags
            prosody: Support for <prosody> tags (general)
            prosody_volume: Support for volume attribute
            prosody_rate: Support for rate attribute
            prosody_pitch: Support for pitch attribute
            say_as: Support for <say-as> tags
            audio: Support for <audio> tags
            mark: Support for <mark> tags
            extensions: Dict of extension names and their support
            sentence_tags: Support for <s> tags
            heading_emphasis: Support for heading emphasis
        """
        self.emphasis = emphasis
        self.break_tags = break_tags
        self.paragraph = paragraph
        self.language = language
        self.phoneme = phoneme
        self.substitution = substitution
        self.prosody = prosody
        self.prosody_volume = prosody_volume and prosody
        self.prosody_rate = prosody_rate and prosody
        self.prosody_pitch = prosody_pitch and prosody
        self.say_as = say_as
        self.audio = audio
        self.mark = mark
        self.extensions = extensions or {}
        self.sentence_tags = sentence_tags
        self.heading_emphasis = heading_emphasis

    def to_config(self) -> dict[str, Any]:
        """Convert capabilities to SSMD config.

        Returns:
            Configuration dict for SSMD converter
        """
        config: dict[str, Any] = {
            "skip": [],
            "capabilities": self,
        }

        # Skip processors for unsupported features
        if not self.emphasis:
            config["skip"].append("emphasis")
        if not self.break_tags:
            config["skip"].append("break")
        if not self.paragraph:
            config["skip"].append("paragraph")
        if not self.mark:
            config["skip"].append("mark")

        # Prosody is handled specially (selective attributes)
        if not self.prosody:
            config["skip"].append("prosody")

        # Headings handled by modifying heading_levels
        if not self.heading_emphasis:
            config["heading_levels"] = {}  # No heading processing

        return config

    def supports_extension(self, extension_name: str) -> bool:
        """Check if an extension is supported.

        Args:
            extension_name: Name of the extension

        Returns:
            True if supported
        """
        return self.extensions.get(extension_name, False)


# Preset capability definitions for common TTS engines
ESPEAK_CAPABILITIES = TTSCapabilities(
    emphasis=False,  # eSpeak doesn't support emphasis
    break_tags=True,
    paragraph=False,  # eSpeak treats paragraphs as plain text
    language=True,
    phoneme=True,  # eSpeak has good phoneme support
    substitution=False,
    prosody=True,
    prosody_volume=True,
    prosody_rate=True,
    prosody_pitch=True,
    say_as=False,
    audio=False,  # No audio file support
    mark=False,
    sentence_tags=False,
    heading_emphasis=False,
)

PYTTSX3_CAPABILITIES = TTSCapabilities(
    emphasis=False,  # pyttsx3 has minimal SSML support
    break_tags=False,
    paragraph=False,
    language=False,  # Voice selection, not SSML
    phoneme=False,
    substitution=False,
    prosody=True,  # Via properties, not SSML
    prosody_volume=True,
    prosody_rate=True,
    prosody_pitch=False,
    say_as=False,
    audio=False,
    mark=False,
    sentence_tags=False,
    heading_emphasis=False,
)

GOOGLE_TTS_CAPABILITIES = TTSCapabilities(
    emphasis=True,
    break_tags=True,
    paragraph=True,
    language=True,
    phoneme=True,
    substitution=True,
    prosody=True,
    prosody_volume=True,
    prosody_rate=True,
    prosody_pitch=True,
    say_as=True,
    audio=True,
    mark=True,
    sentence_tags=True,
    heading_emphasis=True,
)

AMAZON_POLLY_CAPABILITIES = TTSCapabilities(
    emphasis=True,
    break_tags=True,
    paragraph=True,
    language=True,
    phoneme=True,
    substitution=True,
    prosody=True,
    prosody_volume=True,
    prosody_rate=True,
    prosody_pitch=True,
    say_as=True,
    audio=False,  # Limited audio support
    mark=True,
    extensions={"whisper": True, "drc": True},  # Amazon-specific
    sentence_tags=True,
    heading_emphasis=True,
)

AZURE_TTS_CAPABILITIES = TTSCapabilities(
    emphasis=True,
    break_tags=True,
    paragraph=True,
    language=True,
    phoneme=True,
    substitution=True,
    prosody=True,
    prosody_volume=True,
    prosody_rate=True,
    prosody_pitch=True,
    say_as=True,
    audio=True,
    mark=True,
    sentence_tags=True,
    heading_emphasis=True,
)

# Minimal fallback (plain text only)
MINIMAL_CAPABILITIES = TTSCapabilities(
    emphasis=False,
    break_tags=False,
    paragraph=False,
    language=False,
    phoneme=False,
    substitution=False,
    prosody=False,
    say_as=False,
    audio=False,
    mark=False,
    sentence_tags=False,
    heading_emphasis=False,
)

# Full SSML support (reference)
FULL_CAPABILITIES = TTSCapabilities()


# Preset lookup
PRESETS: dict[str, TTSCapabilities] = {
    "espeak": ESPEAK_CAPABILITIES,
    "pyttsx3": PYTTSX3_CAPABILITIES,
    "google": GOOGLE_TTS_CAPABILITIES,
    "polly": AMAZON_POLLY_CAPABILITIES,
    "amazon": AMAZON_POLLY_CAPABILITIES,
    "azure": AZURE_TTS_CAPABILITIES,
    "microsoft": AZURE_TTS_CAPABILITIES,
    "minimal": MINIMAL_CAPABILITIES,
    "full": FULL_CAPABILITIES,
}


def get_preset(name: str) -> TTSCapabilities:
    """Get a preset capability configuration.

    Args:
        name: Preset name (espeak, pyttsx3, google, polly, azure, minimal, full)

    Returns:
        TTSCapabilities instance

    Raises:
        ValueError: If preset not found
    """
    if name.lower() not in PRESETS:
        available = ", ".join(PRESETS.keys())
        raise ValueError(f"Unknown preset '{name}'. Available: {available}")

    return PRESETS[name.lower()]
