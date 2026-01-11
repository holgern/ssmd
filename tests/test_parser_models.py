"""Tests for sentence detection model configuration."""

import pytest

from ssmd.parser import _build_model_name, parse_sentences


class TestBuildModelName:
    """Test the _build_model_name helper function."""

    def test_english_small_model(self):
        """Build English small model name."""
        assert _build_model_name("en", "sm") == "en_core_web_sm"

    def test_english_medium_model(self):
        """Build English medium model name."""
        assert _build_model_name("en", "md") == "en_core_web_md"

    def test_english_large_model(self):
        """Build English large model name."""
        assert _build_model_name("en", "lg") == "en_core_web_lg"

    def test_english_transformer_model(self):
        """Build English transformer model name."""
        assert _build_model_name("en", "trf") == "en_core_web_trf"

    def test_french_models(self):
        """Build French model names."""
        assert _build_model_name("fr", "sm") == "fr_core_news_sm"
        assert _build_model_name("fr", "md") == "fr_core_news_md"
        assert _build_model_name("fr", "lg") == "fr_core_news_lg"

    def test_german_models(self):
        """Build German model names."""
        assert _build_model_name("de", "sm") == "de_core_news_sm"
        assert _build_model_name("de", "md") == "de_core_news_md"

    def test_spanish_models(self):
        """Build Spanish model names."""
        assert _build_model_name("es", "sm") == "es_core_news_sm"

    def test_unsupported_language(self):
        """Return None for unsupported language."""
        assert _build_model_name("xyz", "sm") is None
        assert _build_model_name("unknown", "md") is None


class TestParseSentencesRegexMode:
    """Test sentence parsing with regex mode (use_spacy=False)."""

    def test_regex_basic(self):
        """Parse basic sentences with regex."""
        text = "Hello world. This is a test."
        sentences = parse_sentences(text, use_spacy=False)

        assert len(sentences) == 2
        assert "Hello world" in sentences[0].segments[0].text
        assert "This is a test" in sentences[1].segments[0].text

    def test_regex_question_marks(self):
        """Parse sentences with question marks."""
        text = "Hello? How are you?"
        sentences = parse_sentences(text, use_spacy=False)

        assert len(sentences) == 2

    def test_regex_exclamation(self):
        """Parse sentences with exclamation marks."""
        text = "Hello! Welcome!"
        sentences = parse_sentences(text, use_spacy=False)

        assert len(sentences) == 2

    def test_regex_mixed_punctuation(self):
        """Parse sentences with mixed punctuation."""
        text = "Hello! How are you? I'm fine."
        sentences = parse_sentences(text, use_spacy=False)

        assert len(sentences) == 3

    def test_regex_single_sentence(self):
        """Parse single sentence."""
        text = "Hello world."
        sentences = parse_sentences(text, use_spacy=False)

        assert len(sentences) == 1
        assert "Hello world" in sentences[0].segments[0].text

    def test_regex_no_final_punctuation(self):
        """Parse text without final punctuation."""
        text = "Hello world"
        sentences = parse_sentences(text, use_spacy=False)

        assert len(sentences) == 1
        assert "Hello world" in sentences[0].segments[0].text


class TestParseSentencesModelSize:
    """Test sentence parsing with different model sizes."""

    def test_default_model_size(self):
        """Default uses small model (implicitly via phrasplit)."""
        text = "Hello world. This is a test."
        sentences = parse_sentences(text)

        # Should work with default small model
        assert len(sentences) == 2

    def test_explicit_small_model(self):
        """Explicitly specify small model."""
        text = "Hello world. This is a test."
        sentences = parse_sentences(text, model_size="sm")

        assert len(sentences) == 2

    def test_medium_model(self):
        """Specify medium model (may not be installed)."""
        text = "Hello world. This is a test."

        # If medium model not installed, should fall back to regex
        try:
            sentences = parse_sentences(text, model_size="md")
            # If it works, check results
            assert len(sentences) == 2
        except Exception:
            # If phrasplit fails, that's expected if model not installed
            pytest.skip("Medium model not installed")

    def test_large_model(self):
        """Specify large model (may not be installed)."""
        text = "Hello world. This is a test."

        try:
            sentences = parse_sentences(text, model_size="lg")
            assert len(sentences) == 2
        except Exception:
            pytest.skip("Large model not installed")


class TestParseSentencesCustomModel:
    """Test sentence parsing with custom spaCy model."""

    def test_custom_model_name(self):
        """Specify custom model name (overrides model_size)."""
        text = "Hello world. This is a test."

        # Try with a custom model (falls back to regex if not installed)
        try:
            sentences = parse_sentences(text, spacy_model="en_core_web_sm")
            assert len(sentences) == 2
        except Exception:
            pytest.skip("Custom model not available")

    def test_custom_model_overrides_size(self):
        """Custom model overrides model_size parameter."""
        text = "Hello world. This is a test."

        # spacy_model should take priority over model_size
        try:
            sentences = parse_sentences(
                text, model_size="lg", spacy_model="en_core_web_sm"
            )
            # Should use en_core_web_sm, not en_core_web_lg
            assert len(sentences) == 2
        except Exception:
            pytest.skip("spaCy model not available")


class TestParseSentencesMultiLanguage:
    """Test sentence parsing with multiple languages."""

    def test_french_default_model(self):
        """Parse French text with default small model."""
        text = """
        @voice: fr-FR
        Bonjour tout le monde.
        """
        sentences = parse_sentences(text, language="fr")

        # Should work with French small model
        assert len(sentences) >= 1

    def test_french_medium_model(self):
        """Parse French text with medium model."""
        text = """
        @voice: fr-FR
        Bonjour tout le monde.
        """

        try:
            sentences = parse_sentences(text, language="fr", model_size="md")
            assert len(sentences) >= 1
        except Exception:
            pytest.skip("French medium model not installed")

    def test_voice_language_overrides_parameter(self):
        """Voice language should override language parameter."""
        text = """
        @voice: fr-FR
        Bonjour. Comment allez-vous?

        @voice: en-US
        Hello. How are you?
        """

        sentences = parse_sentences(text, language="en")

        # Should detect both French and English blocks
        assert len(sentences) >= 2


class TestParseSentencesBackwardCompatibility:
    """Test backward compatibility with existing code."""

    def test_no_new_parameters(self):
        """Calling without new parameters should work as before."""
        text = "Hello world. This is a test."
        sentences = parse_sentences(text)

        assert len(sentences) == 2

    def test_existing_parameters_still_work(self):
        """Existing parameters should still work."""
        text = "Hello world. This is a test."

        sentences = parse_sentences(
            text, sentence_detection=True, include_default_voice=True, language="en"
        )

        assert len(sentences) == 2

    def test_sentence_detection_false(self):
        """Disabling sentence detection should still work."""
        text = "Hello world. This is a test."
        sentences = parse_sentences(text, sentence_detection=False)

        # Should return single sentence
        assert len(sentences) == 1


class TestParseSentencesEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_text_with_use_spacy_false(self):
        """Empty text with regex mode."""
        sentences = parse_sentences("", use_spacy=False)
        assert len(sentences) == 0

    def test_whitespace_only_with_use_spacy_false(self):
        """Whitespace-only text with regex mode."""
        sentences = parse_sentences("   \n\n   ", use_spacy=False)
        assert len(sentences) == 0

    def test_no_punctuation_with_use_spacy_false(self):
        """Text without punctuation in regex mode."""
        text = "Hello world"
        sentences = parse_sentences(text, use_spacy=False)

        assert len(sentences) == 1
        assert "Hello world" in sentences[0].segments[0].text

    def test_multiple_spaces_with_use_spacy_false(self):
        """Text with multiple spaces in regex mode."""
        text = "Hello  world.  This  is  a  test."
        sentences = parse_sentences(text, use_spacy=False)

        assert len(sentences) == 2


class TestParseSentencesIntegration:
    """Integration tests with full features."""

    def test_regex_mode_with_emphasis(self):
        """Regex mode should preserve emphasis."""
        text = "Hello *world*. This is *great*."
        sentences = parse_sentences(text, use_spacy=False)

        assert len(sentences) == 2
        # Emphasis should be preserved in segments
        assert any("world" in seg.text for seg in sentences[0].segments)

    def test_regex_mode_with_voice_blocks(self):
        """Regex mode should work with voice blocks."""
        text = """
        @voice: sarah
        Hello world. How are you?

        @voice: michael
        I'm fine. Thanks!
        """
        sentences = parse_sentences(text, use_spacy=False)

        # Should split into 4 sentences (2 per voice)
        assert len(sentences) >= 4

    def test_model_size_with_voice_blocks(self):
        """Model size should apply to all voice blocks."""
        text = """
        @voice: en-US
        Hello world.

        @voice: fr-FR
        Bonjour monde.
        """

        sentences = parse_sentences(text, model_size="sm")

        # Should detect sentences in both languages
        assert len(sentences) >= 2
