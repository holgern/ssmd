"""
SSMD Parser Demo - Shows how to parse SSMD into structured segments.

This demo shows how to use the SSMD parser to extract structured data
from SSMD text instead of generating SSML. This is useful when you need
to process SSMD features programmatically or build your own TTS pipeline.

The parser extracts:
- Voice directives and attributes
- Text transformations (say-as, substitution, phoneme)
- Prosody and emphasis markers
- Breaks and pauses
- Language annotations

Each sentence is broken down into segments that can be processed individually
or reassembled into complete sentences for TTS engines.
"""

from ssmd import (
    parse_segments,
    parse_sentences,
    parse_voice_blocks,
)


def example_1_basic_parsing():
    """Example 1: Basic parsing - Extract segments from simple text."""
    print("=" * 60)
    print("Example 1: Basic Parsing")
    print("=" * 60)

    text = "Hello *world*! This is ...500ms great."

    # Parse into segments
    segments = parse_segments(text)

    print(f"\nInput text: {text}")
    print(f"\nExtracted {len(segments)} segments:")

    for i, seg in enumerate(segments, 1):
        print(f"\n  Segment {i}:")
        print(f"    Text: {seg.text!r}")
        if seg.emphasis:
            print("    Emphasis: True")
        if seg.breaks_after:
            for brk in seg.breaks_after:
                print(f"    Break after: {brk.time}")


def example_2_text_transformations():
    """Example 2: Text transformations - say-as, substitution, phoneme."""
    print("\n" + "=" * 60)
    print("Example 2: Text Transformations")
    print("=" * 60)

    text = """
Call [+1-555-0123](as: telephone) for info.
[H2O](sub: water) is important.
Say [tomato](ph: təˈmeɪtoʊ) correctly.
"""

    segments = parse_segments(text)

    print(f"\nInput text: {text.strip()}")
    print(f"\nExtracted {len(segments)} segments:\n")

    for seg in segments:
        if seg.say_as:
            print(f"  SAY-AS: {seg.text!r} -> interpret as {seg.say_as.interpret_as}")
        elif seg.substitution:
            print(f"  SUBSTITUTION: {seg.text!r} -> speak as {seg.substitution!r}")
        elif seg.phoneme:
            print(f"  PHONEME: {seg.text!r} -> pronounce as {seg.phoneme.ph!r}")


def example_3_voice_blocks():
    """Example 3: Voice blocks - Multi-voice dialogue."""
    print("\n" + "=" * 60)
    print("Example 3: Voice Blocks")
    print("=" * 60)

    script = """
@voice: sarah
Welcome to the show!

@voice: michael
Thanks Sarah! Great to be here.

@voice: sarah
Let's begin!
"""

    # Parse voice blocks
    blocks = parse_voice_blocks(script)

    print(f"\nInput script: {script.strip()}")
    print(f"\nExtracted {len(blocks)} voice blocks:\n")

    for i, (voice, text) in enumerate(blocks, 1):
        if voice:
            print(f"  Block {i}: {voice.name} says: {text.strip()!r}")
        else:
            print(f"  Block {i}: (default voice) says: {text.strip()!r}")


def example_4_complete_workflow():
    """Example 4: Complete TTS workflow - Build sentences from segments."""
    print("\n" + "=" * 60)
    print("Example 4: Complete TTS Workflow")
    print("=" * 60)

    script = """
@voice: sarah
Hello! Call [+1-555-0123](as: telephone) for more info.
[H2O](sub: water) is important.

@voice: michael
Thanks *Sarah*! That's very helpful.
"""

    sentences = parse_sentences(script)

    print(f"\nInput script: {script.strip()}")
    print(f"\nExtracted {len(sentences)} sentences:\n")

    # Process each sentence
    for i, sentence in enumerate(sentences, 1):
        print(f"Sentence {i}:")

        # Get voice info
        if sentence.voice:
            print(f"  Voice: {sentence.voice.name}")
        else:
            print("  Voice: (default)")

        # Build complete sentence from segments
        full_text = ""
        metadata = []

        for seg in sentence.segments:
            # Handle text transformations
            if seg.say_as:
                # In a real TTS engine, you'd convert this based on interpret_as
                text_to_speak = seg.text  # Simplified - TTS engine handles conversion
                metadata.append(f"say-as:{seg.say_as.interpret_as}")
                full_text += text_to_speak
            elif seg.substitution:
                # Use the substitution text instead of original
                full_text += seg.substitution
            elif seg.phoneme:
                # Use phoneme for pronunciation
                text_to_speak = seg.text  # TTS engine uses phoneme data
                metadata.append(f"phoneme:{seg.phoneme.ph}")
                full_text += text_to_speak
            else:
                # Plain text
                full_text += seg.text

            # Track emphasis
            if seg.emphasis:
                metadata.append("emphasis")

            # Handle breaks
            for brk in seg.breaks_after:
                metadata.append(f"break:{brk.time}")

        print(f"  Text: {full_text!r}")
        if metadata:
            print(f"  Metadata: {', '.join(metadata)}")
        print()


def example_5_prosody_and_language():
    """Example 5: Prosody and language annotations."""
    print("\n" + "=" * 60)
    print("Example 5: Prosody and Language")
    print("=" * 60)

    text = "[loud announcement](v: 5) followed by [Bonjour](fr) everyone"

    segments = parse_segments(text)

    print(f"\nInput text: {text}")
    print(f"\nExtracted {len(segments)} segments:\n")

    for seg in segments:
        print(f"  Text: {seg.text!r}")
        if seg.prosody:
            if seg.prosody.volume:
                print(f"    Prosody volume: {seg.prosody.volume}")
            if seg.prosody.rate:
                print(f"    Prosody rate: {seg.prosody.rate}")
            if seg.prosody.pitch:
                print(f"    Prosody pitch: {seg.prosody.pitch}")
        if seg.language:
            print(f"    Language: {seg.language}")


def example_6_advanced_sentence_parsing():
    """Example 6: Advanced sentence parsing with options."""
    print("\n" + "=" * 60)
    print("Example 6: Advanced Sentence Parsing")
    print("=" * 60)

    text = """
Welcome to the demo.

This is a new paragraph. It has multiple sentences.

@voice: sarah
Sarah speaks here.
"""

    # Parse with sentence detection enabled
    sentences = parse_sentences(
        text,
        sentence_detection=True,  # Split by sentences
        include_default_voice=True,  # Include text before first @voice
    )

    print(f"\nInput text: {text.strip()}")
    print(f"\nExtracted {len(sentences)} sentences:\n")

    for i, sent in enumerate(sentences, 1):
        voice_name = sent.voice.name if sent.voice else "(default)"
        # Reconstruct text from segments
        text_content = "".join(seg.text for seg in sent.segments)
        para_marker = " [PARAGRAPH END]" if sent.is_paragraph_end else ""

        print(f"  {i}. [{voice_name}] {text_content!r}{para_marker}")


def example_7_capabilities_filtering():
    """Example 7: Capabilities filtering - Engine-specific parsing."""
    print("\n" + "=" * 60)
    print("Example 7: Capabilities Filtering")
    print("=" * 60)

    from ssmd import get_preset

    text = """
Hello *everyone*! Call [+1-555-0123](as: telephone).
Say [tomato](ph: təˈmeɪtoʊ) in [Français](fr).
"""

    print(f"\nInput text: {text.strip()}")

    # Parse with Google capabilities (full support)
    google_sentences = parse_sentences(text, capabilities="google")
    print(f"\n1. Google TTS (full support): {len(google_sentences)} sentences")

    # Parse with eSpeak capabilities (limited support)
    espeak_sentences = parse_sentences(text, capabilities="espeak")
    print(f"2. eSpeak (limited support): {len(espeak_sentences)} sentences")

    # Parse with custom capabilities
    from ssmd import TTSCapabilities

    custom_caps = TTSCapabilities(
        emphasis=True,
        say_as=False,  # Disable say-as
        phoneme=False,  # Disable phoneme
        language=True,
    )
    custom_sentences = parse_sentences(text, capabilities=custom_caps)
    print(f"3. Custom capabilities: {len(custom_sentences)} sentences")

    # Show SSML output differences
    print("\nSSML output comparison:")
    for sent in google_sentences[:2]:
        ssml = sent.to_ssml()
        print(f"  Google: {ssml[:60]}...")

    for sent in espeak_sentences[:2]:
        ssml = sent.to_ssml(get_preset("espeak"))
        print(f"  eSpeak: {ssml[:60]}...")


def example_8_multilingual():
    """Example 8: Multi-language sentence detection."""
    print("\n" + "=" * 60)
    print("Example 8: Multi-Language Support")
    print("=" * 60)

    # English text
    english_text = "Hello! How are you? I'm fine, thanks."
    en_sentences = parse_sentences(english_text, language="en")
    print(f"\nEnglish ({len(en_sentences)} sentences):")
    for sent in en_sentences:
        print(f"  - {sent.to_text()!r}")

    # German text - may require spaCy model: python -m spacy download de_core_web_sm
    german_text = "Guten Tag! Wie geht es Ihnen? Mir geht es gut, danke."
    try:
        de_sentences = parse_sentences(german_text, language="de")
        print(f"\nGerman ({len(de_sentences)} sentences):")
        for sent in de_sentences:
            print(f"  - {sent.to_text()!r}")
    except OSError:
        print("\nGerman: Skipped - spaCy model not installed")
        print("  Install with: python -m spacy download de_core_web_sm")

    # French text - may require spaCy model: python -m spacy download fr_core_news_sm
    french_text = "Bonjour! Comment allez-vous? Je vais bien, merci."
    try:
        fr_sentences = parse_sentences(french_text, language="fr")
        print(f"\nFrench ({len(fr_sentences)} sentences):")
        for sent in fr_sentences:
            print(f"  - {sent.to_text()!r}")
    except OSError:
        print("\nFrench: Skipped - spaCy model not installed")
        print("  Install with: python -m spacy download fr_core_news_sm")

    print("\nNote: Multi-language support requires spaCy language models.")
    print("Without them, basic regex-based sentence splitting is used.")


def example_9_sentence_attributes():
    """Example 9: Inspecting Sentence object attributes."""
    print("\n" + "=" * 60)
    print("Example 9: Sentence Object Attributes")
    print("=" * 60)

    text = """
@voice: sarah, language: en-US
Welcome to the show! This is *amazing*.

@voice: michael, gender: male
Thanks for having me.

Final thoughts here.
"""

    sentences = parse_sentences(text, sentence_detection=True)

    print(f"\nParsed {len(sentences)} sentences:\n")

    for i, sent in enumerate(sentences, 1):
        print(f"Sentence {i}:")

        # Voice attributes
        if sent.voice:
            print(f"  voice.name: {sent.voice.name}")
            print(f"  voice.language: {sent.voice.language}")
            print(f"  voice.gender: {sent.voice.gender}")
        else:
            print("  voice: (default)")

        # Paragraph info
        print(f"  is_paragraph_end: {sent.is_paragraph_end}")

        # Breaks after sentence
        if sent.breaks_after:
            breaks = [f"{b.time or b.strength}" for b in sent.breaks_after]
            print(f"  breaks_after: {breaks}")

        # Segment count
        print(f"  segments: {len(sent.segments)}")

        # Text content
        print(f"  text: {sent.to_text()!r}")
        print()


def example_10_output_formats():
    """Example 10: Different output formats from sentences."""
    print("\n" + "=" * 60)
    print("Example 10: Output Formats")
    print("=" * 60)

    text = """
@voice: narrator
*Hello* everyone! Call [+1-800-555-0123](as: telephone) for info.
"""

    sentences = parse_sentences(text)

    print(f"\nInput: {text.strip()}")
    print(f"\nParsed {len(sentences)} sentences:\n")

    for i, sent in enumerate(sentences, 1):
        print(f"Sentence {i}:")

        # Plain text (no markup)
        print(f"  to_text():  {sent.to_text()!r}")

        # SSML output
        print(f"  to_ssml():  {sent.to_ssml()}")

        # SSMD output (can regenerate SSMD from parsed data)
        print(f"  to_ssmd():  {sent.to_ssmd()}")

        # SSML with sentence tags
        print(f"  to_ssml(wrap_sentence=True): {sent.to_ssml(wrap_sentence=True)}")
        print()


def mock_tts_integration():
    """Mock TTS integration - Shows how to use parser with a TTS engine."""
    print("\n" + "=" * 60)
    print("Mock TTS Integration Example")
    print("=" * 60)

    script = """
@voice: sarah, language: en-US
Hello! Today's date is [2024-01-15](as: date, format: mdy).
Call [+1-555-0123](as: telephone) for support.

@voice: michael, language: en-GB
*Thank you* for watching!
"""

    sentences = parse_sentences(script)

    print("\nProcessing script for TTS engine:\n")

    # Process each sentence as you would in a real TTS system
    for sentence in sentences:
        # Configure voice
        voice_config = {}
        if sentence.voice:
            if sentence.voice.name:
                voice_config["name"] = sentence.voice.name
            if sentence.voice.language:
                voice_config["language"] = sentence.voice.language
            if sentence.voice.gender:
                voice_config["gender"] = sentence.voice.gender

        print(f"Voice config: {voice_config}")

        # Build audio for each segment
        audio_parts = []

        for seg in sentence.segments:
            # Determine text to speak
            if seg.say_as:
                # TTS engine converts based on interpret_as
                text = f"<say-as {seg.say_as.interpret_as}>{seg.text}</say-as>"
                print(f"  -> Say-as segment: {text}")
            elif seg.substitution:
                # Speak substitution instead of original text
                text = seg.substitution
                print(f"  -> Substitution: '{seg.text}' -> '{text}'")
            elif seg.phoneme:
                # Use phoneme for pronunciation
                text = f"<phoneme>{seg.text}</phoneme>"
                print(f"  -> Phoneme segment: {text} ({seg.phoneme.ph})")
            else:
                text = seg.text
                print(f"  -> Plain text: {text!r}")

            # Apply prosody if present
            if seg.prosody:
                prosody_info = []
                if seg.prosody.volume:
                    prosody_info.append(f"volume={seg.prosody.volume}")
                if seg.prosody.rate:
                    prosody_info.append(f"rate={seg.prosody.rate}")
                if seg.prosody.pitch:
                    prosody_info.append(f"pitch={seg.prosody.pitch}")
                print(f"     Prosody: {', '.join(prosody_info)}")

            # Apply emphasis if present
            if seg.emphasis:
                print("     Emphasis: True")

            # Mock: Generate audio
            audio_parts.append(f"[audio:{text}]")

            # Handle breaks
            for brk in seg.breaks_after:
                audio_parts.append(f"[silence:{brk.time}]")
                print(f"     Break: {brk.time}")

        # Mock: Combine audio parts
        print(f"  Final audio: {' '.join(audio_parts)}")
        print()


if __name__ == "__main__":
    example_1_basic_parsing()
    example_2_text_transformations()
    example_3_voice_blocks()
    example_4_complete_workflow()
    example_5_prosody_and_language()
    example_6_advanced_sentence_parsing()
    example_7_capabilities_filtering()
    example_8_multilingual()
    example_9_sentence_attributes()
    example_10_output_formats()
    mock_tts_integration()

    print("\n" + "=" * 60)
    print("Parser Demo Complete!")
    print("=" * 60)
    print("\nKey takeaways:")
    print("1. parse_segments() - Extract segments from text")
    print("2. parse_voice_blocks() - Split by voice directives")
    print("3. parse_sentences() - Complete workflow with sentences")
    print("4. Each segment has metadata (emphasis, prosody, breaks, etc.)")
    print("5. Build sentences by processing segments individually")
    print("6. Use capabilities to filter for specific TTS engines")
    print("7. Support multiple languages with the language parameter")
    print("8. Output as plain text, SSML, or SSMD")
    print("\nUse the parser when you need programmatic control over")
    print("SSMD features instead of generating SSML directly.")
