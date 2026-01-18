"""Tests for parse_spans span offsets."""

import ssmd


def test_basic_phoneme_span_offsets():
    text = "Say [tomato]{ph='a'} now."
    result = ssmd.parse_spans(text)

    assert result.clean_text == "Say tomato now."
    span = result.annotations[0]
    assert span.char_start == 4
    assert span.char_end == 10
    assert span.attrs.get("ph") == "a"
    assert span.attrs.get("tag") == "phoneme"


def test_repeated_words_offsets():
    text = "[word]{lang='en'} word"
    result = ssmd.parse_spans(text)

    assert result.clean_text == "word word"
    span = result.annotations[0]
    assert span.attrs.get("tag") == "lang"
    assert result.clean_text[span.char_start : span.char_end] == "word"


def test_punctuation_adjacency_offsets():
    text = "Hello, [world]{lang='en'}!"
    result = ssmd.parse_spans(text)

    assert result.clean_text == "Hello, world!"
    span = result.annotations[0]
    assert span.attrs.get("tag") == "lang"
    assert result.clean_text[span.char_start : span.char_end] == "world"


def test_adjacent_annotations():
    text = "[hello]{lang='en'}[world]{lang='en'}"
    result = ssmd.parse_spans(text, preserve_whitespace=True)

    assert result.clean_text == "helloworld"
    assert len(result.annotations) == 2
    assert result.annotations[0].attrs.get("tag") == "lang"
    assert (
        result.clean_text[
            result.annotations[0].char_start : result.annotations[0].char_end
        ]
        == "hello"
    )
    assert result.annotations[1].attrs.get("tag") == "lang"
    assert (
        result.clean_text[
            result.annotations[1].char_start : result.annotations[1].char_end
        ]
        == "world"
    )


def test_div_block_offsets():
    text = "<div lang='fr'>\nBonjour\n</div>"
    result = ssmd.parse_spans(text)

    assert result.clean_text == "Bonjour"
    span = next(s for s in result.annotations if s.attrs.get("lang") == "fr")
    assert span.attrs.get("tag") == "div"
    assert result.clean_text[span.char_start : span.char_end] == "Bonjour"


def test_sentence_iteration_offsets_match_clean_text():
    text = "Hello *world*. Next sentence."
    spans = ssmd.iter_sentences_spans(text, use_spacy=False)
    clean_text = ssmd.parse_spans(text).clean_text

    for sentence, start, end in spans:
        assert clean_text[start:end] == sentence
