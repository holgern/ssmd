TTS Engine Capabilities
=======================

SSMD can automatically filter SSML features based on your TTS engine's capabilities.
This ensures compatibility by converting unsupported features to plain text.

Why Capabilities Matter
-----------------------

Different TTS engines support different SSML features:

* **Basic engines** (pyttsx3, eSpeak) support limited SSML
* **Cloud services** (Google, Azure, Amazon Polly) support full SSML
* **Custom engines** may have unique limitations

Without capability filtering, unsupported SSML tags could:

* Be ignored silently
* Cause errors
* Be spoken as literal text
* Break TTS playback

SSMD solves this by automatically stripping unsupported features.

Using Capability Presets
-------------------------

The easiest way is to use a built-in preset:

.. code-block:: python

   from ssmd import SSMD

   # Configure for your TTS engine
   parser = SSMD(capabilities='espeak')

   # Unsupported features are automatically removed
   ssml = parser.to_ssml("*Hello* [world](fr)!")
   # eSpeak doesn't support emphasis or language
   # Output: <speak>Hello world!</speak>

Available Presets
~~~~~~~~~~~~~~~~~

minimal
^^^^^^^

Plain text only, no SSML features:

.. code-block:: python

   parser = SSMD(capabilities='minimal')

**Supported:** None (all stripped to text)

pyttsx3
^^^^^^^

For the pyttsx3 library (offline TTS):

.. code-block:: python

   parser = SSMD(capabilities='pyttsx3')

**Supported:**

* Prosody (volume, rate, pitch) - limited
* Paragraphs

**Not supported:**

* Emphasis
* Breaks
* Language switching
* Phonemes
* Say-as
* Audio
* Marks

espeak
^^^^^^

For eSpeak/eSpeak-NG:

.. code-block:: python

   parser = SSMD(capabilities='espeak')

**Supported:**

* Breaks (pauses)
* Language switching
* Prosody (volume, rate, pitch)
* Phonemes (IPA and X-SAMPA)
* Paragraphs

**Not supported:**

* Emphasis
* Say-as
* Audio files
* Marks
* Substitution

google / azure / microsoft
^^^^^^^^^^^^^^^^^^^^^^^^^^^

For cloud TTS services with full SSML support:

.. code-block:: python

   parser = SSMD(capabilities='google')
   # or
   parser = SSMD(capabilities='azure')

**Supported:** All standard SSML features

* Emphasis
* Breaks
* Language switching
* Prosody
* Phonemes
* Say-as
* Paragraphs
* Marks
* Substitution

**Not supported:**

* Audio files (varies by service)
* Platform-specific extensions

polly / amazon
^^^^^^^^^^^^^^

For Amazon Polly with extensions:

.. code-block:: python

   parser = SSMD(capabilities='polly')

**Supported:** All features including:

* All standard SSML
* Amazon extensions (whisper, DRC)
* Audio files

full
^^^^

All features enabled (no filtering):

.. code-block:: python

   parser = SSMD(capabilities='full')

Use this when you know your engine supports everything or want to test.

Custom Capabilities
-------------------

Define exactly what your TTS engine supports:

Basic Example
~~~~~~~~~~~~~

.. code-block:: python

   from ssmd import SSMD, TTSCapabilities

   # Create custom capability profile
   caps = TTSCapabilities(
       emphasis=False,      # No <emphasis> support
       break_tags=True,     # Supports <break>
       paragraph=True,      # Supports <p>
       language=False,      # No language switching
       prosody=True,        # Supports volume/rate/pitch
       say_as=False,        # No <say-as>
       audio=False,         # No audio files
       mark=False,          # No markers
       phoneme=False,       # No phonetic notation
       substitution=False,  # No substitution
   )

   parser = SSMD(capabilities=caps)

Partial Prosody Support
~~~~~~~~~~~~~~~~~~~~~~~~

Some engines support only certain prosody attributes:

.. code-block:: python

   from ssmd import TTSCapabilities, ProsodySupport

   caps = TTSCapabilities(
       prosody=ProsodySupport(
           volume=True,     # Supports volume
           rate=True,       # Supports rate
           pitch=False,     # Does NOT support pitch
       )
   )

   parser = SSMD(capabilities=caps)

   # Pitch will be stripped, but volume and rate preserved
   ssml = parser.to_ssml('[text](v: 5, r: 4, p: 5)')
   # → <prosody volume="x-loud" rate="fast">text</prosody>

Extension Support
~~~~~~~~~~~~~~~~~

Control platform-specific extensions:

.. code-block:: python

   caps = TTSCapabilities(
       extensions={
           'whisper': True,   # Amazon whisper effect
           'drc': False,      # Dynamic range compression
       }
   )

   parser = SSMD(capabilities=caps)

   ssml = parser.to_ssml('[secret](ext: whisper)')
   # → <amazon:effect name="whispered">secret</amazon:effect>

Capability Comparison
---------------------

Same input with different engines:

Input
~~~~~

.. code-block:: python

   text = "*Hello* world... [this is loud](v: 5)!"

Output by Engine
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Engine
     - Output SSML
   * - minimal
     - ``<speak>Hello world... this is loud!</speak>``
   * - pyttsx3
     - ``<speak>Hello world... <prosody volume="x-loud">this is loud</prosody>!</speak>``
   * - espeak
     - ``<speak>Hello world<break time="1000ms"/> <prosody volume="x-loud">this is loud</prosody>!</speak>``
   * - google
     - ``<speak><emphasis>Hello</emphasis> world<break time="1000ms"/> <prosody volume="x-loud">this is loud</prosody>!</speak>``

Streaming with Capabilities
----------------------------

Capability filtering works seamlessly with document streaming:

.. code-block:: python

   from ssmd import SSMD

   # Create parser for specific engine
   parser = SSMD(capabilities='espeak')

   # Load document
   doc = parser.load("""
   # Welcome
   *Hello* world!
   [Bonjour](fr) everyone!
   This is +loud+.
   """)

   # All sentences are pre-filtered for eSpeak
   for sentence in doc:
       tts_engine.speak(sentence)
       # Emphasis and language are already removed
       # Prosody is preserved

Testing Capabilities
--------------------

Test what gets filtered:

.. code-block:: python

   from ssmd import SSMD

   engines = ['minimal', 'pyttsx3', 'espeak', 'google', 'polly']
   text = "*Emphasis* ...500ms [language](fr) +loud+"

   for engine in engines:
       parser = SSMD(capabilities=engine)
       ssml = parser.to_ssml(text)
       print(f"{engine:10} → {ssml}")

Output:

.. code-block:: text

   minimal    → <speak>Emphasis language loud</speak>
   pyttsx3    → <speak>Emphasis language <prosody volume="loud">loud</prosody></speak>
   espeak     → <speak>Emphasis <break time="500ms"/> <lang xml:lang="fr-FR">language</lang> <prosody volume="loud">loud</prosody></speak>
   google     → <speak><emphasis>Emphasis</emphasis> <break time="500ms"/> <lang xml:lang="fr-FR">language</lang> <prosody volume="loud">loud</prosody></speak>
   polly      → <speak><emphasis>Emphasis</emphasis> <break time="500ms"/> <lang xml:lang="fr-FR">language</lang> <prosody volume="loud">loud</prosody></speak>

Fallback Behavior
-----------------

When a feature is unsupported:

1. **Text content is preserved** - Never lost
2. **Markup is stripped** - Clean removal
3. **Whitespace is normalized** - No extra spaces
4. **Nesting is handled** - Inner content preserved

Example:

.. code-block:: python

   # With emphasis support disabled
   parser = SSMD(capabilities='minimal')

   # Emphasis markup is removed, text preserved
   ssml = parser.to_ssml("This is *very important* info")
   # → <speak>This is very important info</speak>

Best Practices
--------------

1. **Match your engine**: Use the appropriate preset or create custom capabilities
2. **Test with your engine**: Verify output works as expected
3. **Graceful degradation**: Write content that works even when features are stripped
4. **Document requirements**: Note which TTS engines your content supports
5. **Use capability detection**: Check engine capabilities at runtime if possible

Example:

.. code-block:: python

   # Good: Works with any engine
   text = "Hello world! This is important."

   # Better: Adds features for engines that support them
   text = "Hello world! *This is important*."

   # Best: Provides alternatives
   text = """
   Hello world!
   *This is important.*
   [This is very important.](v: 5, r: 2)
   """

Integration Example
-------------------

Complete example with capability detection:

.. code-block:: python

   from ssmd import SSMD

   class TTSHandler:
       def __init__(self, engine_name):
           self.engine_name = engine_name
           self.parser = SSMD(capabilities=engine_name)

       def speak(self, ssmd_text):
           # Convert with automatic filtering
           ssml = self.parser.to_ssml(ssmd_text)

           # Send to TTS engine
           self.engine.speak(ssml)

   # Usage
   tts = TTSHandler('espeak')
   tts.speak("*Hello* [world](fr)!")
   # Automatically filtered for eSpeak compatibility
