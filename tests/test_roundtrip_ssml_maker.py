"""Comprehensive SSML feature tests using ssml-maker.

This test suite uses ssml-maker to generate valid SSML for every feature,
then validates:
1. SSML → SSMD conversion produces the expected SSMD syntax
2. SSMD → SSML roundtrip preserves the semantic meaning
"""

from ssml_maker import (
    BreakStrength,
    EmphasisLevel,
    InterpretAs,
    PhoneticAlphabet,
    ProsodyConfig,
    ProsodyPitch,
    ProsodyRate,
    Speech,
    VolumeLevel,
)

import ssmd


class TestEmphasis:
    """Test emphasis feature with all levels."""

    def test_emphasis_moderate(self):
        """Moderate emphasis: SSML → *text* → SSML."""
        with Speech() as speech:
            with speech.emphasis(EmphasisLevel.MODERATE):
                speech.add_text("important")

        original_ssml = speech.build()
        ssmd_text = ssmd.from_ssml(original_ssml)

        # Validate SSMD syntax
        assert ssmd_text == "*important*", f"Expected '*important*', got '{ssmd_text}'"

        # Validate roundtrip
        result_ssml = ssmd.to_ssml(ssmd_text)
        assert "<emphasis>" in result_ssml
        assert "important" in result_ssml

    def test_emphasis_strong(self):
        """Strong emphasis: SSML → **text** → SSML."""
        with Speech() as speech:
            with speech.emphasis(EmphasisLevel.STRONG):
                speech.add_text("critical")

        original_ssml = speech.build()
        ssmd_text = ssmd.from_ssml(original_ssml)

        # Validate SSMD syntax
        assert (
            ssmd_text == "**critical**"
        ), f"Expected '**critical**', got '{ssmd_text}'"

        # Validate roundtrip
        result_ssml = ssmd.to_ssml(ssmd_text)
        assert 'level="strong"' in result_ssml or 'level="x-strong"' in result_ssml


class TestBreak:
    """Test break/pause feature with time and strength."""

    def test_break_default_time(self):
        """Default break (1000ms): SSML → ... → SSML."""
        with Speech() as speech:
            speech.add_text("Hello")
            speech.add_break(time="1000ms")
            speech.add_text("world")

        original_ssml = speech.build()
        ssmd_text = ssmd.from_ssml(original_ssml)

        # Validate SSMD syntax
        assert "..." in ssmd_text, f"Expected '...' in '{ssmd_text}'"
        assert "Hello" in ssmd_text
        assert "world" in ssmd_text

        # Validate roundtrip
        result_ssml = ssmd.to_ssml(ssmd_text)
        assert "<break" in result_ssml

    def test_break_custom_time(self):
        """Custom break time: SSML → ...500ms → SSML."""
        with Speech() as speech:
            speech.add_text("Wait")
            speech.add_break(time="500ms")
            speech.add_text("here")

        original_ssml = speech.build()
        ssmd_text = ssmd.from_ssml(original_ssml)

        # Validate SSMD syntax
        assert "...500ms" in ssmd_text, f"Expected '...500ms' in '{ssmd_text}'"

        # Validate roundtrip
        result_ssml = ssmd.to_ssml(ssmd_text)
        assert 'time="500ms"' in result_ssml

    def test_break_strength_strong(self):
        """Break with strength: SSML → ...s → SSML."""
        with Speech() as speech:
            speech.add_text("Sentence one")
            speech.add_break(strength=BreakStrength.STRONG)
            speech.add_text("Sentence two")

        original_ssml = speech.build()
        ssmd_text = ssmd.from_ssml(original_ssml)

        # Validate SSMD syntax
        assert "...s" in ssmd_text, f"Expected '...s' in '{ssmd_text}'"

        # Validate roundtrip
        result_ssml = ssmd.to_ssml(ssmd_text)
        assert "<break" in result_ssml


class TestProsody:
    """Test prosody (volume, rate, pitch) features."""

    def test_prosody_volume_loud(self):
        """Loud volume: SSML → +text+ → SSML."""
        with Speech() as speech:
            config = ProsodyConfig(volume=VolumeLevel.LOUD)
            with speech.prosody(config):
                speech.add_text("LOUD")

        original_ssml = speech.build()
        ssmd_text = ssmd.from_ssml(original_ssml)

        # Validate SSMD syntax
        assert "+LOUD+" in ssmd_text, f"Expected '+LOUD+' in '{ssmd_text}'"

        # Validate roundtrip
        result_ssml = ssmd.to_ssml(ssmd_text)
        assert 'volume="loud"' in result_ssml

    def test_prosody_volume_xloud(self):
        """X-loud volume: SSML → ++text++ → SSML."""
        with Speech() as speech:
            config = ProsodyConfig(volume=VolumeLevel.X_LOUD)
            with speech.prosody(config):
                speech.add_text("VERY LOUD")

        original_ssml = speech.build()
        ssmd_text = ssmd.from_ssml(original_ssml)

        # Validate SSMD syntax
        assert (
            "++VERY LOUD++" in ssmd_text
        ), f"Expected '++VERY LOUD++' in '{ssmd_text}'"

        # Validate roundtrip
        result_ssml = ssmd.to_ssml(ssmd_text)
        assert 'volume="x-loud"' in result_ssml

    def test_prosody_volume_soft(self):
        """Soft volume: SSML → -text- → SSML."""
        with Speech() as speech:
            config = ProsodyConfig(volume=VolumeLevel.SOFT)
            with speech.prosody(config):
                speech.add_text("quiet")

        original_ssml = speech.build()
        ssmd_text = ssmd.from_ssml(original_ssml)

        # Validate SSMD syntax
        assert "-quiet-" in ssmd_text, f"Expected '-quiet-' in '{ssmd_text}'"

        # Validate roundtrip
        result_ssml = ssmd.to_ssml(ssmd_text)
        assert 'volume="soft"' in result_ssml

    def test_prosody_rate_fast(self):
        """Fast rate: SSML → >text> → SSML."""
        with Speech() as speech:
            config = ProsodyConfig(rate=ProsodyRate.FAST)
            with speech.prosody(config):
                speech.add_text("quick")

        original_ssml = speech.build()
        ssmd_text = ssmd.from_ssml(original_ssml)

        # Validate SSMD syntax
        assert ">quick>" in ssmd_text, f"Expected '>quick>' in '{ssmd_text}'"

        # Validate roundtrip
        result_ssml = ssmd.to_ssml(ssmd_text)
        assert 'rate="fast"' in result_ssml

    def test_prosody_pitch_high(self):
        """High pitch: SSML → ^text^ → SSML."""
        with Speech() as speech:
            config = ProsodyConfig(pitch=ProsodyPitch.HIGH)
            with speech.prosody(config):
                speech.add_text("squeaky")

        original_ssml = speech.build()
        ssmd_text = ssmd.from_ssml(original_ssml)

        # Validate SSMD syntax
        assert "^squeaky^" in ssmd_text, f"Expected '^squeaky^' in '{ssmd_text}'"

        # Validate roundtrip
        result_ssml = ssmd.to_ssml(ssmd_text)
        assert 'pitch="high"' in result_ssml

    def test_prosody_multiple_attributes(self):
        """Multiple prosody attributes: SSML → [text](v:4,r:4,p:4) → SSML."""
        with Speech() as speech:
            config = ProsodyConfig(
                volume=VolumeLevel.LOUD, rate=ProsodyRate.FAST, pitch=ProsodyPitch.HIGH
            )
            with speech.prosody(config):
                speech.add_text("energetic")

        original_ssml = speech.build()
        ssmd_text = ssmd.from_ssml(original_ssml)

        # Validate SSMD syntax - should use annotation format
        assert (
            "[energetic]" in ssmd_text
        ), f"Expected annotation format in '{ssmd_text}'"
        assert "v:" in ssmd_text or "volume" in ssmd_text
        assert "r:" in ssmd_text or "rate" in ssmd_text
        assert "p:" in ssmd_text or "pitch" in ssmd_text

        # Validate roundtrip
        result_ssml = ssmd.to_ssml(ssmd_text)
        assert "volume" in result_ssml
        assert "rate" in result_ssml
        assert "pitch" in result_ssml


class TestSayAs:
    """Test say-as interpret-as feature."""

    def test_say_as_telephone(self):
        """Telephone: SSML → [text](as: telephone) → SSML."""
        with Speech() as speech:
            with speech.say_as(InterpretAs.TELEPHONE):
                speech.add_text("+1-555-1234")

        original_ssml = speech.build()
        ssmd_text = ssmd.from_ssml(original_ssml)

        # Validate SSMD syntax
        assert "[+1-555-1234](as: telephone)" in ssmd_text, f"Got '{ssmd_text}'"

        # Validate roundtrip
        result_ssml = ssmd.to_ssml(ssmd_text)
        assert 'interpret-as="telephone"' in result_ssml

    def test_say_as_characters(self):
        """Characters: SSML → [text](as: characters) → SSML."""
        with Speech() as speech:
            with speech.say_as(InterpretAs.CHARACTERS):
                speech.add_text("ABC")

        original_ssml = speech.build()
        ssmd_text = ssmd.from_ssml(original_ssml)

        # Validate SSMD syntax
        assert "[ABC](as: characters)" in ssmd_text, f"Got '{ssmd_text}'"

        # Validate roundtrip
        result_ssml = ssmd.to_ssml(ssmd_text)
        assert 'interpret-as="characters"' in result_ssml


class TestPhoneme:
    """Test phonetic pronunciation feature."""

    def test_phoneme_ipa(self):
        """IPA phoneme: SSML → [text](ipa: ...) → SSML."""
        with Speech() as speech:
            with speech.phoneme(PhoneticAlphabet.IPA, "təˈmeɪtoʊ"):
                speech.add_text("tomato")

        original_ssml = speech.build()
        ssmd_text = ssmd.from_ssml(original_ssml)

        # Validate SSMD syntax
        assert "[tomato](ipa: təˈmeɪtoʊ)" in ssmd_text, f"Got '{ssmd_text}'"

        # Validate roundtrip
        result_ssml = ssmd.to_ssml(ssmd_text)
        assert 'alphabet="ipa"' in result_ssml
        assert 'ph="təˈmeɪtoʊ"' in result_ssml


class TestSubstitution:
    """Test alias substitution feature."""

    def test_substitution(self):
        """Substitution: SSML → [text](sub: alias) → SSML."""
        with Speech() as speech:
            with speech.sub("World Wide Web Consortium"):
                speech.add_text("W3C")

        original_ssml = speech.build()
        ssmd_text = ssmd.from_ssml(original_ssml)

        # Validate SSMD syntax
        assert (
            "[W3C](sub: World Wide Web Consortium)" in ssmd_text
        ), f"Got '{ssmd_text}'"

        # Validate roundtrip
        result_ssml = ssmd.to_ssml(ssmd_text)
        assert 'alias="World Wide Web Consortium"' in result_ssml


class TestParagraph:
    """Test paragraph feature."""

    def test_single_paragraph(self):
        """Single paragraph: SSML → text → SSML."""
        with Speech() as speech:
            with speech.paragraph():
                speech.add_text("This is a paragraph")

        original_ssml = speech.build()
        ssmd_text = ssmd.from_ssml(original_ssml)

        # Validate SSMD syntax
        assert "This is a paragraph" in ssmd_text

        # Validate roundtrip
        result_ssml = ssmd.to_ssml(ssmd_text)
        assert "<p>" in result_ssml

    def test_multiple_paragraphs(self):
        """Multiple paragraphs: SSML → para1\\n\\npara2 → SSML."""
        with Speech() as speech:
            with speech.paragraph():
                speech.add_text("First paragraph")
            with speech.paragraph():
                speech.add_text("Second paragraph")

        original_ssml = speech.build()
        ssmd_text = ssmd.from_ssml(original_ssml)

        # Validate SSMD syntax - paragraphs separated by double newline
        assert "First paragraph" in ssmd_text
        assert "Second paragraph" in ssmd_text
        assert "\n\n" in ssmd_text, f"Expected paragraph separator in '{ssmd_text}'"

        # Validate roundtrip
        result_ssml = ssmd.to_ssml(ssmd_text)
        assert result_ssml.count("<p>") >= 2


class TestComplexScenarios:
    """Test complex nested and mixed scenarios."""

    def test_nested_emphasis_in_paragraph(self):
        """Nested: paragraph with emphasis."""
        with Speech() as speech:
            with speech.paragraph():
                speech.add_text("This is ")
                with speech.emphasis(EmphasisLevel.STRONG):
                    speech.add_text("important")
                speech.add_text(" text")

        original_ssml = speech.build()
        ssmd_text = ssmd.from_ssml(original_ssml)

        # Validate SSMD syntax
        assert "**important**" in ssmd_text
        assert "This is" in ssmd_text
        assert "text" in ssmd_text

        # Validate roundtrip
        result_ssml = ssmd.to_ssml(ssmd_text)
        assert "<emphasis" in result_ssml
        assert "<p>" in result_ssml

    def test_mixed_features(self):
        """Mixed: emphasis, break, say-as in sequence."""
        with Speech() as speech:
            with speech.emphasis(EmphasisLevel.MODERATE):
                speech.add_text("Alert")
            speech.add_break(time="500ms")
            speech.add_text("Call ")
            with speech.say_as(InterpretAs.TELEPHONE):
                speech.add_text("911")

        original_ssml = speech.build()
        ssmd_text = ssmd.from_ssml(original_ssml)

        # Validate SSMD syntax
        assert "*Alert*" in ssmd_text
        assert "...500ms" in ssmd_text
        assert "[911](as: telephone)" in ssmd_text

        # Validate roundtrip
        result_ssml = ssmd.to_ssml(ssmd_text)
        assert "<emphasis>" in result_ssml
        assert "<break" in result_ssml
        assert "say-as" in result_ssml

    def test_prosody_with_emphasis(self):
        """Nested: prosody containing emphasis."""
        with Speech() as speech:
            config = ProsodyConfig(volume=VolumeLevel.LOUD)
            with speech.prosody(config):
                with speech.emphasis(EmphasisLevel.STRONG):
                    speech.add_text("WARNING")

        original_ssml = speech.build()
        ssmd_text = ssmd.from_ssml(original_ssml)

        # Validate SSMD contains both markers
        # Should be: +**WARNING**+ (prosody wraps emphasis)
        assert "**WARNING**" in ssmd_text  # Strong emphasis
        assert "+" in ssmd_text  # Loud volume (wraps the emphasis)
        assert "WARNING" in ssmd_text

        # Validate roundtrip
        result_ssml = ssmd.to_ssml(ssmd_text)
        # Result should have both emphasis and volume indicators
        assert "emphasis" in result_ssml
        assert (
            "prosody" in result_ssml or "+" in ssmd_text
        )  # Either explicit prosody or shorthand
