"""Shared SSML/SSMD conversion tables."""

PROSODY_VOLUME_MAP = {
    "0": "silent",
    "1": "x-soft",
    "2": "soft",
    "3": "medium",
    "4": "loud",
    "5": "x-loud",
}

PROSODY_RATE_MAP = {
    "1": "x-slow",
    "2": "slow",
    "3": "medium",
    "4": "fast",
    "5": "x-fast",
}

PROSODY_PITCH_MAP = {
    "1": "x-low",
    "2": "low",
    "3": "medium",
    "4": "high",
    "5": "x-high",
}

SSML_VOLUME_TO_NUMERIC = {
    "silent": 0,
    "x-soft": 1,
    "soft": 2,
    "medium": 3,
    "loud": 4,
    "x-loud": 5,
}

SSML_RATE_TO_NUMERIC = {
    "x-slow": 1,
    "slow": 2,
    "medium": 3,
    "fast": 4,
    "x-fast": 5,
}

SSML_PITCH_TO_NUMERIC = {
    "x-low": 1,
    "low": 2,
    "medium": 3,
    "high": 4,
    "x-high": 5,
}

SSMD_VOLUME_SHORTHAND = {
    "silent": ("~", "~"),
    "x-soft": ("--", "--"),
    "soft": ("-", "-"),
    "loud": ("+", "+"),
    "x-loud": ("++", "++"),
}

SSMD_RATE_SHORTHAND = {
    "x-slow": ("<<", "<<"),
    "slow": ("<", "<"),
    "fast": (">", ">"),
    "x-fast": (">>", ">>"),
}

SSMD_PITCH_SHORTHAND = {
    "x-low": ("__", "__"),
    "low": ("_", "_"),
    "high": ("^", "^"),
    "x-high": ("^^", "^^"),
}

SSML_VOLUME_SHORTHAND = {
    "silent": ("~", "~"),
    "x-soft": ("--", "--"),
    "soft": ("-", "-"),
    "medium": ("", ""),
    "loud": ("+", "+"),
    "x-loud": ("++", "++"),
}

SSML_RATE_SHORTHAND = {
    "x-slow": ("<<", "<<"),
    "slow": ("<", "<"),
    "medium": ("", ""),
    "fast": (">", ">"),
    "x-fast": (">>", ">>"),
}

SSML_PITCH_SHORTHAND = {
    "x-low": ("vv", "vv"),
    "low": ("v", "v"),
    "medium": ("", ""),
    "high": ("^", "^"),
    "x-high": ("^^", "^^"),
}

SSMD_BREAK_STRENGTH_MAP = {
    "none": "...n",
    "x-weak": "...w",
    "weak": "...w",
    "medium": "...c",
    "strong": "...s",
    "x-strong": "...p",
}

SSML_BREAK_STRENGTH_MAP = {
    "none": "",
    "x-weak": ".",
    "weak": ".",
    "medium": "...",
    "strong": "...s",
    "x-strong": "...p",
}

SSMD_BREAK_MARKER_TO_STRENGTH = {
    "n": "none",
    "w": "x-weak",
    "c": "medium",
    "s": "strong",
    "p": "x-strong",
}
