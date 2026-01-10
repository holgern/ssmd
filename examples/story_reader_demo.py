"""Example: Processing a story book for TTS reading.

This example demonstrates how to use SSMD to:
1. Load a long document (like a story or ebook chapter)
2. Process it with markup for better TTS output
3. Iterate through sentences for streaming TTS
4. Track progress and handle pauses
"""

import re

from ssmd import Document


def read_story_chapter() -> str:
    """Example story chapter with SSMD markup."""
    story = """
# Chapter 3: The Discovery

[Emma](en-GB) stepped into the dusty library ...800ms her eyes adjusting to
the dim light. ++"This is it"++ she whispered to herself.
The ancient book lay on the pedestal @book_location, exactly where the
[map](sub: treasure map) had indicated.

She approached slowly, her footsteps echoing in the silence.
Each step seemed to say [[kri:k]](ph: kri:k) in the quiet.

# The Revelation

As she opened the book ...1s a brilliant *golden light* erupted from the pages!
The text was in [Latin](la), but somehow she could understand it perfectly.

^^"By the power vested in these pages"^^ the book seemed to say,
"knowledge shall flow to those who seek it with a pure heart."

Emma felt a warmth spreading through her fingers.
She knew @moment_of_truth that her life would never be the same again ...2s

"""
    return story


def main() -> None:
    """Main demo showing TTS document processing."""
    print("=" * 80)
    print("📖 SSMD Story Reader Demo")
    print("=" * 80)

    # Create document optimized for storytelling
    config = {
        "auto_sentence_tags": True,  # Wrap each sentence in <s>
        "output_speak_tag": True,  # Include <speak> wrapper
        "heading_levels": {
            1: [("emphasis", "strong"), ("pause", "500ms")],  # Chapter titles
            2: [("emphasis", "moderate"), ("pause", "300ms")],  # Sections
        },
    }

    # Load story
    story = read_story_chapter()
    doc = Document(story, config=config)

    print(f"\n📚 Story loaded: {len(doc)} sentences")
    print(f"📝 Plain text: {len(doc.to_text())} characters\n")

    # Show plain text version
    print("-" * 80)
    print("PLAIN TEXT VERSION:")
    print("-" * 80)
    print(doc.to_text())
    print("-" * 80)

    # Simulate TTS reading with progress tracking
    print("\n🎙️  Reading story aloud...")
    print("=" * 80)

    for i in range(len(doc)):
        sentence = doc[i]

        # Calculate progress
        progress = ((i + 1) / len(doc)) * 100
        bar_length = 40
        filled = int(bar_length * (i + 1) // len(doc))
        bar = "█" * filled + "░" * (bar_length - filled)

        # Show progress
        print(f"\n[{i + 1:2d}/{len(doc):2d}] {bar} {progress:5.1f}%")

        # Show SSML (truncated for display)
        ssml_preview = sentence[:70] + "..." if len(sentence) > 70 else sentence
        print(f"SSML: {ssml_preview}")

        # In a real application, you would:
        # 1. Convert SSML to audio using your TTS engine
        # 2. Play the audio
        # 3. Wait for completion before next sentence
        #
        # Example:
        # audio = tts_engine.synthesize(sentence)
        # tts_engine.play(audio)
        # tts_engine.wait_until_done()

    print("\n" + "=" * 80)
    print("✅ Story reading complete!")
    print("=" * 80)

    # Show random access capability
    print("\n🔍 Random Access Examples:")
    print(f"   First sentence: {doc[0][:60]}...")
    print(f"   Middle sentence: {doc[len(doc) // 2][:60]}...")
    print(f"   Last sentence: {doc[-1][:60]}...")

    # Show full SSML for one sentence
    print("\n📋 Example SSML for first sentence:")
    print("-" * 80)
    print(doc[0])
    print("-" * 80)

    # Show how to get specific metadata
    print("\n📊 Document Statistics:")
    print(f"   Total sentences: {len(doc)}")
    print(f"   Characters (plain): {len(doc.to_text())}")
    print(f"   Characters (SSML): {len(doc.to_ssml())}")
    print(f"   SSML overhead: {len(doc.to_ssml()) - len(doc.to_text())} chars")

    # Show how you might use this for chapter navigation
    print("\n📑 Chapter Navigation Pattern:")
    print("   You can split by headings and create bookmarks:")

    chapter_starts = []
    for i in range(len(doc)):
        sentence = doc[i]
        if '<emphasis level="strong">' in sentence:  # Heading 1
            chapter_starts.append(i)
            # Extract chapter name (simple approach)
            match = re.search(r'<emphasis level="strong">([^<]+)</emphasis>', sentence)
            if match:
                print(f"   - Sentence {i}: {match.group(1)}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
