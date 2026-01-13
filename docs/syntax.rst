SSMD Syntax Reference
=====================

This page provides a complete reference for SSMD markup syntax.

Text and Emphasis
-----------------

SSMD supports all four SSML emphasis levels for fine-grained control over speech emphasis.

Moderate Emphasis
~~~~~~~~~~~~~~~~~

Use single asterisks for moderate (default) emphasis:

.. code-block:: python

   ssmd.to_ssml("This is *important*")
   # → <speak>This is <emphasis>important</emphasis></speak>

Strong Emphasis
~~~~~~~~~~~~~~~

Use double asterisks for strong emphasis:

.. code-block:: python

   ssmd.to_ssml("This is **very important**")
   # → <speak>This is <emphasis level="strong">very important</emphasis></speak>

Reduced Emphasis
~~~~~~~~~~~~~~~~

Use single underscores for reduced (subtle) emphasis:

.. code-block:: python

   ssmd.to_ssml("This is _less important_")
   # → <speak>This is <emphasis level="reduced">less important</emphasis></speak>

No Emphasis
~~~~~~~~~~~

Use explicit annotation syntax for no emphasis (rarely used):

.. code-block:: python

   ssmd.to_ssml("[monotone reading](emphasis: none)")
   # → <speak><emphasis level="none">monotone reading</emphasis></speak>

.. note::
   The "none" emphasis level is rarely needed in practice. It explicitly instructs
   the TTS engine to speak without any emphasis, which can be useful for robotic
   or monotone speech effects.

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
   # → <speak>This is the first paragraph.
   #    Still in first paragraph.
   #    This is the second paragraph.</speak>

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

Voice directives support all voice attributes:

.. code-block:: python

   # Language and gender
   multilingual = """
   @voice: fr-FR, gender: female
   Bonjour! Comment allez-vous aujourd'hui?

   @voice: en-GB, gender: male
   Hello there! Lovely weather we're having.

   @voice: es-ES, gender: female, variant: 1
   ¡Hola! ¿Cómo estás?
   """

Voice directive features:

* Use ``@voice: name`` or ``@voice(name)`` syntax
* Supports all attributes: language, gender, variant
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

   # Say-as with detail attribute (verbosity control)
   ssmd.to_ssml('[123](as: cardinal, detail: 2)')
   # → <speak><say-as interpret-as="cardinal" detail="2">123</say-as></speak>

   ssmd.to_ssml('[12/31/2024](as: date, format: "mdy", detail: 1)')
   # → <speak><say-as interpret-as="date" format="mdy" detail="1">12/31/2024</say-as></speak>

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

The ``detail`` attribute (1-2) controls verbosity level and is platform-specific.
Higher values generally provide more detailed pronunciation.

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

Advanced Audio Attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~

SSMD supports advanced audio control through SSML attributes:

Audio Clipping
^^^^^^^^^^^^^^

Play a portion of an audio file by specifying start and end times:

.. code-block:: python

   ssmd.to_ssml('[music](song.mp3 clip: 5s-30s)')
   # → <audio src="song.mp3" clipBegin="5s" clipEnd="30s"><desc>music</desc></audio>

   ssmd.to_ssml('[intro](podcast.mp3 clip: 0s-10s)')
   # → <audio src="podcast.mp3" clipBegin="0s" clipEnd="10s"><desc>intro</desc></audio>

Speed Control
^^^^^^^^^^^^^

Adjust playback speed using percentages:

.. code-block:: python

   ssmd.to_ssml('[announcement](speech.mp3 speed: 150%)')
   # → <audio src="speech.mp3" speed="150%"><desc>announcement</desc></audio>

   ssmd.to_ssml('[slow](message.mp3 speed: 80%)')
   # → <audio src="message.mp3" speed="80%"><desc>slow</desc></audio>

Repeat Audio
^^^^^^^^^^^^

Repeat audio playback a specific number of times:

.. code-block:: python

   ssmd.to_ssml('[jingle](ad.mp3 repeat: 3)')
   # → <audio src="ad.mp3" repeatCount="3"><desc>jingle</desc></audio>

   ssmd.to_ssml('[beep](alert.mp3 repeat: 5)')
   # → <audio src="alert.mp3" repeatCount="5"><desc>beep</desc></audio>

Volume Adjustment
^^^^^^^^^^^^^^^^^

Control audio volume using decibel adjustment:

.. code-block:: python

   ssmd.to_ssml('[alarm](alert.mp3 level: +6dB)')
   # → <audio src="alert.mp3" soundLevel="+6dB"><desc>alarm</desc></audio>

   ssmd.to_ssml('[background](music.mp3 level: -3dB)')
   # → <audio src="music.mp3" soundLevel="-3dB"><desc>background</desc></audio>

Combining Attributes
^^^^^^^^^^^^^^^^^^^^

Multiple audio attributes can be combined with fallback text:

.. code-block:: python

   ssmd.to_ssml('[bg music](music.mp3 clip: 0s-10s, speed: 120%, level: -3dB Fallback text)')
   # → <audio src="music.mp3" clipBegin="0s" clipEnd="10s" speed="120%" soundLevel="-3dB">
   #    <desc>bg music</desc>Fallback text</audio>

   ssmd.to_ssml('[effect](sound.mp3 clip: 2s-5s, repeat: 2 Sound unavailable)')
   # → <audio src="sound.mp3" clipBegin="2s" clipEnd="5s" repeatCount="2">
   #    <desc>effect</desc>Sound unavailable</audio>

.. note::
   Audio attribute support varies by TTS platform. Amazon Polly and Google Cloud TTS
   support most of these features. Always test with your specific TTS engine.

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

Platform-specific extensions allow you to use TTS features beyond standard SSML.

Amazon Polly Extensions
~~~~~~~~~~~~~~~~~~~~~~~~

Amazon Polly provides effects like whispering and dynamic range compression:

.. code-block:: python

   # Whisper effect
   ssmd.to_ssml('[secret message](ext: whisper)')
   # → <amazon:effect name="whispered">secret message</amazon:effect>

   # Dynamic range compression (for voice over music)
   ssmd.to_ssml('[announcement](ext: drc)')
   # → <amazon:effect name="drc">announcement</amazon:effect>

Google Cloud TTS Speaking Styles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Google Cloud TTS supports speaking styles for Neural2 and Studio voices. You can
configure these using SSMD's extension system:

.. code-block:: python

   from ssmd import Document

   # Configure Google TTS styles as extensions
   doc = Document(config={
       'extensions': {
           'cheerful': lambda text: f'<google:style name="cheerful">{text}</google:style>',
           'calm': lambda text: f'<google:style name="calm">{text}</google:style>',
           'empathetic': lambda text: f'<google:style name="empathetic">{text}</google:style>',
           'apologetic': lambda text: f'<google:style name="apologetic">{text}</google:style>',
           'firm': lambda text: f'<google:style name="firm">{text}</google:style>',
       }
   })

   # Use styles in your content
   doc.add_sentence("[Welcome to our service!](ext: cheerful)")
   doc.add_sentence("[We apologize for the inconvenience.](ext: apologetic)")
   doc.add_sentence("[Please remain calm.](ext: calm)")

   ssml = doc.to_ssml()
   # → <speak>
   #    <google:style name="cheerful">Welcome to our service!</google:style>
   #    <google:style name="apologetic">We apologize for the inconvenience.</google:style>
   #    <google:style name="calm">Please remain calm.</google:style>
   #    </speak>

Available Google TTS speaking styles:

* ``cheerful`` - Upbeat and positive tone
* ``calm`` - Relaxed and soothing tone
* ``empathetic`` - Understanding and compassionate tone
* ``apologetic`` - Sorry and regretful tone
* ``firm`` - Confident and authoritative tone
* ``news`` - Professional news anchor tone (some voices)
* ``conversational`` - Natural conversation tone (some voices)

.. note::
   Google TTS speaking styles are only supported by specific Neural2 and Studio voices.
   See the `Google Cloud TTS documentation <https://cloud.google.com/text-to-speech/docs/speaking-styles>`_
   for voice compatibility.

Custom Extensions
~~~~~~~~~~~~~~~~~

You can define your own extensions for any custom SSML tags your TTS platform supports:

.. code-block:: python

   from ssmd import Document

   doc = Document(config={
       'extensions': {
           'robotic': lambda text: f'<voice-transformation type="robot">{text}</voice-transformation>',
           'echo': lambda text: f'<audio-effect type="echo">{text}</audio-effect>',
       }
   })

   doc.add_sentence("[Hello](ext: robotic)")
   doc.add_sentence("[world](ext: echo)")

For a complete Google TTS styles example, see ``examples/google_tts_styles.py``.

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

Security
~~~~~~~~

All user input is automatically sanitized to prevent XML injection attacks. Special
characters in both text content and annotation parameters are properly escaped:

.. code-block:: python

   # Malicious input is safely escaped
   ssmd.to_ssml('[text](sub: value"><script>alert(1)</script>)')
   # → <speak><sub alias="value&quot;&gt;&lt;script&gt;alert(1)&lt;/script&gt;">text</sub></speak>

The library ensures:

- **XML validity**: Output is always valid, well-formed XML
- **Injection prevention**: User input cannot break out of attribute values or inject tags
- **Automatic escaping**: All special characters (``<``, ``>``, ``&``, ``"``, ``'``) are escaped

You can safely use SSMD with untrusted user input in TTS applications.

Literal Asterisks
~~~~~~~~~~~~~~~~~

To include literal asterisks without emphasis, escape them or use different patterns:

.. code-block:: python

   # These won't be treated as emphasis
   ssmd.to_ssml('2 * 3 = 6')
   # → <speak>2 * 3 = 6</speak>

   ssmd.to_ssml('* list item')
   # → <speak>* list item</speak>
