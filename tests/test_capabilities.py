"""Test TTS capability filtering."""

import pytest

from ssmd import SSMD, TTSCapabilities


def test_capability_emphasis_disabled():
    """Test that emphasis is stripped when not supported."""
    caps = TTSCapabilities(emphasis=False)
    parser = SSMD(capabilities=caps)

    result = parser.to_ssml("Hello *world*!")
    # Should strip emphasis markup
    assert "<emphasis>" not in result
    assert "world" in result


def test_capability_prosody_disabled():
    """Test that prosody is stripped when not supported."""
    caps = TTSCapabilities(prosody=False)
    parser = SSMD(capabilities=caps)

    result = parser.to_ssml("++loud text++")
    # Should strip prosody markup
    assert "<prosody" not in result
    assert "loud text" in result


def test_capability_break_disabled():
    """Test that breaks are stripped when not supported."""
    caps = TTSCapabilities(break_tags=False)
    parser = SSMD(capabilities=caps)

    result = parser.to_ssml("Hello ...500ms world")
    # Should strip break tags
    assert "<break" not in result
    assert "Hello" in result and "world" in result


def test_capability_language_disabled():
    """Test that language tags are stripped when not supported."""
    caps = TTSCapabilities(language=False)
    parser = SSMD(capabilities=caps)

    result = parser.to_ssml("[Bonjour](fr) world")
    # Should strip language tags
    assert "<lang" not in result
    assert "Bonjour" in result


def test_capability_audio_disabled():
    """Test that audio tags are stripped when not supported."""
    caps = TTSCapabilities(audio=False)
    parser = SSMD(capabilities=caps)

    result = parser.to_ssml("[sound](https://example.com/beep.mp3)")
    # Should strip audio tags
    assert "<audio" not in result
    assert "sound" in result


def test_capability_substitution_disabled():
    """Test that substitution tags are stripped when not supported."""
    caps = TTSCapabilities(substitution=False)
    parser = SSMD(capabilities=caps)

    result = parser.to_ssml("[H2O](sub: water)")
    # Should strip sub tags
    assert "<sub" not in result
    assert "H2O" in result


def test_preset_espeak():
    """Test eSpeak preset (limited capabilities)."""
    parser = SSMD(capabilities="espeak")

    # eSpeak doesn't support emphasis
    result = parser.to_ssml("Hello *world*!")
    assert "<emphasis>" not in result

    # But it supports breaks
    result = parser.to_ssml("Hello ...500ms world")
    assert "<break" in result


def test_preset_pyttsx3():
    """Test pyttsx3 preset (minimal SSML)."""
    parser = SSMD(capabilities="pyttsx3")

    # pyttsx3 has very minimal SSML support
    result = parser.to_ssml("Hello *world* ...500ms [bonjour](fr)!")

    # Should strip most features
    assert "<emphasis>" not in result
    assert "<break" not in result
    assert "<lang" not in result

    # Should keep text
    assert "Hello" in result
    assert "world" in result


def test_preset_google():
    """Test Google TTS preset (full support)."""
    parser = SSMD(capabilities="google")

    # Google supports most features
    result = parser.to_ssml("Hello *world* ...500ms [bonjour](fr)!")

    assert "<emphasis>" in result
    assert "<break" in result
    assert "<lang" in result


def test_mixed_config_and_capabilities():
    """Test combining custom config with capabilities."""
    caps = TTSCapabilities(emphasis=False)
    parser = SSMD(config={"auto_sentence_tags": True}, capabilities=caps)

    result = parser.to_ssml("Hello *world*!\nHow are you?")

    # Should have sentence tags (from config)
    assert "<s>" in result or "<p>" in result

    # Should NOT have emphasis (from capabilities)
    assert "<emphasis>" not in result


def test_custom_capabilities():
    """Test custom capability definition."""
    # Create custom TTS with specific limitations
    caps = TTSCapabilities(
        emphasis=True,
        break_tags=True,
        prosody=False,  # No prosody
        language=True,
        audio=False,  # No audio
        say_as=False,  # No say-as
    )

    parser = SSMD(capabilities=caps)

    text = """
    Hello *world*!
    Pause here ...500ms please.
    Say [bonjour](fr) to everyone.
    This is ++very loud++.
    The number is [123](as: cardinal).
    """

    result = parser.to_ssml(text)

    # Supported features
    assert "<emphasis>" in result
    assert "<break" in result
    assert "<lang" in result

    # Unsupported features (should be stripped)
    assert "<prosody" not in result
    assert "<say-as" not in result
    assert "very loud" in result  # Text preserved


def test_prosody_partial_support():
    """Test partial prosody support (only some attributes)."""
    caps = TTSCapabilities(
        prosody=True,
        prosody_volume=True,  # Supports volume
        prosody_rate=False,  # Doesn't support rate
        prosody_pitch=False,  # Doesn't support pitch
    )

    parser = SSMD(capabilities=caps)

    # Volume should work
    result = parser.to_ssml("++loud++")
    assert "<prosody" in result or "loud" in result

    # Rate should be stripped (not supported)
    result = parser.to_ssml(">>fast>>")
    # Should strip rate markup
    assert "fast" in result


def test_extension_filtering():
    """Test that extensions are filtered based on capabilities."""
    caps = TTSCapabilities(extensions={"whisper": True, "drc": False})

    parser = SSMD(capabilities=caps)

    # Whisper is supported
    result = parser.to_ssml("[quiet](ext: whisper)")
    assert "whisper" in result or "quiet" in result

    # DRC is not supported (should strip to text)
    result = parser.to_ssml("[compressed](ext: drc)")
    assert "compressed" in result
    # Should not have DRC-specific tags


def test_minimal_preset():
    """Test minimal preset (everything stripped)."""
    parser = SSMD(capabilities="minimal")

    text = """
    # Heading
    Hello *world*!
    Pause ...500ms here.
    [Bonjour](fr) everyone.
    ++Loud text++
    """

    result = parser.to_ssml(text)

    # Should strip all markup
    assert "<emphasis>" not in result
    assert "<break" not in result
    assert "<lang" not in result
    assert "<prosody" not in result

    # But preserve text
    assert "Heading" in result
    assert "Hello" in result
    assert "world" in result


def test_capability_preserves_text():
    """Test that all capabilities preserve the actual text content."""
    caps = TTSCapabilities(
        emphasis=False,
        prosody=False,
        break_tags=False,
        language=False,
    )

    parser = SSMD(capabilities=caps)

    text = "Hello *world* from [France](fr) with ++excitement++ ...500ms please!"
    result = parser.to_ssml(text)

    # All text should be preserved
    assert "Hello" in result
    assert "world" in result
    assert "France" in result
    assert "excitement" in result
    assert "please" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
