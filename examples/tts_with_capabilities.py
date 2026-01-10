#!/usr/bin/env python3
"""Example: TTS capability-based filtering.

This example demonstrates how SSMD automatically filters SSML features
based on the TTS engine's capabilities, ensuring compatibility.
"""

from ssmd import SSMD, TTSCapabilities

# Sample SSMD text with various features
SAMPLE_TEXT = """
# Welcome to SSMD

This is a *powerful* text-to-speech system... with many features.

[Command & Conquer](en) is a *classic* game.

You can adjust [volume](v: 5) and [speed](r: 3) easily.

Call us at [+1-555-1234](as: telephone) or visit our website.

Some systems support [whispered text](ext: whisper) too!
"""


def demo_preset(preset_name: str):
    """Demonstrate a TTS preset capability.

    Args:
        preset_name: Name of the preset (espeak, pyttsx3, google, etc.)
    """
    print(f"\n{'=' * 70}")
    print(f"Preset: {preset_name.upper()}")
    print(f"{'=' * 70}")

    parser = SSMD(capabilities=preset_name)
    ssml = parser.to_ssml(SAMPLE_TEXT)

    print(ssml)


def demo_custom_capabilities():
    """Demonstrate custom capability configuration."""
    print(f"\n{'=' * 70}")
    print("CUSTOM: Basic TTS with breaks only")
    print(f"{'=' * 70}")

    # Create custom capabilities (only supports breaks and paragraphs)
    custom_caps = TTSCapabilities(
        emphasis=False,  # No emphasis
        break_tags=True,  # Supports pauses
        paragraph=True,  # Supports paragraphs
        language=False,  # No language switching
        phoneme=False,  # No phonetic pronunciation
        substitution=False,  # No alias substitution
        prosody=False,  # No volume/rate/pitch
        say_as=False,  # No interpret-as
        audio=False,  # No audio files
        mark=False,  # No markers
        sentence_tags=False,  # No sentence tags
        heading_emphasis=False,  # No heading emphasis
    )

    parser = SSMD(capabilities=custom_caps)
    ssml = parser.to_ssml(SAMPLE_TEXT)

    print(ssml)


def demo_comparison():
    """Compare output for different TTS engines side by side."""
    print(f"\n{'=' * 70}")
    print("COMPARISON: Same input, different TTS capabilities")
    print(f"{'=' * 70}")

    simple_text = "*Hello* world... [this is loud](v: 5)!"

    engines = ["minimal", "pyttsx3", "espeak", "google"]

    for engine in engines:
        parser = SSMD(capabilities=engine)
        ssml = parser.to_ssml(simple_text)

        print(f"\n{engine.upper():>12}: {ssml}")


def demo_streaming_with_capabilities():
    """Demonstrate streaming TTS with capability filtering."""
    print(f"\n{'=' * 70}")
    print("STREAMING: pyttsx3 engine (minimal SSML support)")
    print(f"{'=' * 70}")

    # pyttsx3 has minimal SSML support - most features will be stripped
    parser = SSMD(capabilities="pyttsx3")
    doc = parser.load(SAMPLE_TEXT)

    print(f"Total sentences: {len(doc)}\n")

    # Iterate through sentences for streaming
    for i, sentence in enumerate(doc, 1):
        plain = parser.strip(sentence)
        print(f"[{i}/{len(doc)}] SSML: {sentence}")
        print(f"{'':14} Text: {plain}\n")


if __name__ == "__main__":
    print("=" * 70)
    print("SSMD TTS Capability Demonstration")
    print("=" * 70)
    print("\nThis demo shows how SSMD automatically filters unsupported SSML")
    print("features based on the TTS engine's capabilities.")

    # Demonstrate different presets
    demo_preset("minimal")  # Plain text only
    demo_preset("pyttsx3")  # Very limited SSML
    demo_preset("espeak")  # Moderate SSML support
    demo_preset("google")  # Full SSML support

    # Custom capabilities
    demo_custom_capabilities()

    # Side-by-side comparison
    demo_comparison()

    # Streaming with capabilities
    demo_streaming_with_capabilities()

    print(f"\n{'=' * 70}")
    print("Demo complete!")
    print(f"{'=' * 70}")
