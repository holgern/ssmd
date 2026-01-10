"""Example: Using SSMD Document as a TTS container.

This example demonstrates how to use SSMD Document to build and
iterate through content for streaming TTS applications.
"""

import time

from ssmd import Document


class MockTTSEngine:
    """Mock TTS engine for demonstration purposes."""

    def speak(self, ssml: str) -> None:
        """Simulate speaking SSML text."""
        # Extract text content (simple approach)
        import re

        text = re.sub(r"<[^>]+>", "", ssml)
        print(f"  🔊 Speaking: {text[:50]}...")

        # Simulate speaking time (0.1s per 10 characters)
        time.sleep(len(text) * 0.01)

    def wait_until_done(self) -> None:
        """Wait for speech to complete."""
        # In a real implementation, this would block until TTS finishes
        pass


def main() -> None:
    """Main demo function."""
    print("=" * 70)
    print("SSMD Document Container Demo")
    print("=" * 70)

    # Create document and build it incrementally
    doc = Document(config={"auto_sentence_tags": True})

    # Build document piece by piece
    doc.add_paragraph("# Welcome to SSMD")
    doc.add_sentence("Hello and *welcome* to our presentation!")
    doc.add_sentence("Today we'll discuss some ...200ms exciting topics.")

    doc.add_paragraph("# What is SSMD?")
    doc.add_sentence("SSMD stands for [Speech Synthesis Markdown](sub: S S M D).")
    doc.add_sentence("It's a ++much easier++ way to write TTS content!")

    doc.add_paragraph("# Features")
    doc.add_sentence("You can use all kinds of markup:")
    doc.add_sentence("- Pauses ...500ms like this")
    doc.add_sentence("- [Different languages](de) wie das")
    doc.add_sentence("- Even [phonetic pronunciations](ph: f@nEtIk)")

    doc.add_paragraph("# Conclusion")
    doc.add_sentence("Thank you for listening @end_marker!")
    doc.add_sentence("[Goodbye](v: 3, p: 4)!")

    # Show document info
    print("\n📄 Document Summary:")
    print(f"   Total sentences: {len(doc)}")
    print(f"   Total characters: {len(doc.ssmd)}")

    # Show plain text version
    print("\n📝 Plain text version:")
    print("-" * 70)
    print(doc.to_text())
    print("-" * 70)

    # Create mock TTS engine
    tts = MockTTSEngine()

    # Process sentences one by one
    print(f"\n🎤 Processing {len(doc)} sentences...")
    print("=" * 70)

    for i in range(len(doc)):
        sentence_ssml = doc[i]
        print(f"\n[{i + 1}/{len(doc)}]")
        print(f"  SSML: {sentence_ssml[:60]}...")
        tts.speak(sentence_ssml)
        tts.wait_until_done()

    print("\n" + "=" * 70)
    print("✅ Document reading complete!")
    print("=" * 70)

    # Demonstrate document editing
    print("\n🔧 Document Editing Demo:")
    print(f"   Original first sentence: {doc[0][:50]}...")
    doc[0] = "Modified opening sentence!"
    print(f"   Modified first sentence: {doc[0][:50]}...")

    # Show SSMD content
    print("\n📋 Raw SSMD content (first 300 chars):")
    print("-" * 70)
    print(doc.ssmd[:300] + "...")
    print("-" * 70)


if __name__ == "__main__":
    main()
