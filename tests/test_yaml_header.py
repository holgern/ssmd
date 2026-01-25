"""Tests for YAML header parsing in SSMD."""

import pytest

import ssmd


def test_yaml_header_parsed_and_removed():
    text = """---
voice:
  languageCode: en-us
  name: en-US-Standard-B
  ssmlGender: MALE
audioConfig:
  audioEncoding: MP3
author: Jane Doe
chapter: 3
---
Hello world.
"""
    doc = ssmd.Document(text, parse_yaml_header=True)
    assert doc.header is not None
    assert doc.header["voice"]["languageCode"] == "en-us"
    assert doc.header["audioConfig"]["audioEncoding"] == "MP3"
    assert doc.header["author"] == "Jane Doe"
    assert "---" not in doc.ssmd
    assert doc.ssmd.strip() == "Hello world."


def test_yaml_header_ignored_when_disabled():
    text = """---
voice:
  languageCode: en-us
---
Hello world.
"""
    doc = ssmd.Document(text, parse_yaml_header=False)
    assert doc.header is None
    assert doc.ssmd.lstrip().startswith("---")
    assert "languageCode" in doc.ssmd


def test_yaml_header_parse_sentences_disabled_preserves_header():
    text = """---
title: Demo
---
Hello world.
"""
    sentences = ssmd.parse_sentences(text, parse_yaml_header=False, use_spacy=False)
    assert sentences
    combined = "\n".join(sentence.to_ssmd() for sentence in sentences)
    assert "---" in combined
    assert "title" in combined


def test_yaml_header_parse_sentences_enabled_strips_header():
    text = """---
title: Demo
---
Hello world.
"""
    sentences = ssmd.parse_sentences(text, parse_yaml_header=True, use_spacy=False)
    combined = "\n".join(sentence.to_ssmd() for sentence in sentences)
    assert "---" not in combined
    assert "Hello world." in combined


def test_yaml_header_supports_dots_end_marker():
    text = """---
voice:
  languageCode: en-us
...
Hello world.
"""
    doc = ssmd.Document(text, parse_yaml_header=True)
    assert doc.header is not None
    assert doc.header["voice"]["languageCode"] == "en-us"
    assert doc.ssmd.strip() == "Hello world."


def test_yaml_header_heading_and_extensions_config():
    text = """---
heading:
  - level_1:
      pause_before: 300ms
      emphasis: strong
      pause: 300ms
  - level_2:
      pause_before: 75ms
      emphasis: moderate
      pause: 75ms
extensions:
  - cheerful:
      value: '<google:style name="cheerful">{text}</google:style>'

---
# Heading One
"""
    doc = ssmd.Document(text, parse_yaml_header=True)
    assert doc.header is not None
    assert "heading" in doc.header
    assert "extensions" in doc.header
    ssml = doc.to_ssml()
    assert "Heading One" in ssml


def test_yaml_header_extension_requires_text_placeholder():
    text = """---
extensions:
  - custom:
      value: "<custom></custom>"
---
Hello world.
"""
    with pytest.raises(ValueError, match="must include '\\{text\\}'"):
        ssmd.Document(text, parse_yaml_header=True)
