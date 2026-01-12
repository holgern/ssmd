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
    return html.escape(text, quote=True)


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


# Unicode private use area characters for placeholders
# These won't conflict with normal text or SSMD syntax
_PLACEHOLDER_MAP = {
    "*": "\ue000",  # ASTERISK
    "_": "\ue001",  # UNDERSCORE
    "[": "\ue002",  # LEFT BRACKET
    "]": "\ue003",  # RIGHT BRACKET
    ".": "\ue004",  # DOT
    "@": "\ue005",  # AT SIGN
    "#": "\ue006",  # HASH
    "~": "\ue007",  # TILDE
    "+": "\ue008",  # PLUS
    "-": "\ue009",  # HYPHEN
    "<": "\ue00a",  # LESS THAN
    ">": "\ue00b",  # GREATER THAN
    "^": "\ue00c",  # CARET
}

# Reverse map for unescaping
_REVERSE_PLACEHOLDER_MAP = {v: k for k, v in _PLACEHOLDER_MAP.items()}


def escape_ssmd_syntax(
    text: str,
    patterns: list[str] | None = None,
) -> str:
    """Escape SSMD syntax patterns to prevent interpretation as markup.

    This is useful when processing plain text or markdown that may contain
    characters that coincidentally match SSMD syntax patterns. Uses placeholder
    replacement which is reversed after SSML processing.

    Args:
        text: Input text that may contain SSMD-like patterns
        patterns: List of pattern types to escape. If None, escapes all.
            Valid values: 'emphasis', 'annotations', 'breaks', 'marks',
            'headings', 'voice_directives', 'prosody_shorthand'

    Returns:
        Text with SSMD patterns replaced with placeholders

    Example:
        >>> text = "This *word* should not be emphasized"
        >>> escape_ssmd_syntax(text)
        'This \ue000word\ue000 should not be emphasized'

        >>> text = "Visit [our site](https://example.com)"
        >>> escaped = escape_ssmd_syntax(text)
        # Placeholders prevent SSMD interpretation

        >>> # Selective escaping
        >>> escape_ssmd_syntax(text, patterns=['emphasis', 'breaks'])
    """
    if patterns is None:
        # Escape all patterns by default
        patterns = [
            "emphasis",
            "annotations",
            "breaks",
            "marks",
            "headings",
            "voice_directives",
            "prosody_shorthand",
        ]

    result = text

    # Process patterns in specific order (most specific first)
    # Replace special characters with placeholders

    if "voice_directives" in patterns:
        # Voice directives at line start: @voice: or @voice(
        result = re.sub(
            r"^(@)voice([:(])",
            lambda m: _PLACEHOLDER_MAP["@"] + "voice" + m.group(2),
            result,
            flags=re.MULTILINE,
        )

    if "headings" in patterns:
        # Headings at line start: #, ##, ###
        result = re.sub(
            r"^(#{1,6})(\s)",
            lambda m: _PLACEHOLDER_MAP["#"] * len(m.group(1)) + m.group(2),
            result,
            flags=re.MULTILINE,
        )

    if "emphasis" in patterns:
        # Strong emphasis: **text**
        result = re.sub(
            r"\*\*([^*]+)\*\*",
            lambda m: _PLACEHOLDER_MAP["*"] * 2
            + m.group(1)
            + _PLACEHOLDER_MAP["*"] * 2,
            result,
        )
        # Moderate emphasis: *text*
        result = re.sub(
            r"\*([^*\n]+)\*",
            lambda m: _PLACEHOLDER_MAP["*"] + m.group(1) + _PLACEHOLDER_MAP["*"],
            result,
        )
        # Reduced emphasis/pitch: _text_ (but not in middle of words)
        result = re.sub(
            r"(?<!\w)_([^_\n]+)_(?!\w)",
            lambda m: _PLACEHOLDER_MAP["_"] + m.group(1) + _PLACEHOLDER_MAP["_"],
            result,
        )

    if "annotations" in patterns:
        # Annotations: [text](params) - replace the brackets
        result = re.sub(
            r"\[([^\]]+)\]\(([^)]+)\)",
            lambda m: _PLACEHOLDER_MAP["["]
            + m.group(1)
            + _PLACEHOLDER_MAP["]"]
            + "("
            + m.group(2)
            + ")",
            result,
        )

    if "breaks" in patterns:
        # Breaks: ...n, ...w, ...c, ...s, ...p, ...500ms, ...5s
        result = re.sub(
            r"\.\.\.((?:[nwcsp]|\d+(?:ms|s))(?:\s|$))",
            lambda m: _PLACEHOLDER_MAP["."] * 3 + m.group(1),
            result,
        )

    if "marks" in patterns:
        # Marks: @word (but not @voice which is handled above)
        # Use word boundary to avoid matching @domain in emails
        result = re.sub(
            r"(?<!\w)@(?!voice)(\w+)",
            lambda m: _PLACEHOLDER_MAP["@"] + m.group(1),
            result,
        )

    if "prosody_shorthand" in patterns:
        # Prosody shorthand - paired characters around text
        # Double character versions first
        result = re.sub(
            r"~~([^~\n]+)~~",
            lambda m: _PLACEHOLDER_MAP["~"] * 2
            + m.group(1)
            + _PLACEHOLDER_MAP["~"] * 2,
            result,
        )
        result = re.sub(
            r"\+\+([^+\n]+)\+\+",
            lambda m: _PLACEHOLDER_MAP["+"] * 2
            + m.group(1)
            + _PLACEHOLDER_MAP["+"] * 2,
            result,
        )
        result = re.sub(
            r"--([^-\n]+)--",
            lambda m: _PLACEHOLDER_MAP["-"] * 2
            + m.group(1)
            + _PLACEHOLDER_MAP["-"] * 2,
            result,
        )
        result = re.sub(
            r"<<([^<\n]+)<<",
            lambda m: _PLACEHOLDER_MAP["<"] * 2
            + m.group(1)
            + _PLACEHOLDER_MAP["<"] * 2,
            result,
        )
        result = re.sub(
            r">>([^>\n]+)>>",
            lambda m: _PLACEHOLDER_MAP[">"] * 2
            + m.group(1)
            + _PLACEHOLDER_MAP[">"] * 2,
            result,
        )
        result = re.sub(
            r"\^\^([^^|\n]+)\^\^",
            lambda m: _PLACEHOLDER_MAP["^"] * 2
            + m.group(1)
            + _PLACEHOLDER_MAP["^"] * 2,
            result,
        )
        result = re.sub(
            r"__([^_\n]+)__",
            lambda m: _PLACEHOLDER_MAP["_"] * 2
            + m.group(1)
            + _PLACEHOLDER_MAP["_"] * 2,
            result,
        )

        # Single character versions
        result = re.sub(
            r"~([^~\n]+)~",
            lambda m: _PLACEHOLDER_MAP["~"] + m.group(1) + _PLACEHOLDER_MAP["~"],
            result,
        )
        result = re.sub(
            r"\+([^+\n]+)\+",
            lambda m: _PLACEHOLDER_MAP["+"] + m.group(1) + _PLACEHOLDER_MAP["+"],
            result,
        )
        result = re.sub(
            r"-([^-\n]+)-",
            lambda m: _PLACEHOLDER_MAP["-"] + m.group(1) + _PLACEHOLDER_MAP["-"],
            result,
        )
        result = re.sub(
            r"<([^<\n]+)<",
            lambda m: _PLACEHOLDER_MAP["<"] + m.group(1) + _PLACEHOLDER_MAP["<"],
            result,
        )
        result = re.sub(
            r">([^>\n]+)>",
            lambda m: _PLACEHOLDER_MAP[">"] + m.group(1) + _PLACEHOLDER_MAP[">"],
            result,
        )
        result = re.sub(
            r"\^([^^\n]+)\^",
            lambda m: _PLACEHOLDER_MAP["^"] + m.group(1) + _PLACEHOLDER_MAP["^"],
            result,
        )

    return result


def unescape_ssmd_syntax(text: str) -> str:
    """Remove placeholder escaping from SSMD syntax.

    This is used internally to replace placeholders with original characters
    after TTS processing.

    Args:
        text: Text with placeholder-escaped SSMD syntax

    Returns:
        Text with placeholders replaced by original characters

    Example:
        >>> unescape_ssmd_syntax("This \ue000word\ue000 is escaped")
        'This *word* is escaped'
    """
    result = text
    # Replace all placeholders with their original characters
    for placeholder, original in _REVERSE_PLACEHOLDER_MAP.items():
        result = result.replace(placeholder, original)
    return result
