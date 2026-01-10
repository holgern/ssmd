"""Example: Using SSMD with TTS engine capabilities.

This example demonstrates how SSMD automatically filters features
based on your TTS engine's capabilities, ensuring compatibility.
"""

from ssmd import Document, TTSCapabilities


def demonstrate_capability_filtering() -> None:
    """Show how different TTS engines handle the same content."""

    # Sample SSMD content with various features
    content = """
    # Welcome
    Hello and *welcome* to SSMD!

    This is ++very exciting++ content.

    Let's pause here ...500ms for effect.

    [Bonjour](fr) everyone!

    The number is [123](as: cardinal).

    [Whispered text](ext: whisper) for Amazon Polly.
    """

    print("=" * 80)
    print("SSMD TTS Capabilities Demo")
    print("=" * 80)
    print("\nSame SSMD content processed for different TTS engines:\n")

    # Show original SSMD
    print("📝 Original SSMD content:")
    print("-" * 80)
    print(content.strip())
    print("-" * 80)

    # Engine 1: Minimal (plain text only)
    print("\n\n1️⃣  MINIMAL ENGINE (no SSML support)")
    print("-" * 80)
    doc = Document(content, capabilities="minimal")
    ssml = doc.to_ssml()
    print(f"Output: {ssml[:200]}...")
    print("\nNOTE: All markup stripped to plain text")

    # Engine 2: pyttsx3 (very limited)
    print("\n\n2️⃣  PYTTSX3 (minimal SSML support)")
    print("-" * 80)
    doc = Document(content, capabilities="pyttsx3")
    ssml = doc.to_ssml()
    print(f"Output: {ssml[:300]}...")
    print("\nNOTE: Only basic prosody supported, most features stripped")

    # Engine 3: eSpeak (moderate support)
    print("\n\n3️⃣  ESPEAK (moderate SSML support)")
    print("-" * 80)
    doc = Document(content, capabilities="espeak")
    ssml = doc.to_ssml()
    print(f"Output: {ssml[:400]}...")
    print("\nNOTE: Supports breaks, language, prosody, phonemes")

    # Engine 4: Google TTS (full support)
    print("\n\n4️⃣  GOOGLE TTS (full SSML support)")
    print("-" * 80)
    doc = Document(content, capabilities="google")
    ssml = doc.to_ssml()
    print(f"Output: {ssml[:500]}...")
    print("\nNOTE: All standard SSML features supported")

    # Engine 5: Amazon Polly (full + extensions)
    print("\n\n5️⃣  AMAZON POLLY (full + extensions)")
    print("-" * 80)
    doc = Document(content, capabilities="polly")
    ssml = doc.to_ssml()
    print(f"Output: {ssml[:500]}...")
    print("\nNOTE: All features + Amazon-specific extensions (whisper, DRC)")

    print("\n" + "=" * 80)


def demonstrate_custom_capabilities() -> None:
    """Show how to define custom TTS capabilities."""

    print("\n\n" + "=" * 80)
    print("Custom TTS Capabilities Demo")
    print("=" * 80)

    # Define a custom TTS with specific limitations
    custom_caps = TTSCapabilities(
        emphasis=True,  # Supports <emphasis>
        break_tags=True,  # Supports <break>
        paragraph=True,  # Supports <p>
        language=True,  # Supports <lang>
        prosody=False,  # NO prosody support
        say_as=False,  # NO say-as support
        audio=False,  # NO audio files
        mark=True,  # Supports <mark>
        phoneme=False,  # NO phoneme support
    )

    content = """
    Hello *world*!
    Pause here ...500ms please.
    Say [bonjour](fr) to everyone.
    This is ++very loud++ text.
    The number is [123](as: cardinal).
    Place a @marker here.
    """

    print("\n📝 SSMD content:")
    print("-" * 80)
    print(content.strip())
    print("-" * 80)

    print("\n\n🎛️  Custom TTS Engine Output:")
    print("    Supports: emphasis, breaks, language, marks")
    print("    Does NOT support: prosody, say-as, phonemes")
    print("-" * 80)

    doc = Document(content, capabilities=custom_caps)
    ssml = doc.to_ssml()

    print(ssml)
    print("-" * 80)

    print("\n✅ Result:")
    print("   - <emphasis> tags: KEPT")
    print("   - <break> tags: KEPT")
    print("   - <lang> tags: KEPT")
    print("   - <mark> tags: KEPT")
    print("   - <prosody> tags: STRIPPED (not supported)")
    print("   - <say-as> tags: STRIPPED (not supported)")

    print("\n" + "=" * 80)


def demonstrate_capability_aware_streaming() -> None:
    """Show streaming TTS with capability filtering."""

    print("\n\n" + "=" * 80)
    print("Capability-Aware Streaming Demo")
    print("=" * 80)

    # Build a document for eSpeak
    doc = Document(capabilities="espeak", config={"auto_sentence_tags": True})

    doc.add_paragraph("# Story Time")
    doc.add_sentence("Once upon a time, there was a *brave* knight.")
    doc.add_sentence("He traveled ...300ms across distant lands.")
    doc.add_sentence("[Bonjour](fr) said the French wizard.")
    doc.add_sentence("This story is ++very exciting++!")

    print(f"\n📖 Streaming {len(doc)} sentences to eSpeak TTS engine...")
    print("    (emphasis and extensions are auto-stripped)")
    print("-" * 80)

    for i in range(len(doc)):
        sentence_ssml = doc[i]
        print(f"\n[{i + 1}/{len(doc)}] {sentence_ssml[:70]}...")
        # In real code: tts_engine.speak(sentence)

    print("\n" + "=" * 80)


if __name__ == "__main__":
    demonstrate_capability_filtering()
    demonstrate_custom_capabilities()
    demonstrate_capability_aware_streaming()

    print("\n\n🎉 All demos complete!")
    print("\nSee ssmd/capabilities.py for available presets:")
    print("   - minimal, pyttsx3, espeak, google, azure, polly, full")
