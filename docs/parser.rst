Parser API
==========

The SSMD Parser provides an alternative to SSML generation by extracting structured
data from SSMD text. This is useful when you need programmatic control over SSMD
features or want to build custom TTS pipelines.

When to Use the Parser
----------------------

Use the parser API when you need to:

* **Process SSMD features programmatically** - Extract and handle features individually
* **Build custom TTS pipelines** - Implement your own text-to-speech workflow
* **Handle text transformations** - Process say-as, substitution, and phoneme conversions
* **Create multi-voice dialogue systems** - Build voice-specific processing pipelines
* **Analyze SSMD content** - Extract metadata and features without generating SSML

Overview
--------

The parser extracts SSMD markup into structured segments, allowing you to process
each feature individually instead of generating a complete SSML document.

.. code-block:: python

   from ssmd import parse_sentences

   script = """
   @voice: sarah
   Hello! Call [+1-555-0123](as: telephone) for info.

   @voice: michael
   Thanks *Sarah*!
   """

   # Parse into structured sentences
   for sentence in parse_sentences(script):
       # Get voice configuration
       voice_name = sentence.voice.name if sentence.voice else "default"

       # Build complete text from segments
       full_text = ""
       for seg in sentence.segments:
           # Handle text transformations
           if seg.say_as:
               text = convert_say_as(seg.text, seg.say_as.interpret_as)
           elif seg.substitution:
               text = seg.substitution
           elif seg.phoneme:
               text = seg.text  # TTS engine handles phoneme
           else:
               text = seg.text
           full_text += text

       # Speak with TTS engine
       tts.speak(full_text, voice=voice_name)

Parser Functions
----------------

parse_sentences
~~~~~~~~~~~~~~~

Parse SSMD text into structured sentences with segments.

.. autofunction:: ssmd.parse_sentences

**Parameters:**

* ``ssmd_text`` (str): SSMD markdown text to parse
* ``sentence_detection`` (bool): Split text into sentences (default: ``True``)
* ``include_default_voice`` (bool): Include text before first ``@voice:`` directive (default: ``True``)
* ``capabilities`` (TTSCapabilities | str): Filter features based on TTS engine support
* ``language`` (str): Language code for sentence detection (default: ``"en"``)
* ``model_size`` (str): spaCy model size - ``"sm"``, ``"md"``, ``"lg"``, ``"trf"`` (default: ``"sm"``)
* ``spacy_model`` (str): Custom spaCy model name (overrides ``model_size``)
* ``use_spacy`` (bool): If ``False``, use fast regex splitting instead of spaCy (default: ``True``)

**Returns:** List of :class:`SSMDSentence` objects

**Example:**

.. code-block:: python

   from ssmd import parse_sentences

   sentences = parse_sentences("Hello *world*! This is great.")

   for sent in sentences:
       print(f"Voice: {sent.voice.name if sent.voice else 'default'}")
       print(f"Segments: {len(sent.segments)}")
       for seg in sent.segments:
           print(f"  - {seg.text!r} (emphasis={seg.emphasis})")

Sentence Detection Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Control how sentences are detected and split. SSMD uses **phrasplit** for intelligent
sentence detection with optional spaCy support for maximum accuracy.

**Fast Mode (Regex-Based, No spaCy Required)**

The default mode uses fast regex-based splitting that works great for well-formatted text:

.. code-block:: python

   from ssmd import parse_sentences

   # Fast regex splitting (works out-of-the-box, no spaCy needed)
   sentences = parse_sentences(
       "Hello world. This is fast.",
       use_spacy=False
   )

**Auto-Detection (Recommended)**

By default, SSMD auto-detects if spaCy is installed and uses it for better accuracy:

.. code-block:: python

   # Auto-detect: uses spaCy if installed, falls back to regex
   sentences = parse_sentences("Hello. World.")
   # Works without spaCy, better accuracy with spaCy

**Model Size Selection**

When spaCy is installed, choose different model sizes for quality vs. speed tradeoffs:

.. code-block:: python

   # Small model (fast, good accuracy) - DEFAULT
   sentences = parse_sentences("Hello. World.")
   # Uses: en_core_web_sm, fr_core_news_sm, etc.

   # Medium model (better accuracy)
   sentences = parse_sentences("Hello. World.", model_size="md")
   # Uses: en_core_web_md, fr_core_news_md, etc.

   # Large model (best accuracy)
   sentences = parse_sentences("Hello. World.", model_size="lg")
   # Uses: en_core_web_lg, fr_core_news_lg, etc.

   # Transformer model (research-grade quality, slowest)
   sentences = parse_sentences("Hello. World.", model_size="trf")
   # Uses: en_core_web_trf, fr_dep_news_trf, etc.

**Custom Models**

Use domain-specific or custom spaCy models:

.. code-block:: python

   # Use a custom spaCy model
   sentences = parse_sentences(
       "Technical text here.",
       spacy_model="en_core_sci_md"  # Scientific/medical domain model
   )

**Multi-Language Support**

The ``model_size`` parameter works across all spaCy-supported languages:

.. code-block:: python

   script = """
   @voice: fr-FR
   Bonjour tout le monde!

   @voice: en-US
   Hello everyone!
   """

   # Uses fr_core_news_md for French, en_core_web_md for English
   sentences = parse_sentences(script, model_size="md")

**Installation**

SSMD works out-of-the-box with fast regex mode. For spaCy support:

.. code-block:: bash

   # Install spaCy support
   pip install "ssmd[spacy]"

   # Install models for your languages
   python -m spacy download en_core_web_sm  # English (small)
   python -m spacy download en_core_web_md  # English (medium)
   python -m spacy download en_core_web_lg  # English (large)
   python -m spacy download fr_core_news_sm  # French

See the `spaCy models documentation <https://spacy.io/models>`_ for a complete list of available models.

**Performance Comparison**

=========== =========== ======== ======== =============================
Mode        Speed       Accuracy Size     Use Case
=========== =========== ======== ======== =============================
Regex       60x faster  85-90%   0 MB     Simple text, speed-critical
spaCy sm    Baseline    ~95%     ~30 MB   Balanced accuracy/performance
spaCy md    Slower      ~97%     ~100 MB  Better accuracy
spaCy lg    2x slower   ~98%     ~500 MB  Best accuracy
spaCy trf   10x slower  ~99%+    ~1 GB    Research, maximum quality
=========== =========== ======== ======== =============================

parse_segments
~~~~~~~~~~~~~~

Parse SSMD text into segments without sentence grouping.

.. autofunction:: ssmd.parse_segments

**Parameters:**

* ``text`` (str): SSMD text to parse
* ``capabilities`` (TTSCapabilities | str): Filter features based on TTS engine support
* ``voice_context`` (VoiceAttrs | None): Current voice context

**Returns:** List of :class:`SSMDSegment` objects

**Example:**

.. code-block:: python

   from ssmd import parse_segments

   segments = parse_segments("Call [+1-555-0123](as: telephone) now")

   for seg in segments:
       if seg.say_as:
           print(f"Say-as: {seg.text!r} as {seg.say_as.interpret_as}")

parse_voice_blocks
~~~~~~~~~~~~~~~~~~

Split text by voice directives.

.. autofunction:: ssmd.parse_voice_blocks

**Returns:** List of ``(VoiceAttrs | None, str)`` tuples

**Example:**

.. code-block:: python

   from ssmd import parse_voice_blocks

   blocks = parse_voice_blocks("""
   @voice: sarah
   Hello from Sarah

   @voice: michael
   Hello from Michael
   """)

   for voice, text in blocks:
       print(f"{voice.name}: {text.strip()}")

Data Structures
---------------

SSMDSentence
~~~~~~~~~~~~

Represents a complete sentence with voice context and segments.

.. autoclass:: ssmd.SSMDSentence
   :members:
   :undoc-members:

**Attributes:**

* ``segments`` (list[SSMDSegment]): List of text segments making up the sentence
* ``voice`` (VoiceAttrs | None): Voice configuration for this sentence
* ``is_paragraph_end`` (bool): Whether this sentence ends a paragraph
* ``breaks_after`` (list[BreakAttrs]): Breaks after the sentence
* ``position`` (int): Position in original text

SSMDSegment
~~~~~~~~~~~

Represents a text segment with associated metadata and features.

.. autoclass:: ssmd.SSMDSegment
   :members:
   :undoc-members:

**Attributes:**

* ``text`` (str): The text content of this segment
* ``emphasis`` (bool): Whether this segment has emphasis
* ``prosody`` (ProsodyAttrs | None): Prosody attributes (volume, rate, pitch)
* ``language`` (str | None): Language code (e.g., ``"fr-FR"``)
* ``breaks_after`` (list[BreakAttrs]): Pauses after this segment
* ``breaks_before`` (list[BreakAttrs]): Pauses before this segment
* ``say_as`` (SayAsAttrs | None): Say-as interpretation
* ``substitution`` (str | None): Substitution text
* ``phoneme`` (str | None): Phonetic pronunciation (IPA)
* ``audio`` (AudioAttrs | None): Audio file information
* ``extension`` (tuple[str, str] | None): Extension name and text
* ``marks_before`` (list[str]): Marker names before this segment
* ``marks_after`` (list[str]): Marker names after this segment
* ``position`` (int): Position in original text

VoiceAttrs
~~~~~~~~~~

Voice configuration attributes.

.. autoclass:: ssmd.VoiceAttrs
   :members:
   :undoc-members:

**Attributes:**

* ``name`` (str | None): Voice name (e.g., ``"sarah"``, ``"en-US-Wavenet-A"``)
* ``language`` (str | None): Language code (e.g., ``"en-US"``)
* ``gender`` (str | None): Gender (``"male"``, ``"female"``, ``"neutral"``)
* ``variant`` (int | None): Voice variant number

ProsodyAttrs
~~~~~~~~~~~~

Prosody attributes for controlling volume, rate, and pitch.

.. autoclass:: ssmd.ProsodyAttrs
   :members:
   :undoc-members:

**Attributes:**

* ``volume`` (str | None): Volume level (e.g., ``"x-loud"``, ``"+10dB"``)
* ``rate`` (str | None): Speech rate (e.g., ``"fast"``, ``"120%"``)
* ``pitch`` (str | None): Pitch level (e.g., ``"high"``, ``"+20%"``)

BreakAttrs
~~~~~~~~~~

Pause/break attributes.

.. autoclass:: ssmd.BreakAttrs
   :members:
   :undoc-members:

**Attributes:**

* ``time`` (str | None): Break duration (e.g., ``"500ms"``, ``"2s"``)
* ``strength`` (str | None): Break strength (e.g., ``"weak"``, ``"strong"``)

SayAsAttrs
~~~~~~~~~~

Say-as interpretation attributes.

.. autoclass:: ssmd.SayAsAttrs
   :members:
   :undoc-members:

**Attributes:**

* ``interpret_as`` (str): Interpretation type (e.g., ``"telephone"``, ``"date"``)
* ``format`` (str | None): Format string (e.g., ``"mdy"`` for dates)

AudioAttrs
~~~~~~~~~~

Audio file attributes.

.. autoclass:: ssmd.AudioAttrs
   :members:
   :undoc-members:

**Attributes:**

* ``src`` (str): Audio file URL
* ``alt_text`` (str | None): Alternative text if audio fails to load

Usage Examples
--------------

Basic Parsing
~~~~~~~~~~~~~

Extract segments from simple text:

.. code-block:: python

   from ssmd import parse_segments

   text = "Hello *world*! This is ...500ms great."
   segments = parse_segments(text)

   for seg in segments:
       print(f"Text: {seg.text!r}")
       if seg.emphasis:
           print("  Has emphasis")
       for brk in seg.breaks_after:
           print(f"  Break: {brk.time}")

Text Transformations
~~~~~~~~~~~~~~~~~~~~

Handle say-as, substitution, and phoneme features:

.. code-block:: python

   from ssmd import parse_segments

   text = """
   Call [+1-555-0123](as: telephone) for info.
   [H2O](sub: water) is important.
   Say [tomato](ph: təˈmeɪtoʊ) correctly.
   """

   segments = parse_segments(text)

   for seg in segments:
       if seg.say_as:
           print(f"Say-as: {seg.text!r} as {seg.say_as.interpret_as}")
       elif seg.substitution:
           print(f"Substitute: {seg.text!r} → {seg.substitution!r}")
       elif seg.phoneme:
           print(f"Phoneme: {seg.text!r} → {seg.phoneme!r}")

Multi-Voice Dialogue
~~~~~~~~~~~~~~~~~~~~

Process voice blocks separately:

.. code-block:: python

   from ssmd import parse_voice_blocks

   script = """
   @voice: sarah
   Welcome to the show!

   @voice: michael
   Thanks Sarah! Great to be here.
   """

   blocks = parse_voice_blocks(script)

   for voice, text in blocks:
       if voice:
           print(f"{voice.name}: {text.strip()}")

Complete TTS Workflow
~~~~~~~~~~~~~~~~~~~~~

Build sentences from segments for TTS processing:

.. code-block:: python

   from ssmd import parse_sentences

   script = """
   @voice: sarah
   Hello! Call [+1-555-0123](as: telephone) for info.

   @voice: michael
   Thanks *Sarah*!
   """

   for sentence in parse_sentences(script):
       # Get voice
       voice_name = sentence.voice.name if sentence.voice else "default"

       # Build complete text
       full_text = ""
       metadata = []

       for seg in sentence.segments:
           # Handle transformations
           if seg.say_as:
               text = convert_say_as(seg.text, seg.say_as.interpret_as)
               metadata.append(f"say-as:{seg.say_as.interpret_as}")
           elif seg.substitution:
               text = seg.substitution
           elif seg.phoneme:
               text = seg.text
               metadata.append(f"phoneme:{seg.phoneme}")
           else:
               text = seg.text

           full_text += text

           # Track emphasis
           if seg.emphasis:
               metadata.append("emphasis")

           # Track breaks
           for brk in seg.breaks_after:
               metadata.append(f"break:{brk.time}")

       # Speak with TTS engine
       print(f"[{voice_name}] {full_text}")
       if metadata:
           print(f"  Metadata: {', '.join(metadata)}")

Advanced Sentence Parsing
~~~~~~~~~~~~~~~~~~~~~~~~~~

Control sentence detection and voice filtering:

.. code-block:: python

   from ssmd import parse_sentences

   text = """
   Welcome to the demo.

   This is a new paragraph.

   @voice: sarah
   Sarah speaks here.
   """

   sentences = parse_sentences(
       text,
       sentence_detection=True,       # Split by sentences
       include_default_voice=True,    # Include text before @voice
   )

   for i, sent in enumerate(sentences, 1):
       voice_name = sent.voice.name if sent.voice else "(default)"
       text_content = "".join(seg.text for seg in sent.segments)
       para_marker = " [PARA_END]" if sent.is_paragraph_end else ""

       print(f"{i}. [{voice_name}] {text_content!r}{para_marker}")

TTS Engine Integration
~~~~~~~~~~~~~~~~~~~~~~

Example integration with a TTS engine:

.. code-block:: python

   from ssmd import parse_sentences

   class TTSEngine:
       def speak(self, text: str, voice: str = "default", **kwargs):
           """Speak text with given voice and parameters."""
           print(f"[TTS] Voice: {voice}, Text: {text}")
           # Your TTS implementation here
           pass

   def process_ssmd_script(script: str, tts: TTSEngine):
       """Process SSMD script with TTS engine."""
       sentences = parse_sentences(script)

       for sentence in sentences:
           # Configure voice
           voice_config = {}
           if sentence.voice:
               if sentence.voice.name:
                   voice_config["voice"] = sentence.voice.name
               if sentence.voice.language:
                   voice_config["language"] = sentence.voice.language

           # Build text with transformations
           full_text = ""
           for seg in sentence.segments:
               if seg.say_as:
                   # TTS engine handles say-as conversion
                   text = handle_say_as(seg.text, seg.say_as)
               elif seg.substitution:
                   text = seg.substitution
               elif seg.phoneme:
                   text = seg.text  # Use phoneme for pronunciation
               else:
                   text = seg.text

               full_text += text

           # Speak with TTS
           tts.speak(full_text, **voice_config)

   # Usage
   script = """
   @voice: sarah
   Hello! Today's date is [2024-01-15](as: date, format: mdy).

   @voice: michael
   Thank you for listening!
   """

   tts = TTSEngine()
   process_ssmd_script(script, tts)

Capability Filtering
~~~~~~~~~~~~~~~~~~~~

Filter features based on TTS engine capabilities:

.. code-block:: python

   from ssmd import parse_sentences

   # Parse with pyttsx3 capabilities (limited SSML support)
   sentences = parse_sentences(
       "Hello *world*! [Bonjour](fr) everyone!",
       capabilities='pyttsx3'
   )

   # Unsupported features (emphasis, language) are filtered out
   for sent in sentences:
       for seg in sent.segments:
           # seg.emphasis will be False (pyttsx3 doesn't support it)
           # seg.language will be None (pyttsx3 doesn't support it)
           print(seg.text)

Complete Demo
~~~~~~~~~~~~~

See ``examples/parser_demo.py`` for a comprehensive demonstration:

.. code-block:: bash

   python examples/parser_demo.py

The demo includes:

* Basic segment parsing
* Text transformations (say-as, substitution, phoneme)
* Voice block handling
* Complete TTS workflow
* Prosody and language annotations
* Advanced sentence parsing
* Mock TTS integration

See Also
--------

* :doc:`quickstart` - Getting started with SSMD
* :doc:`syntax` - SSMD syntax reference
* :doc:`examples` - More usage examples
* :doc:`api` - Complete API reference
