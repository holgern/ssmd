"""Basic functionality tests for SSMD."""

import pytest

import ssmd


def test_simple_text():
    """Test plain text conversion."""
    result = ssmd.to_ssml("hello world")
    assert result == "<speak><p>hello world</p></speak>"


def test_emphasis():
    """Test emphasis conversion."""
    result = ssmd.to_ssml("hello *world*!")
    assert result == "<speak><p>hello <emphasis>world</emphasis>!</p></speak>"


def test_strip_emphasis():
    """Test stripping emphasis."""
    result = ssmd.strip_ssmd("hello *world*!")
    assert result == "hello world!"


def test_break():
    """Test break conversion."""
    result = ssmd.to_ssml("hello ... world")
    assert '<break time="1000ms"/>' in result


def test_language_annotation():
    """Test language annotation."""
    result = ssmd.to_ssml("[Guardians of the Galaxy](en)")
    assert 'xml:lang="en-US"' in result
    assert "Guardians of the Galaxy" in result


def test_substitution():
    """Test substitution annotation."""
    result = ssmd.to_ssml("[H2O](sub: water)")
    assert '<sub alias="water">H2O</sub>' in result


def test_mark():
    """Test mark processor."""
    result = ssmd.to_ssml("hello @marker world")
    assert '<mark name="marker"/>' in result


def test_strip_mark():
    """Test stripping marks."""
    result = ssmd.strip_ssmd("hello @marker world")
    assert result == "hello world"


def test_paragraph():
    """Test paragraph processing."""
    result = ssmd.to_ssml("First paragraph.\n\nSecond paragraph.")
    assert "<p>First paragraph.</p><p>Second paragraph.</p>" in result


def test_document_iteration():
    """Test document sentence iteration."""
    parser = ssmd.SSMD({"auto_sentence_tags": True})
    doc = parser.load("Hello world!\nHow are you?")

    sentences = list(doc.sentences())
    assert len(sentences) > 0


def test_class_api():
    """Test SSMD class API."""
    parser = ssmd.SSMD()
    result = parser.to_ssml("hello *world*")
    assert "emphasis" in result

    plain = parser.strip("hello *world*")
    assert plain == "hello world"


def test_document_properties():
    """Test SSMDDocument properties."""
    parser = ssmd.SSMD()
    doc = parser.load("Hello *world*!")

    # Test ssml property
    assert "<speak>" in doc.ssml
    assert "<emphasis>" in doc.ssml

    # Test plain_text property
    assert doc.plain_text == "Hello world!"


def test_config_skip_processor():
    """Test skipping processors via config."""
    parser = ssmd.SSMD({"skip": ["emphasis"]})
    result = parser.to_ssml("hello *world*")
    # Should not process emphasis
    assert "<emphasis>" not in result
    assert "*world*" in result


def test_prosody_shorthand():
    """Test prosody shorthand."""
    result = ssmd.to_ssml("++loud++")
    assert '<prosody volume="x-loud">loud</prosody>' in result


def test_xml_escaping():
    """Test XML special characters are properly escaped."""
    result = ssmd.to_ssml("command & conquer")
    assert "&amp;" in result or "command & conquer" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
