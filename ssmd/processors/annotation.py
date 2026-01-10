"""Annotation processor: [text](annotations) → various SSML tags"""

import re

from ssmd.annotations import get_annotation
from ssmd.annotations.base import BaseAnnotation
from ssmd.processors.base import BaseProcessor


class AnnotationProcessor(BaseProcessor):
    """Process annotation markup [text](annotations).

    Annotations can include:
    - Language codes: [text](en), [text](en-GB)
    - Voice: [text](voice: Joanna), [text](voice: en-US, gender: female)
    - Phonemes: [text](ph: dIC), [text](ipa: dɪç)
    - Prosody: [text](vrp: 555), [text](v: 5, r: 3, p: 1)
    - Substitution: [text](sub: alias)
    - Say-as: [text](as: telephone)
    - Audio: [text](url.mp3 alt text)
    - Extensions: [text](ext: whisper)
    """

    name = "annotation"

    def regex(self) -> re.Pattern:
        """Match [text](annotations) pattern.

        Returns:
            Pattern matching annotation syntax
        """
        return re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")

    def _is_annotation_supported(self, annotation: BaseAnnotation) -> bool:
        """Check if annotation is supported by current capabilities.

        Args:
            annotation: Annotation instance to check

        Returns:
            True if supported or no capability restrictions
        """
        capabilities = self.config.get("capabilities")
        if not capabilities:
            return True

        # Import annotation types for checking
        from ssmd.annotations.audio import AudioAnnotation
        from ssmd.annotations.extension import ExtensionAnnotation
        from ssmd.annotations.language import LanguageAnnotation
        from ssmd.annotations.phoneme import PhonemeAnnotation
        from ssmd.annotations.prosody import ProsodyAnnotation
        from ssmd.annotations.say_as import SayAsAnnotation
        from ssmd.annotations.substitution import SubstitutionAnnotation
        from ssmd.annotations.voice import VoiceAnnotation

        # Check annotation type against capabilities
        if isinstance(annotation, LanguageAnnotation):
            return capabilities.language
        elif isinstance(annotation, PhonemeAnnotation):
            return capabilities.phoneme
        elif isinstance(annotation, SubstitutionAnnotation):
            return capabilities.substitution
        elif isinstance(annotation, SayAsAnnotation):
            return capabilities.say_as
        elif isinstance(annotation, AudioAnnotation):
            return capabilities.audio
        elif isinstance(annotation, VoiceAnnotation):
            # Voice is generally supported by cloud TTS but not by basic engines
            return getattr(capabilities, "voice", True)
        elif isinstance(annotation, ProsodyAnnotation):
            # For prosody annotations, check if any attribute is supported
            return capabilities.prosody
        elif isinstance(annotation, ExtensionAnnotation):
            # Check specific extension support
            ext_name = getattr(annotation, "extension_name", None)
            if ext_name:
                return capabilities.supports_extension(ext_name)
            return False

        # Unknown annotation type - allow it
        return True

    def result(self, match: re.Match) -> str:
        """Convert to SSML using appropriate annotation handlers.

        Args:
            match: Regex match object

        Returns:
            SSML with annotations applied
        """
        text = match.group(1)
        annotations_str = match.group(2)

        # Check if this is a voice annotation (which may contain commas)
        # Voice annotations should be matched as a whole before comma-splitting
        from ssmd.annotations.voice import VoiceAnnotation

        voice_pattern = VoiceAnnotation.regex()
        voice_match = voice_pattern.match(annotations_str.strip())
        if voice_match is not None:
            # This is a voice annotation - don't split by comma
            voice_annotation = VoiceAnnotation(voice_match)
            if self._is_annotation_supported(voice_annotation):
                return voice_annotation.wrap(text)
            else:
                return text  # Return plain text if not supported

        # Parse comma-separated annotations (for non-voice annotations)
        annotation_parts = [a.strip() for a in annotations_str.split(",")]

        # Build list of unique annotations (combining duplicates)
        annotations: list[BaseAnnotation] = []
        for part in annotation_parts:
            ann = get_annotation(part)
            if ann is not None:
                # Filter based on capabilities
                if not self._is_annotation_supported(ann):
                    continue  # Skip unsupported annotation

                # Check if we already have this type
                existing = next(
                    (a for a in annotations if isinstance(a, type(ann))),
                    None,
                )
                if existing:
                    # Combine with existing (first wins by default)
                    existing.combine(ann)
                else:
                    annotations.append(ann)

        # Wrap text in annotations (innermost to outermost)
        result = text
        for ann in annotations:
            result = ann.wrap(result)

        return result

    def text(self, match: re.Match) -> str:
        """Extract plain text from annotation.

        Args:
            match: Regex match object

        Returns:
            Text without annotation parameters
        """
        return match.group(1)
