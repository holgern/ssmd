"""SSMD annotations for extended syntax in [text](annotations) format."""

from typing import Optional

from ssmd.annotations.base import BaseAnnotation


def get_annotation(annotation_str: str) -> BaseAnnotation | None:
    """Try to create an annotation from a string.

    Args:
        annotation_str: Annotation string (e.g., "en", "ph: dIC", "vrp: 555")

    Returns:
        Annotation instance or None if no match
    """
    from ssmd.annotations.audio import AudioAnnotation
    from ssmd.annotations.extension import ExtensionAnnotation
    from ssmd.annotations.language import LanguageAnnotation
    from ssmd.annotations.phoneme import PhonemeAnnotation
    from ssmd.annotations.prosody import ProsodyAnnotation
    from ssmd.annotations.say_as import SayAsAnnotation
    from ssmd.annotations.substitution import SubstitutionAnnotation
    from ssmd.annotations.voice import VoiceAnnotation

    # Try each annotation type in order
    annotation_types: list[type[BaseAnnotation]] = [
        AudioAnnotation,  # Try audio first (has URL pattern)
        ExtensionAnnotation,  # Extensions (ext: name)
        VoiceAnnotation,  # Voice (voice: name, voice: lang)
        SayAsAnnotation,  # Say-as (as: type)
        PhonemeAnnotation,  # Phonemes (ph: ..., ipa: ...)
        ProsodyAnnotation,  # Prosody (vrp: 555, v: 5, etc.)
        SubstitutionAnnotation,  # Substitution (sub: alias)
        LanguageAnnotation,  # Language (en, en-US, etc.)
    ]

    for annotation_type in annotation_types:
        annotation = annotation_type.try_create(annotation_str)
        if annotation:
            return annotation

    return None


__all__ = ["get_annotation"]
