API Reference
=============

This page documents the public API of the SSMD library.

Core Classes
------------

SSMD
~~~~

.. autoclass:: ssmd.SSMD
   :members:
   :undoc-members:
   :show-inheritance:

SSMDDocument
~~~~~~~~~~~~

.. autoclass:: ssmd.SSMDDocument
   :members:
   :undoc-members:
   :show-inheritance:

TTSCapabilities
~~~~~~~~~~~~~~~

.. autoclass:: ssmd.TTSCapabilities
   :members:
   :undoc-members:
   :show-inheritance:

ProsodySupport
~~~~~~~~~~~~~~

.. autoclass:: ssmd.ProsodySupport
   :members:
   :undoc-members:
   :show-inheritance:

Convenience Functions
---------------------

to_ssml
~~~~~~~

.. autofunction:: ssmd.to_ssml

strip_ssmd
~~~~~~~~~~

.. autofunction:: ssmd.strip_ssmd

from_ssml
~~~~~~~~~

.. autofunction:: ssmd.from_ssml

Internal Modules
----------------

Converter
~~~~~~~~~

.. automodule:: ssmd.converter
   :members:
   :undoc-members:
   :show-inheritance:

SSML Parser
~~~~~~~~~~~

.. automodule:: ssmd.ssml_parser
   :members:
   :undoc-members:
   :show-inheritance:

Processors
~~~~~~~~~~

.. automodule:: ssmd.processors.base
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: ssmd.processors.emphasis
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: ssmd.processors.break_processor
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: ssmd.processors.prosody
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: ssmd.processors.annotation
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: ssmd.processors.paragraph
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: ssmd.processors.heading
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: ssmd.processors.mark
   :members:
   :undoc-members:
   :show-inheritance:

Annotations
~~~~~~~~~~~

.. automodule:: ssmd.annotations.base
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: ssmd.annotations.language
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: ssmd.annotations.phoneme
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: ssmd.annotations.prosody
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: ssmd.annotations.substitution
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: ssmd.annotations.say_as
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: ssmd.annotations.audio
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: ssmd.annotations.extension
   :members:
   :undoc-members:
   :show-inheritance:

Utilities
~~~~~~~~~

.. automodule:: ssmd.utils
   :members:
   :undoc-members:
   :show-inheritance:
