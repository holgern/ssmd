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
