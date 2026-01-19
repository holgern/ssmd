"""Google TTS Style Extensions Demo.

This example demonstrates how to use Google Cloud TTS speaking styles
with SSMD extension syntax.

Google Cloud TTS supports various speaking styles for WaveNet voices:
- default: Standard speaking style
- calm: Calm and soothing tone
- cheerful: Upbeat and positive tone
- empathetic: Empathetic and understanding tone
- firm: Confident and assertive tone
- lively: Energetic and animated tone
- serious: Professional and serious tone
- unfriendly: Cold and distant tone (use sparingly!)

Note: Style support varies by voice. Not all voices support all styles.
See: https://cloud.google.com/text-to-speech/docs/voices
"""

import ssmd


def google_style_extension(style: str):
    """Create a Google TTS style extension handler.

    Args:
        style: The style name (e.g., 'cheerful', 'calm', 'empathetic')

    Returns:
        Lambda function that wraps text in google:style tags
    """
    return lambda text: f'<google:style name="{style}">{text}</google:style>'


def main():
    """Demonstrate Google TTS styles using SSMD extension syntax."""

    # Configure document with Google style extensions
    doc = ssmd.Document(
        config={
            "extensions": {
                # Register common Google TTS styles
                "cheerful": google_style_extension("cheerful"),
                "calm": google_style_extension("calm"),
                "empathetic": google_style_extension("empathetic"),
                "firm": google_style_extension("firm"),
                "lively": google_style_extension("lively"),
                "serious": google_style_extension("serious"),
            }
        }
    )

    # Build a demo script with various styles
    doc.add_paragraph("# Customer Service Demo")
    doc.add_sentence('[Welcome to our support line!]{ext="cheerful"}')
    doc.add_sentence('[I understand this must be frustrating.]{ext="empathetic"}')
    doc.add_sentence('[Let me help you resolve this issue.]{ext="calm"}')

    doc.add_paragraph("# News Broadcast Demo")
    doc.add_sentence('[Good evening, I\'m your news anchor.]{ext="serious"}')
    doc.add_sentence('[Today\'s top story is truly *extraordinary*!]{ext="lively"}')

    doc.add_paragraph("# Leadership Speech Demo")
    doc.add_sentence('[We need to take action *now*.]{ext="firm"}')
    doc.add_sentence('[Together, we can make a difference!]{ext="cheerful"}')

    # Export to SSML
    ssml = doc.to_ssml()
    print("=" * 60)
    print("SSMD Document:")
    print("=" * 60)
    print(doc.ssmd)
    print()

    print("=" * 60)
    print("Generated SSML with Google Styles:")
    print("=" * 60)
    print(ssml)
    print()

    # You can also use inline SSMD syntax
    print("=" * 60)
    print("Inline Style Examples:")
    print("=" * 60)

    examples = [
        '[Hello there!]{ext="cheerful"}',
        '[Please remain calm.]{ext="calm"}',
        '[I\'m here to help.]{ext="empathetic"}',
        '[Listen carefully.]{ext="firm"}',
        '[This is amazing!]{ext="lively"}',
        '[Breaking news.]{ext="serious"}',
    ]

    for example in examples:
        result = ssmd.to_ssml(
            example,
            extensions={
                "cheerful": google_style_extension("cheerful"),
                "calm": google_style_extension("calm"),
                "empathetic": google_style_extension("empathetic"),
                "firm": google_style_extension("firm"),
                "lively": google_style_extension("lively"),
                "serious": google_style_extension("serious"),
            },
        )
        print(f"SSMD: {example}")
        print(f"SSML: {result}")
        print()

    print("=" * 60)
    print("Integration with Voice Selection:")
    print("=" * 60)

    # Combine Google styles with voice selection
    multi_voice = ssmd.Document(
        config={
            "extensions": {
                "cheerful": google_style_extension("cheerful"),
                "empathetic": google_style_extension("empathetic"),
            }
        }
    )

    multi_voice.add_paragraph(
        """
<div voice="en-US-Wavenet-F">
[Hello! How can I help you today?]{ext="cheerful"}
</div>

<div voice="en-US-Wavenet-C">
I'm having trouble with my order.
</div>

<div voice="en-US-Wavenet-F">
[I completely understand your concern.]{ext="empathetic"}
Let me look into that for you right away.
</div>
    """
    )

    print(multi_voice.to_ssml())

    print()
    print("=" * 60)
    print("Usage Notes:")
    print("=" * 60)
    print("""
1. Register your Google styles in the Document config
2. Use [text]{ext="style_name"} syntax in your SSMD
3. Combine with other SSMD features (voice, prosody, etc.)
4. Check Google Cloud TTS docs for voice-specific style support
5. Test with Google Cloud TTS API to hear the actual styles

Example API usage (requires google-cloud-texttospeech):
    from google.cloud import texttospeech

    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Wavenet-F"
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)
""")


if __name__ == "__main__":
    main()
