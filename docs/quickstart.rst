Quick Start
===========

This guide will help you get started with SSMD quickly.

Basic Conversion
----------------

The simplest way to use SSMD is with the convenience functions:

SSMD to SSML
~~~~~~~~~~~~

.. code-block:: python

   import ssmd

   # Convert SSMD markup to SSML
   ssml = ssmd.to_ssml("Hello *world*!")
   print(ssml)
   # Output: <speak>Hello <emphasis>world</emphasis>!</speak>

   # More complex example
   ssml = ssmd.to_ssml("""
   # Welcome
   Hello *world*!
   This is a ...500ms pause.
   [Bonjour](fr) everyone!
   """)

Strip Markup
~~~~~~~~~~~~

Remove all SSMD markup to get plain text:

.. code-block:: python

   import ssmd

   plain = ssmd.strip_ssmd("Hello *world* @marker!")
   print(plain)
   # Output: Hello world!

SSML to SSMD
~~~~~~~~~~~~

Convert SSML back to SSMD format:

.. code-block:: python

   import ssmd

   ssml = '<speak><emphasis>Hello</emphasis> world</speak>'
   ssmd_text = ssmd.from_ssml(ssml)
   print(ssmd_text)
   # Output: *Hello* world

Using the SSMD Class
--------------------

For more control, create an SSMD parser instance:

.. code-block:: python

   from ssmd import SSMD

   # Create parser with default settings
   parser = SSMD()

   # Convert to SSML
   ssml = parser.to_ssml("Hello *world*!")

   # Strip markup
   plain = parser.strip("Hello *world*!")

   # Convert from SSML
   ssmd_text = parser.from_ssml('<speak><emphasis>Hello</emphasis></speak>')

Configuration Options
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ssmd import SSMD

   # Create parser with custom configuration
   parser = SSMD({
       'output_speak_tag': True,      # Wrap in <speak> tags (default: True)
       'pretty_print': True,           # Format XML output (default: False)
       'auto_sentence_tags': True,     # Wrap sentences in <s> (default: False)
       'heading_levels': {
           1: [('emphasis', 'strong'), ('pause', '300ms')],
           2: [('emphasis', 'moderate')]
       }
   })

   text = """
   # Main Title
   This is a paragraph.
   
   ## Subtitle
   Another paragraph here.
   """

   ssml = parser.to_ssml(text)

TTS Streaming
-------------

Load documents for sentence-by-sentence processing:

.. code-block:: python

   from ssmd import SSMD

   # Create parser
   parser = SSMD({'auto_sentence_tags': True})

   # Load a document
   doc = parser.load("""
   # Chapter 1
   Welcome to SSMD!
   This is the first sentence.
   This is the second sentence.
   
   # Chapter 2
   Here's another chapter.
   """)

   # Iterate through sentences
   for i, sentence in enumerate(doc, 1):
       print(f"Sentence {i}: {sentence}")
       # Your TTS engine here:
       # tts_engine.speak(sentence)

   # Access specific sentences
   print(f"Total: {len(doc)} sentences")
   print(f"First: {doc[0]}")

   # Get full document
   print(doc.ssml)        # Complete SSML
   print(doc.plain_text)  # Plain text

Working with TTS Engines
-------------------------

Filter output based on engine capabilities:

Using Presets
~~~~~~~~~~~~~

.. code-block:: python

   from ssmd import SSMD

   # Use preset for eSpeak (limited SSML support)
   parser = SSMD(capabilities='espeak')

   ssml = parser.to_ssml("*Hello* [world](fr)!")
   # eSpeak doesn't support emphasis or language switching
   # Output: <speak>Hello world!</speak>

   # Use preset for Google TTS (full support)
   parser = SSMD(capabilities='google')
   ssml = parser.to_ssml("*Hello* [world](fr)!")
   # Output: <speak><emphasis>Hello</emphasis> <lang xml:lang="fr-FR">world</lang>!</speak>

Available presets:

* ``minimal`` - Plain text only
* ``pyttsx3`` - Basic prosody only
* ``espeak`` - Moderate support (breaks, prosody, phonemes)
* ``google`` / ``azure`` - Full SSML support
* ``polly`` / ``amazon`` - Full + Amazon extensions
* ``full`` - All features enabled

Common Patterns
---------------

Emphasis and Stress
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   ssmd.to_ssml("This is *important*!")
   ssmd.to_ssml("This is **very important**!")

Pauses and Breaks
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Default pause (1000ms)
   ssmd.to_ssml("Hello ... world")

   # Specific duration
   ssmd.to_ssml("Hello ...500ms world")
   ssmd.to_ssml("Hello ...2s world")

   # Strength-based
   ssmd.to_ssml("Hello ...c world")  # comma
   ssmd.to_ssml("Hello ...s world")  # sentence
   ssmd.to_ssml("Hello ...p world")  # paragraph

Voice Control
~~~~~~~~~~~~~

.. code-block:: python

   # Volume
   ssmd.to_ssml("This is +loud+")
   ssmd.to_ssml("This is ++very loud++")
   ssmd.to_ssml("This is -soft-")

   # Speed
   ssmd.to_ssml("This is >fast>")
   ssmd.to_ssml("This is >>very fast>>")
   ssmd.to_ssml("This is <slow<")

   # Pitch
   ssmd.to_ssml("This is ^high^")
   ssmd.to_ssml("This is ^^very high^^")
   ssmd.to_ssml("This is _low_")

Language Switching
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   ssmd.to_ssml('[Bonjour](fr) everyone!')
   ssmd.to_ssml('[Hola](es-MX) amigos!')
   ssmd.to_ssml('[Hello](en-GB) there!')

Phonetic Pronunciation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   ssmd.to_ssml('[tomato](ph: təˈmeɪtoʊ)')
   ssmd.to_ssml('[hello](ipa: həˈloʊ)')

Next Steps
----------

* Read the complete :doc:`syntax` reference
* Learn about :doc:`capabilities` filtering
* Explore :doc:`examples` for real-world use cases
* Check the :doc:`api` documentation for advanced usage
