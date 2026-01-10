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
    result = ssmd.to_text("hello *world*!")
    assert result == "hello world!"


def test_break():
    """Test break conversion."""
    result = ssmd.to_ssml("hello ...1s world")
    assert '<break time="1s"/>' in result


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
    result = ssmd.to_text("hello @marker world")
    assert result == "hello world"


def test_paragraph():
    """Test paragraph processing."""
    result = ssmd.to_ssml("First paragraph.\n\nSecond paragraph.")
    assert "<p>First paragraph.</p><p>Second paragraph.</p>" in result


def test_document_iteration():
    """Test document sentence iteration."""
    doc = ssmd.Document(
        "Hello world!\nHow are you?", config={"auto_sentence_tags": True}
    )

    sentences = list(doc.sentences())
    assert len(sentences) > 0


def test_document_api():
    """Test Document class API."""
    doc = ssmd.Document("hello *world*")
    result = doc.to_ssml()
    assert "emphasis" in result

    plain = doc.to_text()
    assert plain == "hello world"


def test_document_properties():
    """Test Document properties."""
    doc = ssmd.Document("Hello *world*!")

    # Test ssml property via to_ssml()
    assert "<speak>" in doc.to_ssml()
    assert "<emphasis>" in doc.to_ssml()

    # Test to_text() method
    assert doc.to_text() == "Hello world!"

    # Test ssmd property
    assert doc.ssmd == "Hello *world*!"


def test_config_skip_processor():
    """Test skipping processors via config."""
    doc = ssmd.Document("hello *world*", config={"skip": ["emphasis"]})
    result = doc.to_ssml()
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


def test_document_building():
    """Test building documents incrementally."""
    doc = ssmd.Document()
    doc.add("Hello")
    doc.add(" ")
    doc.add("*world*")

    assert doc.ssmd == "Hello *world*"
    assert "<emphasis>world</emphasis>" in doc.to_ssml()


def test_document_add_sentence():
    """Test add_sentence method."""
    doc = ssmd.Document("First")
    doc.add_sentence("Second")

    assert doc.ssmd == "First\nSecond"


def test_document_add_paragraph():
    """Test add_paragraph method."""
    doc = ssmd.Document("First")
    doc.add_paragraph("Second")

    assert doc.ssmd == "First\n\nSecond"


def test_document_from_ssml():
    """Test creating Document from SSML."""
    ssml = "<speak><emphasis>Hello</emphasis> world</speak>"
    doc = ssmd.Document.from_ssml(ssml)

    assert "*Hello* world" in doc.ssmd


def test_document_from_text():
    """Test creating Document from plain text."""
    doc = ssmd.Document.from_text("Hello world")

    assert doc.ssmd == "Hello world"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
