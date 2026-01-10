"""Utility functions for SSMD processing."""

import html
import re


def escape_xml(text: str) -> str:
    """Escape XML special characters.

    Args:
        text: Input text to escape

    Returns:
        Text with XML entities escaped
    """
    return html.escape(text, quote=False)


def unescape_xml(text: str) -> str:
    """Unescape XML entities.

    Args:
        text: Text with XML entities

    Returns:
        Unescaped text
    """
    return html.unescape(text)


def format_xml(xml_text: str, pretty: bool = True) -> str:
    """Format XML with optional pretty printing.

    Args:
        xml_text: XML string to format
        pretty: Enable pretty printing

    Returns:
        Formatted XML string
    """
    if not pretty:
        return xml_text

    try:
        from xml.dom import minidom

        dom = minidom.parseString(xml_text)
        return dom.toprettyxml(indent="  ", encoding=None)
    except Exception:
        # Fallback: return as-is if parsing fails
        return xml_text


def extract_sentences(ssml: str) -> list[str]:
    """Extract sentences from SSML.

    Looks for <s> tags or splits by sentence boundaries.

    Args:
        ssml: SSML string

    Returns:
        List of SSML sentence strings
    """
    # First try to extract <s> tags
    s_tag_pattern = re.compile(r"<s>(.*?)</s>", re.DOTALL)
    sentences = s_tag_pattern.findall(ssml)

    if sentences:
        return sentences

    # Fallback: extract <p> tags
    p_tag_pattern = re.compile(r"<p>(.*?)</p>", re.DOTALL)
    paragraphs = p_tag_pattern.findall(ssml)

    if paragraphs:
        return paragraphs

    # Last resort: remove <speak> wrapper and return as single sentence
    clean = re.sub(r"</?speak>", "", ssml).strip()
    return [clean] if clean else []
