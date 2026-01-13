API Reference
=============

This page documents the public API of the SSMD library.

Core Classes
------------

Document
~~~~~~~~

The primary class for creating and managing SSMD/SSML documents.

.. autoclass:: ssmd.Document
   :members:
   :undoc-members:
   :show-inheritance:

   **Construction Methods:**

   .. automethod:: __init__
   .. automethod:: from_ssml
   .. automethod:: from_text

   **Building Methods:**

   .. automethod:: add
   .. automethod:: add_sentence
   .. automethod:: add_paragraph

   **Export Methods:**

   .. automethod:: to_ssml
   .. automethod:: to_ssmd
   .. automethod:: to_text

   **Properties:**

   .. autoproperty:: ssmd
   .. autoproperty:: config
   .. autoproperty:: capabilities

   **Iteration:**

   .. automethod:: sentences
   .. automethod:: __iter__
   .. automethod:: __len__

   **List-like Interface:**

   .. automethod:: __getitem__
   .. automethod:: __setitem__
   .. automethod:: __delitem__
   .. automethod:: __iadd__

   **Editing Methods:**

   .. automethod:: insert
   .. automethod:: remove
   .. automethod:: clear
   .. automethod:: replace

   **Advanced Methods:**

   .. automethod:: merge
   .. automethod:: split
   .. automethod:: get_fragment

TTSCapabilities
~~~~~~~~~~~~~~~

Define TTS engine capabilities for automatic feature filtering.

.. autoclass:: ssmd.TTSCapabilities
   :members:
   :undoc-members:
   :show-inheritance:

SSMLParser
~~~~~~~~~~

Parse SSML and convert to SSMD format.

.. autoclass:: ssmd.SSMLParser
   :members:
   :undoc-members:
   :show-inheritance:

Convenience Functions
---------------------

Parser Functions
~~~~~~~~~~~~~~~~

Extract structured data from SSMD text.

.. autofunction:: ssmd.parse_sentences
.. autofunction:: ssmd.parse_segments
.. autofunction:: ssmd.parse_voice_blocks

Conversion Functions
~~~~~~~~~~~~~~~~~~~~

Convert between SSMD, SSML, and plain text.

to_ssml
^^^^^^^

Convert SSMD markup to SSML.

.. autofunction:: ssmd.to_ssml

to_text
^^^^^^^

Convert SSMD to plain text (strips all markup).

.. autofunction:: ssmd.to_text

from_ssml
^^^^^^^^^

Convert SSML back to SSMD format.

.. autofunction:: ssmd.from_ssml

Parser Data Structures
----------------------

Sentence (alias: SSMDSentence)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Represents a sentence with voice context and segments.

.. autoclass:: ssmd.Sentence
   :members:
   :undoc-members:
   :show-inheritance:

Segment (alias: SSMDSegment)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Represents a text segment with metadata.

.. autoclass:: ssmd.Segment
   :members:
   :undoc-members:
   :show-inheritance:

VoiceAttrs
~~~~~~~~~~

Voice configuration attributes.

.. autoclass:: ssmd.VoiceAttrs
   :members:
   :undoc-members:
   :show-inheritance:

ProsodyAttrs
~~~~~~~~~~~~

Prosody (volume, rate, pitch) attributes.

.. autoclass:: ssmd.ProsodyAttrs
   :members:
   :undoc-members:
   :show-inheritance:

BreakAttrs
~~~~~~~~~~

Pause/break attributes.

.. autoclass:: ssmd.BreakAttrs
   :members:
   :undoc-members:
   :show-inheritance:

SayAsAttrs
~~~~~~~~~~

Say-as interpretation attributes.

.. autoclass:: ssmd.SayAsAttrs
   :members:
   :undoc-members:
   :show-inheritance:

PhonemeAttrs
~~~~~~~~~~~~

Phonetic pronunciation attributes.

.. autoclass:: ssmd.PhonemeAttrs
   :members:
   :undoc-members:
   :show-inheritance:

AudioAttrs
~~~~~~~~~~

Audio file attributes.

.. autoclass:: ssmd.AudioAttrs
   :members:
   :undoc-members:
   :show-inheritance:

Capability Presets
------------------

Pre-configured capability sets for common TTS engines.

.. autodata:: ssmd.MINIMAL_CAPABILITIES
.. autodata:: ssmd.PYTTSX3_CAPABILITIES
.. autodata:: ssmd.ESPEAK_CAPABILITIES
.. autodata:: ssmd.GOOGLE_TTS_CAPABILITIES
.. autodata:: ssmd.AZURE_TTS_CAPABILITIES
.. autodata:: ssmd.AMAZON_POLLY_CAPABILITIES
.. autodata:: ssmd.FULL_CAPABILITIES

.. autofunction:: ssmd.get_preset

Internal Modules
----------------

SSML Parser
~~~~~~~~~~~

Internal SSML to SSMD parsing engine.

.. automodule:: ssmd.ssml_parser
   :members:
   :undoc-members:
   :show-inheritance:

Document Module
~~~~~~~~~~~~~~~

Document container implementation.

.. automodule:: ssmd.document
   :members:
   :undoc-members:
   :show-inheritance:

Parser Module
~~~~~~~~~~~~~

SSMD parsing functions for extracting structured data.

.. automodule:: ssmd.parser
   :members:
   :undoc-members:
   :show-inheritance:

Segment Module
~~~~~~~~~~~~~~

Segment class for representing text portions with attributes.

.. automodule:: ssmd.segment
   :members:
   :undoc-members:
   :show-inheritance:

Sentence Module
~~~~~~~~~~~~~~~

Sentence class for representing collections of segments.

.. automodule:: ssmd.sentence
   :members:
   :undoc-members:
   :show-inheritance:

Types Module
~~~~~~~~~~~~

Data types used throughout the SSMD library.

.. automodule:: ssmd.types
   :members:
   :undoc-members:
   :show-inheritance:

Utilities
~~~~~~~~~

Helper functions for SSML processing.

.. automodule:: ssmd.utils
   :members:
   :undoc-members:
   :show-inheritance:
