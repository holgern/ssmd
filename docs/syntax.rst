SSMD Syntax Reference
=====================

This page provides a complete reference for SSMD markup syntax.

Text and Emphasis
-----------------

Moderate Emphasis
~~~~~~~~~~~~~~~~~

Use single asterisks for moderate emphasis:

.. code-block:: python

   ssmd.to_ssml("This is *important*")
   # → <speak>This is <emphasis>important</emphasis></speak>

Strong Emphasis
~~~~~~~~~~~~~~~

Use double asterisks for strong emphasis:

.. code-block:: python

   ssmd.to_ssml("This is **very important**")
   # → <speak>This is <emphasis level="strong">very important</emphasis></speak>

Breaks and Pauses
-----------------

Time-Based Breaks
~~~~~~~~~~~~~~~~~

Specify duration in milliseconds or seconds using `...` followed by a time value:

.. code-block:: python

   ssmd.to_ssml("Wait ...500ms please")
   # → <speak>Wait <break time="500ms"/> please</speak>

   ssmd.to_ssml("Wait ...2s please")
   # → <speak>Wait <break time="2s"/> please</speak>

.. note::
   Bare `...` (without a time or strength code) is NOT treated as a break.
   It will be preserved as literal ellipsis in your text.

Strength-Based Breaks
~~~~~~~~~~~~~~~~~~~~~~

Use strength codes for semantic pauses:

.. code-block:: python

   ssmd.to_ssml("Hello ...n world")   # none
   ssmd.to_ssml("Hello ...w world")   # weak (x-weak)
   ssmd.to_ssml("Hello ...c world")   # comma (medium)
   ssmd.to_ssml("Hello ...s world")   # sentence (strong)
   ssmd.to_ssml("Hello ...p world")   # paragraph (x-strong)

Strength codes:

* ``n`` - none
* ``w`` - weak (x-weak)
* ``c`` - comma (medium)
* ``s`` - sentence (strong)
* ``p`` - paragraph (x-strong)

Paragraphs
----------

Blank lines separate paragraphs:

.. code-block:: python

   text = """
   This is the first paragraph.
   Still in first paragraph.

   This is the second paragraph.
   """

   ssmd.to_ssml(text)
   # → <speak><p>This is the first paragraph.
   #    Still in first paragraph.</p>
   #    <p>This is the second paragraph.</p></speak>

Headings
--------

Use hash marks for headings (configurable):

.. code-block:: python

   from ssmd import Document

   text = """
   # Main Title
   Content here.

   ## Subtitle
   More content.
   """

   doc = Document(text, heading_levels={
       1: [('emphasis', 'strong'), ('pause', '500ms')],
       2: [('emphasis', 'moderate')]
   })

   ssml = doc.to_ssml()

Annotations
-----------

Annotations use the format ``[text](annotation)`` where annotations can be:

Language Codes
~~~~~~~~~~~~~~

Specify language with ISO codes:

.. code-block:: python

   # Auto-complete to full locale
   ssmd.to_ssml('[Bonjour](fr)')
   # → <speak><lang xml:lang="fr-FR">Bonjour</lang></speak>

   # Explicit locale
   ssmd.to_ssml('[Hello](en-GB)')
   # → <speak><lang xml:lang="en-GB">Hello</lang></speak>

Common language codes:

* ``en`` → en-US
* ``fr`` → fr-FR
* ``de`` → de-DE
* ``es`` → es-ES
* ``it`` → it-IT
* ``ja`` → ja-JP
* ``zh`` → zh-CN
* ``ru`` → ru-RU

Voice Selection
~~~~~~~~~~~~~~~

SSMD supports two ways to specify voices: **inline annotations** for short phrases
and **block directives** for longer passages (ideal for dialogue and scripts).

Inline Voice Annotations
^^^^^^^^^^^^^^^^^^^^^^^^^

Perfect for short voice changes within a sentence:

.. code-block:: python

   # Simple voice name
   ssmd.to_ssml('[Hello](voice: Joanna)')
   # → <speak><voice name="Joanna">Hello</voice></speak>

   # Cloud TTS voice (e.g., Google Wavenet, AWS Polly)
   ssmd.to_ssml('[Hello](voice: en-US-Wavenet-A)')
   # → <speak><voice name="en-US-Wavenet-A">Hello</voice></speak>

   # Language and gender attributes
   ssmd.to_ssml('[Bonjour](voice: fr-FR, gender: female)')
   # → <speak><voice language="fr-FR" gender="female">Bonjour</voice></speak>

   # All attributes (language, gender, variant)
   ssmd.to_ssml('[Text](voice: en-GB, gender: male, variant: 1)')
   # → <speak><voice language="en-GB" gender="male" variant="1">Text</voice></speak>

Voice attributes:

* ``voice: NAME`` - Voice name (e.g., Joanna, en-US-Wavenet-A)
* ``gender: GENDER`` - male, female, or neutral
* ``variant: NUMBER`` - Variant number for tiebreaking

Voice Directives (Block Syntax)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Perfect for dialogue, podcasts, and scripts with multiple speakers:

.. code-block:: python

   # Use @voice: name or @voice(name) for clean dialogue formatting
   script = """
   @voice: af_sarah
   Welcome to Tech Talk! I'm Sarah, and today we're diving into the
   fascinating world of text-to-speech technology.
   ...s

   @voice: am_michael
   And I'm Michael! We've got an amazing episode lined up. The advances
   in neural TTS have been incredible lately.
   ...s

   @voice: af_sarah
   So what are we covering today?
   """

   ssmd.to_ssml(script)
   # Each voice directive creates a separate voice block in SSML

Voice directive features:

* Use ``@voice: name`` or ``@voice(name)`` syntax
* Applies to all text until the next directive or paragraph break
* Automatically detected on SSML→SSMD conversion for long voice blocks
* Much more readable than inline annotations for dialogue

Mixing inline and directive syntax:

.. code-block:: python

   # Block directive for main speaker, inline for interruptions
   text = """
   @voice: sarah
   Hello everyone, [but wait!](voice: michael) Michael interrupts...

   @voice: michael
   Sorry, I had to jump in there!
   """


Phonetic Pronunciation
~~~~~~~~~~~~~~~~~~~~~~

IPA (International Phonetic Alphabet)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   ssmd.to_ssml('[tomato](ph: təˈmeɪtoʊ)')
   # → <speak><phoneme alphabet="ipa" ph="təˈmeɪtoʊ">tomato</phoneme></speak>

   ssmd.to_ssml('[hello](ipa: həˈloʊ)')
   # → <speak><phoneme alphabet="ipa" ph="həˈloʊ">hello</phoneme></speak>

X-SAMPA (Extended Speech Assessment Methods Phonetic Alphabet)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   ssmd.to_ssml('[dictionary](sampa: dIkS@n@ri)')
   # → <speak><phoneme alphabet="x-sampa" ph="dIkS@n@ri">dictionary</phoneme></speak>

Substitution (Aliases)
~~~~~~~~~~~~~~~~~~~~~~

Replace text with alternative pronunciation:

.. code-block:: python

   ssmd.to_ssml('[H2O](sub: water)')
   # → <speak><sub alias="water">H2O</sub></speak>

   ssmd.to_ssml('[AWS](sub: Amazon Web Services)')
   # → <speak><sub alias="Amazon Web Services">AWS</sub></speak>

   ssmd.to_ssml('[NATO](sub: North Atlantic Treaty Organization)')

Say-As Interpretations
~~~~~~~~~~~~~~~~~~~~~~

Control how text is interpreted:

.. code-block:: python

   # Telephone number
   ssmd.to_ssml('[+1-555-0123](as: telephone)')

   # Date with format
   ssmd.to_ssml('[31.12.2024](as: date, format: "dd.mm.yyyy")')

   # Spell out characters
   ssmd.to_ssml('[NASA](as: character)')

   # Number types
   ssmd.to_ssml('[123](as: cardinal)')     # one hundred twenty-three
   ssmd.to_ssml('[1st](as: ordinal)')      # first
   ssmd.to_ssml('[123](as: digits)')       # one two three
   ssmd.to_ssml('[3.14](as: fraction)')    # three point one four

   # Time
   ssmd.to_ssml('[14:30](as: time)')

   # Expletive (censored/beeped)
   ssmd.to_ssml('[damn](as: expletive)')

Supported interpret-as values:

* ``character`` - Spell out
* ``cardinal`` - Number
* ``ordinal`` - First, second, etc.
* ``digits`` - Individual digits
* ``fraction`` - Decimal numbers
* ``unit`` - Measurements
* ``date`` - Dates
* ``time`` - Time values
* ``telephone`` - Phone numbers
* ``address`` - Street addresses
* ``expletive`` - Censored words

Prosody (Voice Control)
------------------------

Shorthand Notation
~~~~~~~~~~~~~~~~~~

Volume
^^^^^^

.. code-block:: python

   ssmd.to_ssml("~silent~")        # silent
   ssmd.to_ssml("--whisper--")     # x-soft
   ssmd.to_ssml("-soft-")          # soft
   ssmd.to_ssml("+loud+")          # loud
   ssmd.to_ssml("++very loud++")   # x-loud

Rate (Speed)
^^^^^^^^^^^^

.. code-block:: python

   ssmd.to_ssml("<<very slow<<")   # x-slow
   ssmd.to_ssml("<slow<")          # slow
   ssmd.to_ssml(">fast>")          # fast
   ssmd.to_ssml(">>very fast>>")   # x-fast

Pitch
^^^^^

.. code-block:: python

   ssmd.to_ssml("__very low__")    # x-low
   ssmd.to_ssml("_low_")           # low
   ssmd.to_ssml("^high^")          # high
   ssmd.to_ssml("^^very high^^")   # x-high

Explicit Notation
~~~~~~~~~~~~~~~~~

Scale-Based Values (1-5)
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Volume, Rate, Pitch (combined)
   ssmd.to_ssml('[loud and fast](vrp: 555)')
   # → <prosody volume="x-loud" rate="x-fast" pitch="x-high">loud and fast</prosody>

   # Individual attributes
   ssmd.to_ssml('[text](v: 5)')    # x-loud
   ssmd.to_ssml('[text](r: 4)')    # fast
   ssmd.to_ssml('[text](p: 2)')    # low

   # Multiple attributes
   ssmd.to_ssml('[text](v: 4, r: 2, p: 3)')
   # → <prosody volume="loud" rate="slow" pitch="medium">text</prosody>

Scale mapping:

* Volume (v:): 0=silent, 1=x-soft, 2=soft, 3=medium, 4=loud, 5=x-loud
* Rate (r:): 1=x-slow, 2=slow, 3=medium, 4=fast, 5=x-fast
* Pitch (p:): 1=x-low, 2=low, 3=medium, 4=high, 5=x-high

Relative Values
^^^^^^^^^^^^^^^

.. code-block:: python

   # Decibels for volume
   ssmd.to_ssml('[louder](v: +6dB)')
   ssmd.to_ssml('[quieter](v: -3dB)')

   # Percentages for rate and pitch
   ssmd.to_ssml('[faster](r: +20%)')
   ssmd.to_ssml('[slower](r: -10%)')
   ssmd.to_ssml('[higher](p: +15%)')
   ssmd.to_ssml('[lower](p: -5%)')

Audio Files
-----------

Basic Audio
~~~~~~~~~~~

.. code-block:: python

   # With description
   ssmd.to_ssml('[doorbell](https://example.com/sounds/bell.mp3)')
   # → <audio src="https://example.com/sounds/bell.mp3"><desc>doorbell</desc></audio>

   # No description
   ssmd.to_ssml('[](beep.mp3)')
   # → <audio src="beep.mp3"></audio>

Audio with Fallback
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   ssmd.to_ssml('[cat purring](cat.ogg Sound file not loaded)')
   # → <audio src="cat.ogg"><desc>cat purring</desc>Sound file not loaded</audio>

The fallback text is spoken if the audio file can't be played.

Markers
-------

Markers create synchronization points for events:

.. code-block:: python

   ssmd.to_ssml('I always wanted a @animal cat as a pet.')
   # → <speak>I always wanted a <mark name="animal"/> cat as a pet.</speak>

   ssmd.to_ssml('Click @here to continue.')
   # → <speak>Click <mark name="here"/> to continue.</speak>

Markers are removed when stripping to plain text:

.. code-block:: python

   ssmd.to_text('Click @here now')
   # → Click now

Extensions
----------

Platform-specific extensions:

.. code-block:: python

   # Amazon whisper effect
   ssmd.to_ssml('[secret message](ext: whisper)')
   # → <amazon:effect name="whispered">secret message</amazon:effect>

Custom extensions can be registered via configuration.

Combining Multiple Annotations
-------------------------------

Multiple annotations can be comma-separated:

.. code-block:: python

   ssmd.to_ssml('[Bonjour](fr, v: 5, r: 2)')
   # → <lang xml:lang="fr-FR"><prosody volume="x-loud" rate="slow">Bonjour</prosody></lang>

   ssmd.to_ssml('[important](v: 5, as: character)')
   # → <prosody volume="x-loud"><say-as interpret-as="character">important</say-as></prosody>

Escaping
--------

XML Special Characters
~~~~~~~~~~~~~~~~~~~~~~~

XML special characters are automatically escaped:

.. code-block:: python

   ssmd.to_ssml('5 < 10 & 10 > 5')
   # → <speak>5 &lt; 10 &amp; 10 &gt; 5</speak>

Literal Asterisks
~~~~~~~~~~~~~~~~~

To include literal asterisks without emphasis, escape them or use different patterns:

.. code-block:: python

   # These won't be treated as emphasis
   ssmd.to_ssml('2 * 3 = 6')
   # → <speak>2 * 3 = 6</speak>

   ssmd.to_ssml('* list item')
   # → <speak>* list item</speak>
