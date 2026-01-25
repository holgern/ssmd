import ssmd
from ssmd.paragraph import Paragraph


def test_parse_ssmd_returns_paragraphs():
    paragraphs = ssmd.parse_ssmd("Hello world.")

    assert isinstance(paragraphs, list)
    assert paragraphs
    assert isinstance(paragraphs[0], Paragraph)
    assert paragraphs[0].sentences


def test_parser_types_aliases():
    import ssmd.parser_types as parser_types
    from ssmd.segment import Segment
    from ssmd.sentence import Sentence

    assert parser_types.SSMDSegment is Segment
    assert parser_types.SSMDSentence is Sentence
