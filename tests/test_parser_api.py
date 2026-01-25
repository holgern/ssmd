import ssmd
from ssmd.paragraph import Paragraph


def test_parse_ssmd_returns_paragraphs():
    paragraphs = ssmd.parse_ssmd("Hello world.")

    assert isinstance(paragraphs, list)
    assert paragraphs
    assert isinstance(paragraphs[0], Paragraph)
    assert paragraphs[0].sentences
