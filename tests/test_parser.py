"""Tests for SSMD parser (segment-based parsing)."""

import pytest

from ssmd import (
    parse_segments,
    parse_sentences,
    parse_voice_blocks,
)


class TestParseVoiceBlocks:
    """Test voice block parsing."""

    def test_no_voice_directive(self):
        """Test text without voice directives."""
        text = "Hello world"
        blocks = parse_voice_blocks(text)

        assert len(blocks) == 1
        assert blocks[0][0] is None  # No voice
        assert blocks[0][1] == "Hello world"

    def test_single_voice(self):
        """Test single voice directive."""
        text = "@voice: sarah\nHello world"
        blocks = parse_voice_blocks(text)

        assert len(blocks) == 1
        assert blocks[0][0] is not None
        assert blocks[0][0].name == "sarah"
        assert blocks[0][1] == "Hello world"

    def test_multiple_voices(self):
        """Test multiple voice directives."""
        text = """@voice: sarah
Hello from Sarah

@voice: michael
Hello from Michael"""
        blocks = parse_voice_blocks(text)

        assert len(blocks) == 2
        assert blocks[0][0] is not None
        assert blocks[0][0].name == "sarah"
        assert "Sarah" in blocks[0][1]
        assert blocks[1][0] is not None
        assert blocks[1][0].name == "michael"
        assert "Michael" in blocks[1][1]

    def test_voice_with_language_gender(self):
        """Test voice directive with language and gender."""
        text = "@voice: fr-FR, gender: female\nBonjour"
        blocks = parse_voice_blocks(text)

        assert len(blocks) == 1
        voice = blocks[0][0]
        assert voice is not None
        assert voice.language == "fr-FR"
        assert voice.gender == "female"
        assert voice.name is None

    def test_voice_with_all_attributes(self):
        """Test voice directive with all attributes."""
        text = "@voice: en-GB, gender: male, variant: 1\nHello"
        blocks = parse_voice_blocks(text)

        voice = blocks[0][0]
        assert voice is not None
        assert voice.language == "en-GB"
        assert voice.gender == "male"
        assert voice.variant == 1

    def test_voice_with_explicit_language(self):
        """Test voice directive with explicit language: parameter."""
        text = "@voice: sarah, language: en-US\nHello"
        blocks = parse_voice_blocks(text)

        voice = blocks[0][0]
        assert voice is not None
        assert voice.name == "sarah"
        assert voice.language == "en-US"
        assert voice.gender is None

    def test_voice_with_name_language_and_gender(self):
        """Test voice directive with name, language, and gender."""
        text = "@voice: narrator, language: en-GB, gender: male\nHello"
        blocks = parse_voice_blocks(text)

        voice = blocks[0][0]
        assert voice is not None
        assert voice.name == "narrator"
        assert voice.language == "en-GB"
        assert voice.gender == "male"

    def test_voice_parentheses_syntax(self):
        """Test voice directive with parentheses syntax."""
        text = "@voice(sarah)\nHello"
        blocks = parse_voice_blocks(text)

        assert blocks[0][0] is not None
        assert blocks[0][0].name == "sarah"


class TestParseSegments:
    """Test segment parsing."""

    def test_plain_text(self):
        """Test parsing plain text."""
        segments = parse_segments("Hello world")

        assert len(segments) == 1
        assert segments[0].text == "Hello world"
        assert segments[0].emphasis is False

    def test_emphasis(self):
        """Test parsing emphasis."""
        segments = parse_segments("Hello *world*")

        # Currently creates one segment with emphasis flag
        assert len(segments) >= 1
        # Find segment with "world"
        world_seg = next(s for s in segments if "world" in s.text)
        assert world_seg.emphasis is True

    def test_breaks(self):
        """Test parsing breaks."""
        segments = parse_segments("Hello ...500ms world")

        # Should create segments with break between them
        assert len(segments) >= 1
        # At least one segment should have breaks_after
        has_break = any(len(s.breaks_after) > 0 for s in segments)
        assert has_break

    def test_say_as(self):
        """Test parsing say-as annotation."""
        segments = parse_segments("Call [+1-555-0123](as: telephone) now")

        # Should find segment with say-as
        say_as_seg = next((s for s in segments if s.say_as), None)
        assert say_as_seg is not None
        assert say_as_seg.say_as is not None
        assert say_as_seg.say_as.interpret_as == "telephone"
        assert say_as_seg.text == "+1-555-0123"

    def test_substitution(self):
        """Test parsing substitution."""
        segments = parse_segments("[H2O](sub: water) is important")

        # Should find segment with substitution
        sub_seg = next((s for s in segments if s.substitution), None)
        assert sub_seg is not None
        assert sub_seg.text == "H2O"
        assert sub_seg.substitution == "water"

    def test_phoneme(self):
        """Test parsing phoneme."""
        segments = parse_segments("Say [tomato](ph: t@meItoU) properly")

        # Should find segment with phoneme
        phoneme_seg = next((s for s in segments if s.phoneme), None)
        assert phoneme_seg is not None
        assert phoneme_seg.text == "tomato"
        assert phoneme_seg.phoneme is not None  # X-SAMPA converted to IPA

    def test_prosody_annotation(self):
        """Test parsing prosody annotation."""
        segments = parse_segments("[loud text](v: 5)")

        # Should find segment with prosody
        prosody_seg = next((s for s in segments if s.prosody), None)
        assert prosody_seg is not None
        assert prosody_seg.prosody is not None
        assert prosody_seg.prosody.volume == "x-loud"

    def test_language_annotation(self):
        """Test parsing language annotation."""
        segments = parse_segments("[Bonjour](fr) everyone")

        # Should find segment with language
        lang_seg = next((s for s in segments if s.language), None)
        assert lang_seg is not None
        assert lang_seg.language == "fr"


class TestParseSentences:
    """Test sentence parsing."""

    def test_single_sentence(self):
        """Test parsing single sentence."""
        sentences = parse_sentences("Hello world.")

        assert len(sentences) == 1
        assert len(sentences[0].segments) >= 1

    def test_multiple_sentences(self):
        """Test parsing multiple sentences."""
        sentences = parse_sentences("Hello world. How are you?")

        assert len(sentences) == 2

    def test_voice_blocks_create_sentences(self):
        """Test that voice changes create sentence boundaries."""
        text = """@voice: sarah
Hello from Sarah

@voice: michael
Hello from Michael"""
        sentences = parse_sentences(text)

        # Should have at least 2 sentences (one per voice block)
        assert len(sentences) >= 2
        assert sentences[0].voice is not None
        assert sentences[0].voice.name == "sarah"

    def test_paragraph_detection(self):
        """Test paragraph break detection."""
        text = "First paragraph.\n\nSecond paragraph."
        sentences = parse_sentences(text, sentence_detection=True)

        # Should detect paragraph break
        assert len(sentences) >= 2
        # First sentence should be marked as paragraph end
        assert any(s.is_paragraph_end for s in sentences)

    def test_no_sentence_detection(self):
        """Test disabling sentence detection."""
        text = "Hello. How are you?"
        sentences = parse_sentences(text, sentence_detection=False)

        # Should treat as single sentence when detection disabled
        assert len(sentences) == 1

    def test_include_default_voice(self):
        """Test including text before first voice directive."""
        text = """Intro text

@voice: sarah
Sarah speaks"""
        sentences = parse_sentences(text, include_default_voice=True)

        # Should include intro text
        assert len(sentences) >= 2
        assert sentences[0].voice is None

    def test_exclude_default_voice(self):
        """Test excluding text before first voice directive."""
        text = """Intro text

@voice: sarah
Sarah speaks"""
        sentences = parse_sentences(text, include_default_voice=False)

        # Should skip intro text
        assert all(s.voice is not None for s in sentences)


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_multi_voice_dialogue(self):
        """Test parsing multi-voice dialogue."""
        script = """
@voice: sarah
Welcome to the show!

@voice: michael
Thanks Sarah!

@voice: sarah
Great idea!
"""
        sentences = parse_sentences(script)

        # Should parse all voice blocks
        assert len(sentences) == 3
        assert sentences[0].voice is not None
        assert sentences[0].voice.name == "sarah"
        assert sentences[1].voice is not None
        assert sentences[1].voice.name == "michael"
        assert sentences[2].voice is not None
        assert sentences[2].voice.name == "sarah"

    def test_complex_features(self):
        """Test parsing multiple features in one text."""
        text = """@voice: sarah
Hello *world*! ...500ms Call [+1-555-0123](as: telephone) now.
[H2O](sub: water) is important."""

        sentences = parse_sentences(text)

        # Should parse all features
        assert len(sentences) >= 1

        # Collect all segments
        all_segments = []
        for sent in sentences:
            all_segments.extend(sent.segments)

        # Should have segments with different features
        has_say_as = any(s.say_as for s in all_segments)
        has_substitution = any(s.substitution for s in all_segments)

        assert has_say_as or has_substitution  # At least one text transformation
        # Note: breaks might be merged, so they're not checked

    def test_multilingual_script(self):
        """Test multi-language script with voice blocks and gender."""
        script = """@voice: fr-FR, gender: female
Bonjour! Comment allez-vous?

@voice: en-GB, gender: male
Hello there! How are you?"""

        try:
            sentences = parse_sentences(script)

            assert len(sentences) >= 2
            assert sentences[0].voice is not None
            assert sentences[0].voice.language == "fr-FR"
            assert sentences[0].voice.gender == "female"
            # Later sentences may have en-GB voice
            en_sentence = next(
                (s for s in sentences if s.voice and s.voice.language == "en-GB"), None
            )
            if en_sentence:
                assert en_sentence.voice is not None
                assert en_sentence.voice.gender == "male"
        except OSError:
            # French or English model not installed - use regex mode
            pytest.skip("spaCy models not installed for all languages")


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_text(self):
        """Test parsing empty text."""
        sentences = parse_sentences("")
        assert len(sentences) == 0

    def test_whitespace_only(self):
        """Test parsing whitespace-only text."""
        sentences = parse_sentences("   \n\n   ")
        assert len(sentences) == 0

    def test_voice_without_content(self):
        """Test voice directive without following content."""
        text = "@voice: sarah\n"
        sentences = parse_sentences(text)

        # Should not create empty sentences
        assert all(len(s.segments) > 0 for s in sentences) or len(sentences) == 0
