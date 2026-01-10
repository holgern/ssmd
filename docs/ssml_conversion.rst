SSML to SSMD Conversion
=======================

SSMD supports bidirectional conversion: you can convert SSML back to SSMD format.
This is useful for editing existing SSML, migrating from other tools, or creating
round-trip workflows.

Basic Conversion
----------------

Using the Convenience Function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import ssmd

   # Convert SSML to SSMD
   ssml = '<speak><emphasis>Hello</emphasis> world</speak>'
   ssmd_text = ssmd.from_ssml(ssml)
   print(ssmd_text)
   # Output: *Hello* world

Using the Document Class
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ssmd import Document

   ssml = '<speak><emphasis>Hello</emphasis> world</speak>'
   doc = Document.from_ssml(ssml)
   ssmd_text = doc.to_ssmd()
   print(ssmd_text)
   # Output: *Hello* world

Supported SSML Elements
------------------------

Emphasis
~~~~~~~~

.. code-block:: python

   # Moderate emphasis
   ssmd.from_ssml('<emphasis>text</emphasis>')
   # → *text*

   # Strong emphasis
   ssmd.from_ssml('<emphasis level="strong">text</emphasis>')
   # → **text**

Breaks
~~~~~~

.. code-block:: python

   # Time-based breaks
   ssmd.from_ssml('<break time="500ms"/>')
   # → ...500ms

   ssmd.from_ssml('<break time="2s"/>')
   # → ...2s

   # Strength-based breaks
   ssmd.from_ssml('<break strength="weak"/>')
   # → ...w

   ssmd.from_ssml('<break strength="medium"/>')
   # → ...c

   ssmd.from_ssml('<break strength="strong"/>')
   # → ...s

Language
~~~~~~~~

.. code-block:: python

   # Full locale
   ssmd.from_ssml('<lang xml:lang="fr-FR">Bonjour</lang>')
   # → [Bonjour](fr)

   # Non-standard locales preserved
   ssmd.from_ssml('<lang xml:lang="en-GB">Hello</lang>')
   # → [Hello](en-GB)

Phonemes
~~~~~~~~

.. code-block:: python

   # IPA notation
   ssmd.from_ssml('<phoneme alphabet="ipa" ph="təˈmeɪtoʊ">tomato</phoneme>')
   # → [tomato](ph: təˈmeɪtoʊ)

   # X-SAMPA notation
   ssmd.from_ssml('<phoneme alphabet="x-sampa" ph="t@meIt@U">tomato</phoneme>')
   # → [tomato](sampa: t@meIt@U)

Prosody
~~~~~~~

.. code-block:: python

   # Volume
   ssmd.from_ssml('<prosody volume="loud">text</prosody>')
   # → [text](v: 4)

   ssmd.from_ssml('<prosody volume="x-loud">text</prosody>')
   # → [text](v: 5)

   # Rate
   ssmd.from_ssml('<prosody rate="fast">text</prosody>')
   # → [text](r: 4)

   # Pitch
   ssmd.from_ssml('<prosody pitch="high">text</prosody>')
   # → [text](p: 4)

   # Multiple attributes
   ssmd.from_ssml('<prosody volume="loud" rate="fast" pitch="high">text</prosody>')
   # → [text](v: 4, r: 4, p: 4)

Say-As
~~~~~~

.. code-block:: python

   # Basic say-as
   ssmd.from_ssml('<say-as interpret-as="telephone">+1-555-1234</say-as>')
   # → [+1-555-1234](as: telephone)

   # With format attribute
   ssmd.from_ssml('<say-as interpret-as="date" format="mdy">12/31/2024</say-as>')
   # → [12/31/2024](as: date, format: "mdy")

Substitution
~~~~~~~~~~~~

.. code-block:: python

   ssmd.from_ssml('<sub alias="World Wide Web">WWW</sub>')
   # → [WWW](sub: World Wide Web)

Audio
~~~~~

.. code-block:: python

   # With description
   ssmd.from_ssml('<audio src="sound.mp3">Alternative text</audio>')
   # → [](sound.mp3 Alternative text)

   # With desc tag
   ssmd.from_ssml('<audio src="bell.mp3"><desc>doorbell</desc></audio>')
   # → [doorbell](bell.mp3)

   # No description
   ssmd.from_ssml('<audio src="beep.mp3"></audio>')
   # → [](beep.mp3)

Marks
~~~~~

.. code-block:: python

   ssmd.from_ssml('Text <mark name="here"/> more text')
   # → Text @here more text

Paragraphs
~~~~~~~~~~

.. code-block:: python

   ssml = '''<speak>
   <p>First paragraph.</p>
   <p>Second paragraph.</p>
   </speak>'''

   ssmd_text = ssmd.from_ssml(ssml)
   # Output:
   # First paragraph.
   #
   # Second paragraph.

Platform Extensions
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Amazon whisper effect
   ssml = '<amazon:effect name="whispered">secret</amazon:effect>'
   ssmd.from_ssml(ssml)
   # → [secret](ext: whisper)

Default Value Filtering
------------------------

SSMD automatically removes default/medium values to keep output clean:

.. code-block:: python

   # Medium values are filtered out
   ssml = '<prosody volume="medium" rate="medium" pitch="medium">text</prosody>'
   ssmd.from_ssml(ssml)
   # → text  (not [text](v: 3, r: 3, p: 3))

   # Only non-default values are included
   ssml = '<prosody volume="loud" rate="medium" pitch="medium">text</prosody>'
   ssmd.from_ssml(ssml)
   # → [text](v: 4)

Round-Trip Conversion
---------------------

Convert SSMD → SSML → SSMD preserving semantics:

.. code-block:: python

   import ssmd

   # Original SSMD
   original = "*Hello* [world](fr) ...500ms +loud+"

   # Convert to SSML
   ssml = ssmd.to_ssml(original)
   print(ssml)
   # <speak><emphasis>Hello</emphasis> <lang xml:lang="fr-FR">world</lang>
   #  <break time="500ms"/> <prosody volume="loud">loud</prosody></speak>

   # Convert back to SSMD
   restored = ssmd.from_ssml(ssml)
   print(restored)
   # *Hello* [world](fr) ...500ms [loud](v: 4)

   # Semantically equivalent, even if syntax differs slightly

Complex Examples
----------------

Nested Elements
~~~~~~~~~~~~~~~

.. code-block:: python

   ssml = '''<speak>
   <p>
     <emphasis>Important:</emphasis>
     <lang xml:lang="fr-FR">
       <prosody volume="loud">Bonjour</prosody>
     </lang>
   </p>
   </speak>'''

   ssmd_text = ssmd.from_ssml(ssml)
   # Output: *Important:* [[Bonjour](v: 4)](fr)

Mixed Content
~~~~~~~~~~~~~

.. code-block:: python

   ssml = '''<speak>
   <p><emphasis>Hello</emphasis> world</p>
   <p>This is <prosody volume="loud">important</prosody></p>
   <break time="500ms"/>
   <p>Goodbye</p>
   </speak>'''

   ssmd_text = ssmd.from_ssml(ssml)
   # Output:
   # *Hello* world
   #
   # This is [important](v: 4)
   #
   # ...500ms
   #
   # Goodbye

Whitespace Handling
-------------------

SSMD normalizes whitespace during conversion:

.. code-block:: python

   # Extra whitespace is normalized
   ssml = '''<speak>
     <emphasis>
       Hello
     </emphasis>
     world
   </speak>'''

   ssmd_text = ssmd.from_ssml(ssml)
   # → *Hello* world  (whitespace normalized)

Error Handling
--------------

Invalid SSML
~~~~~~~~~~~~

.. code-block:: python

   import ssmd

   try:
       ssmd.from_ssml('<speak><invalid>text</invalid></speak>')
   except ValueError as e:
       print(f"Error: {e}")

   # Invalid/unknown tags are treated as plain text

Malformed XML
~~~~~~~~~~~~~

.. code-block:: python

   try:
       ssmd.from_ssml('<speak><emphasis>unclosed</speak>')
   except ValueError as e:
       print(f"XML Parse Error: {e}")

Configuration Options
---------------------

.. code-block:: python

   from ssmd import Document

   parser = Document(capabilities='espeak')

   # SSML features not supported by eSpeak will be simplified
   ssml = '<speak><emphasis>Hello</emphasis></speak>'
   doc = Document.from_ssml(ssml, capabilities='espeak')
   ssmd_text = doc.to_ssmd()
   # eSpeak doesn't support emphasis, so output is just: Hello

Use Cases
---------

Migration from Raw SSML
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ssmd import Document

   # You have existing SSML files
   with open('old_ssml.xml') as f:
       ssml = f.read()

   # Convert to SSMD for easier editing
   doc = Document.from_ssml(ssml)
   ssmd_text = doc.to_ssmd()

   with open('new_ssmd.txt', 'w') as f:
       f.write(ssmd_text)

SSML Editor Backend
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ssmd import Document

   # Load SSML for editing
   def load_document(ssml_file):
       with open(ssml_file) as f:
           ssml = f.read()
       return Document.from_ssml(ssml)

   # Save as SSML
   def save_document(doc, ssml_file):
       ssml = doc.to_ssml()
       with open(ssml_file, 'w') as f:
           f.write(ssml)

Testing and Validation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ssmd import Document

   # Validate SSML by round-trip conversion
   def validate_ssml(ssml_text):
       try:
           doc = Document.from_ssml(ssml_text)
           restored_ssml = doc.to_ssml()
           return True
       except Exception as e:
           print(f"Validation failed: {e}")
           return False

Limitations
-----------

1. **Syntax differences**: Round-trip conversion is semantically equivalent but may
   use different syntax (e.g., ``+loud+`` becomes ``[loud](v: 4)``)

2. **Comments lost**: XML comments are not preserved

3. **Unknown elements**: Custom SSML elements are converted to plain text

4. **Attribute order**: Attribute order may change but semantics are preserved

5. **Whitespace**: Whitespace is normalized for readability
