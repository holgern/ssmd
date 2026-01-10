SSMD - Speech Synthesis Markdown
==================================

**SSMD** (Speech Synthesis Markdown) is a lightweight Python library that provides a
human-friendly markdown-like syntax for creating SSML (Speech Synthesis Markup Language)
documents. It's designed to make TTS (Text-to-Speech) content more readable and
maintainable.

.. image:: https://img.shields.io/pypi/v/ssmd
   :target: https://pypi.org/project/ssmd/
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/ssmd
   :alt: Python Versions

.. image:: https://codecov.io/gh/holgern/ssmd/graph/badge.svg?token=iCHXwbjAXG
   :target: https://codecov.io/gh/holgern/ssmd
   :alt: Code Coverage

Features
--------

✨ **Markdown-like syntax** - More intuitive than raw SSML

🎯 **Full SSML support** - All major SSML features covered

🔄 **Bidirectional** - Convert SSMD↔SSML or strip to plain text

📝 **TTS streaming** - Iterate through sentences for real-time TTS

🎛️ **TTS capabilities** - Auto-filter features based on engine support

🎨 **Extensible** - Custom extensions for platform-specific features

🧪 **Type-safe** - Full mypy type checking support

Quick Example
-------------

.. code-block:: python

   import ssmd

   # Convert SSMD to SSML
   ssml = ssmd.to_ssml("Hello *world*!")
   # → <speak>Hello <emphasis>world</emphasis>!</speak>

   # Convert SSML back to SSMD
   ssmd_text = ssmd.from_ssml('<speak><emphasis>Hello</emphasis></speak>')
   # → *Hello*

   # Strip markup for plain text
   plain = ssmd.strip_ssmd("Hello *world* @marker!")
   # → Hello world!

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   syntax
   capabilities
   ssml_conversion
   examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
