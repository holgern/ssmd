"""Example: Using SSMD as a TTS document container.

This example demonstrates how to use SSMD to load a document
and iterate through sentences for streaming TTS applications.
"""

import time

from ssmd import SSMD


class MockTTSEngine:
    """Mock TTS engine for demonstration purposes."""

    def speak(self, ssml: str):
        """Simulate speaking SSML text."""
        # Extract text content (simple approach)
        import re

        text = re.sub(r"<[^>]+>", "", ssml)
        print(f"  🔊 Speaking: {text[:50]}...")

        # Simulate speaking time (0.1s per 10 characters)
        time.sleep(len(text) * 0.01)

    def wait_until_done(self):
        """Wait for speech to complete."""
        # In a real implementation, this would block until TTS finishes
        pass


def main():
    """Main demo function."""
    print("=" * 70)
    print("SSMD TTS Document Container Demo")
    print("=" * 70)

    # Sample SSMD document
    document = """
# Welcome to SSMD
Hello and *welcome* to our presentation!
Today we'll discuss some ...200ms exciting topics.

# What is SSMD?
SSMD stands for [Speech Synthesis Markdown](sub: S S M D).
It's a ++much easier++ way to write TTS content!

# Features
You can use all kinds of markup:
- Pauses ...500ms like this
- [Different languages](de) wie das
- Even [phonetic pronunciations](ph: f@nEtIk)

# Conclusion
Thank you for listening @end_marker!
[Goodbye](v: 3, p: 4)!
"""

    # Create parser with sentence tags enabled
    parser = SSMD(
        {
            "auto_sentence_tags": True,
            "output_speak_tag": False,  # Individual sentences don't need <speak>
        }
    )

    # Load document
    print("\n📄 Loading SSMD document...")
    doc = parser.load(document)

    # Show document info
    print(f"   Total sentences: {len(doc)}")
    print(f"   Plain text length: {len(doc.plain_text)} characters")

    # Show plain text version
    print("\n📝 Plain text version:")
    print("-" * 70)
    print(doc.plain_text)
    print("-" * 70)

    # Create mock TTS engine
    tts = MockTTSEngine()

    # Process sentences one by one
    print(f"\n🎤 Processing {len(doc)} sentences...")
    print("=" * 70)

    for i, sentence in enumerate(doc, 1):
        print(f"\n[{i}/{len(doc)}]")
        print(f"  SSML: {sentence[:60]}...")
        tts.speak(sentence)
        tts.wait_until_done()

    print("\n" + "=" * 70)
    print("✅ Document reading complete!")
    print("=" * 70)

    # Demonstrate random access
    print("\n🔍 Random access demo:")
    print(f"   First sentence: {doc[0][:60]}...")
    print(f"   Last sentence: {doc[-1][:60]}...")

    # Show full SSML
    print("\n📋 Full SSML output:")
    print("-" * 70)
    print(parser.to_ssml(document)[:500] + "...")
    print("-" * 70)


if __name__ == "__main__":
    main()
