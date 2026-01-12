"""Tests for SSML to SSMD conversion."""

import pytest

import ssmd
from ssmd import SSMLParser


class TestSSMLToSSMD:
    """Test SSML to SSMD reverse conversion."""

    def test_simple_text(self):
        """Test plain text without markup."""
        ssml = "<speak>Hello world</speak>"
        result = ssmd.from_ssml(ssml)
        assert result.strip() == "Hello world"

    def test_emphasis(self):
        """Test emphasis conversion."""
        ssml = "<speak><emphasis>Hello</emphasis> world</speak>"
        result = ssmd.from_ssml(ssml)
        assert result.strip() == "*Hello* world"

    def test_emphasis_strong(self):
        """Test strong emphasis conversion."""
        ssml = '<speak><emphasis level="strong">Hello</emphasis></speak>'
        result = ssmd.from_ssml(ssml)
        assert result.strip() == "**Hello**"

    def test_break_default(self):
        """Test default break conversion."""
        ssml = '<speak>Hello<break time="1000ms"/>world</speak>'
        result = ssmd.from_ssml(ssml)
        # Breaks have space before and after per SSMD spec
        assert result.strip() == "Hello ...1000ms world"

    def test_break_custom_time(self):
        """Test break with custom time."""
        ssml = '<speak>Hello<break time="500ms"/>world</speak>'
        result = ssmd.from_ssml(ssml)
        assert result.strip() == "Hello ...500ms world"

    def test_break_seconds(self):
        """Test break with seconds."""
        ssml = '<speak>Hello<break time="2s"/>world</speak>'
        result = ssmd.from_ssml(ssml)
        assert result.strip() == "Hello ...2s world"

    def test_break_strength(self):
        """Test break with strength."""
        ssml = '<speak>Hello<break strength="strong"/>world</speak>'
        result = ssmd.from_ssml(ssml)
        assert result.strip() == "Hello ...s world"

    def test_paragraph(self):
        """Test paragraph conversion."""
        ssml = "<speak><p>First paragraph</p><p>Second paragraph</p></speak>"
        result = ssmd.from_ssml(ssml)
        assert "First paragraph" in result
        assert "Second paragraph" in result
        # Paragraphs should be separated by double newlines
        assert "\n\n" in result

    def test_language(self):
        """Test language tag conversion."""
        ssml = '<speak><lang xml:lang="en-US">Hello</lang></speak>'
        result = ssmd.from_ssml(ssml)
        # Per SSMD spec, language is just the code: [text](en)
        assert result.strip() == "[Hello](en)"

    def test_language_non_standard(self):
        """Test non-standard language locale."""
        ssml = '<speak><lang xml:lang="en-GB">Hello</lang></speak>'
        result = ssmd.from_ssml(ssml)
        assert result.strip() == "[Hello](en-GB)"

    def test_phoneme_ipa(self):
        """Test phoneme with IPA."""
        ssml = '<speak><phoneme alphabet="ipa" ph="təmeɪtoʊ">tomato</phoneme></speak>'
        result = ssmd.from_ssml(ssml)
        assert result.strip() == "[tomato](ph: təmeɪtoʊ, alphabet: ipa)"

    def test_phoneme_xsampa(self):
        """Test phoneme with X-SAMPA."""
        ssml = (
            '<speak><phoneme alphabet="x-sampa" ph="t@meItoU">tomato</phoneme></speak>'
        )
        result = ssmd.from_ssml(ssml)
        assert result.strip() == "[tomato](ph: t@meItoU, alphabet: x-sampa)"

    def test_substitution(self):
        """Test substitution conversion."""
        ssml = '<speak><sub alias="World Wide Web Consortium">W3C</sub></speak>'
        result = ssmd.from_ssml(ssml)
        assert result.strip() == "[W3C](sub: World Wide Web Consortium)"

    def test_say_as(self):
        """Test say-as conversion."""
        ssml = '<speak><say-as interpret-as="telephone">+1-555-1234</say-as></speak>'
        result = ssmd.from_ssml(ssml)
        # Per SSMD spec, uses "as:" not "say-as:"
        assert result.strip() == "[+1-555-1234](as: telephone)"

    def test_say_as_with_format(self):
        """Test say-as with format attribute."""
        ssml = (
            '<speak><say-as interpret-as="date" format="mdy">'
            "12/31/2024</say-as></speak>"
        )
        result = ssmd.from_ssml(ssml)
        # Format is quoted in SSMD per spec
        assert result.strip() == '[12/31/2024](as: date, format: "mdy")'

    def test_audio(self):
        """Test audio tag conversion."""
        ssml = '<speak><audio src="sound.mp3">Alternative text</audio></speak>'
        result = ssmd.from_ssml(ssml)
        assert result.strip() == "[Alternative text](sound.mp3 alt)"

    def test_audio_no_alt(self):
        """Test audio tag without alt text."""
        ssml = '<speak><audio src="sound.mp3"/></speak>'
        result = ssmd.from_ssml(ssml)
        assert result.strip() == "[](sound.mp3)"

    def test_mark(self):
        """Test mark conversion."""
        ssml = '<speak>Hello<mark name="point1"/>world</speak>'
        result = ssmd.from_ssml(ssml)
        # Marks have space before
        assert result.strip() == "Hello @point1 world"

    def test_prosody_volume_shorthand(self):
        """Test prosody volume with shorthand."""
        ssml = '<speak><prosody volume="loud">Hello</prosody></speak>'
        result = ssmd.from_ssml(ssml)
        assert result.strip() == "+Hello+"

    def test_prosody_volume_xloud(self):
        """Test prosody x-loud volume."""
        ssml = '<speak><prosody volume="x-loud">Hello</prosody></speak>'
        result = ssmd.from_ssml(ssml)
        assert result.strip() == "++Hello++"

    def test_prosody_volume_soft(self):
        """Test prosody soft volume."""
        ssml = '<speak><prosody volume="soft">Hello</prosody></speak>'
        result = ssmd.from_ssml(ssml)
        assert result.strip() == "-Hello-"

    def test_prosody_rate_shorthand(self):
        """Test prosody rate with shorthand."""
        ssml = '<speak><prosody rate="fast">Hello</prosody></speak>'
        result = ssmd.from_ssml(ssml)
        assert result.strip() == ">Hello>"

    def test_prosody_pitch_shorthand(self):
        """Test prosody pitch with shorthand."""
        ssml = '<speak><prosody pitch="high">Hello</prosody></speak>'
        result = ssmd.from_ssml(ssml)
        assert result.strip() == "^Hello^"

    def test_prosody_multiple_attributes(self):
        """Test prosody with multiple attributes."""
        ssml = '<speak><prosody volume="loud" rate="fast">Hello</prosody></speak>'
        result = ssmd.from_ssml(ssml)
        # Should use annotation syntax for multiple attributes with v: and r: shorthand
        assert "[Hello]" in result
        assert "v:" in result or "volume:" in result
        assert "r:" in result or "rate:" in result

    def test_amazon_whisper_effect(self):
        """Test Amazon whisper effect."""
        # Amazon effects require namespace declaration
        ssml = (
            '<speak xmlns:amazon="https://amazon.com/ssml">'
            '<amazon:effect name="whispered">secret</amazon:effect></speak>'
        )
        result = ssmd.from_ssml(ssml)
        assert result.strip() == "[secret](ext: whisper)"

    def test_complex_nested(self):
        """Test complex nested markup."""
        ssml = """<speak>
            <p><emphasis>Hello</emphasis> world</p>
            <p>This is <prosody volume="loud">important</prosody></p>
        </speak>"""
        result = ssmd.from_ssml(ssml)
        assert "*Hello* world" in result
        assert "+important+" in result

    def test_roundtrip_simple(self):
        """Test roundtrip conversion for simple text."""
        original = "*Hello* world"
        ssml_out = ssmd.to_ssml(original)
        ssmd_back = ssmd.from_ssml(ssml_out)
        assert ssmd_back.strip() == original

    def test_roundtrip_emphasis(self):
        """Test roundtrip with emphasis."""
        original = "This is *emphasized* text"
        ssml_out = ssmd.to_ssml(original)
        ssmd_back = ssmd.from_ssml(ssml_out)
        assert ssmd_back.strip() == original

    def test_roundtrip_break(self):
        """Test roundtrip with break."""
        original = "Hello ...1s world"
        ssml_out = ssmd.to_ssml(original)
        ssmd_back = ssmd.from_ssml(ssml_out)
        assert ssmd_back.strip() == original

    def test_roundtrip_language(self):
        """Test roundtrip with language."""
        original = "[Bonjour](fr) world"
        ssml_out = ssmd.to_ssml(original)
        ssmd_back = ssmd.from_ssml(ssml_out)
        assert ssmd_back.strip() == original

    def test_roundtrip_prosody_volume(self):
        """Test roundtrip with prosody volume."""
        original = "+loud+"
        ssml_out = ssmd.to_ssml(original)
        ssmd_back = ssmd.from_ssml(ssml_out)
        assert ssmd_back.strip() == original

    def test_invalid_ssml(self):
        """Test handling of invalid SSML."""
        with pytest.raises(ValueError, match="Invalid SSML XML"):
            ssmd.from_ssml("<speak><unclosed>")

    def test_parser_class(self):
        """Test using SSMLParser class directly."""
        parser = SSMLParser()
        ssml = "<speak><emphasis>Hello</emphasis></speak>"
        result = parser.to_ssmd(ssml)
        assert result.strip() == "*Hello*"

    def test_without_speak_wrapper(self):
        """Test SSML without <speak> wrapper."""
        ssml = "<emphasis>Hello</emphasis> world"
        result = ssmd.from_ssml(ssml)
        assert result.strip() == "*Hello* world"

    def test_sentence_tags(self):
        """Test sentence tags are stripped."""
        ssml = "<speak><s>Hello world</s></speak>"
        result = ssmd.from_ssml(ssml)
        assert result.strip() == "Hello world"

    def test_whitespace_normalization(self):
        """Test whitespace is normalized."""
        ssml = """<speak>
            Hello    world

            Test
        </speak>"""
        result = ssmd.from_ssml(ssml)
        # Multiple spaces should be collapsed
        assert "  " not in result
        # Content should be preserved
        assert "Hello world" in result
        assert "Test" in result

    def test_voice_name(self):
        """Test voice with name conversion."""
        ssml = '<speak><voice name="Joanna">Hello</voice></speak>'
        result = ssmd.from_ssml(ssml)
        assert result.strip() == "[Hello](voice: Joanna)"

    def test_voice_language_gender(self):
        """Test voice with language and gender."""
        ssml = '<speak><voice language="fr-FR" gender="female">Bonjour</voice></speak>'
        result = ssmd.from_ssml(ssml)
        assert result.strip() == "[Bonjour](voice: fr-FR, gender: female)"

    def test_voice_all_attributes(self):
        """Test voice with all attributes."""
        ssml = (
            '<speak><voice language="en-GB" gender="male" '
            'variant="1">Text</voice></speak>'
        )
        result = ssmd.from_ssml(ssml)
        assert result.strip() == "[Text](voice: en-GB, gender: male, variant: 1)"

    def test_roundtrip_voice_name(self):
        """Test roundtrip voice with name."""
        original = "[Hello](voice: Joanna)"
        ssml_out = ssmd.to_ssml(original)
        ssmd_back = ssmd.from_ssml(ssml_out)
        assert ssmd_back.strip() == original

    def test_roundtrip_voice_complex(self):
        """Test roundtrip voice with language and gender."""
        original = "[Bonjour](voice: fr-FR, gender: female)"
        ssml_out = ssmd.to_ssml(original)
        ssmd_back = ssmd.from_ssml(ssml_out)
        assert ssmd_back.strip() == original

    def test_voice_directive_to_ssmd(self):
        """Test converting multiline voice SSML to directive syntax."""
        ssml = (
            '<speak><p><voice name="sarah">This is a long sentence that '
            "should convert to directive syntax because it is longer than "
            "eighty characters.</voice></p></speak>"
        )
        result = ssmd.from_ssml(ssml)
        assert result.startswith("@voice: sarah\n")
        assert "This is a long sentence" in result

    def test_voice_directive_roundtrip(self):
        """Test roundtrip with voice directive syntax."""
        original = """@voice: sarah
Hello from Sarah with a very long message that definitely spans way more
than eighty characters to trigger directive format

@voice: michael
And hello from Michael with another long message to ensure it uses
directive format too"""
        ssml_out = ssmd.to_ssml(original)
        assert '<voice name="sarah">' in ssml_out
        assert '<voice name="michael">' in ssml_out
        # Convert back - should use directive syntax for long content
        ssmd_back = ssmd.from_ssml(ssml_out)
        assert "@voice: sarah" in ssmd_back
        assert "@voice: michael" in ssmd_back

    def test_voice_directive_with_attrs_to_ssmd(self):
        """Test converting voice with attributes to directive syntax."""
        ssml = (
            '<speak><p><voice language="fr-FR" gender="female">'
            "Bonjour! Comment allez-vous aujourd'hui? "
            "J'espère que vous passez une excellente journée!"
            "</voice></p></speak>"
        )
        result = ssmd.from_ssml(ssml)
        # Should use directive syntax because content is long
        assert "@voice: fr-FR, gender: female" in result
        assert "Bonjour!" in result

    def test_voice_directive_attrs_roundtrip(self):
        """Test roundtrip with voice directive using attributes."""
        original = """@voice: fr-FR, gender: female
Bonjour! C'est un très grand plaisir de vous parler aujourd'hui dans
cette magnifique langue française!

@voice: en-GB, gender: male, variant: 1
Hello there! It's absolutely lovely to meet you on this fine day in
the beautiful United Kingdom."""
        ssml_out = ssmd.to_ssml(original)
        assert '<voice language="fr-FR" gender="female">' in ssml_out
        assert '<voice language="en-GB" gender="male" variant="1">' in ssml_out
        # Convert back - should preserve directive format with attributes
        ssmd_back = ssmd.from_ssml(ssml_out)
        assert "@voice: fr-FR, gender: female" in ssmd_back
        assert "@voice: en-GB, gender: male" in ssmd_back
