Examples
========

This page provides practical examples of using SSMD in real-world scenarios.

Basic TTS Integration
----------------------

pyttsx3 (Offline TTS)
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pyttsx3
   from ssmd import SSMD

   # Initialize TTS engine
   engine = pyttsx3.init()

   # Create SSMD parser with pyttsx3 capabilities
   parser = SSMD(capabilities='pyttsx3')

   # Create content with SSMD
   text = """
   # Welcome Message
   *Hello* and welcome!
   Please ...500ms listen carefully.
   This is >>very fast>>.
   """

   # Convert to SSML
   ssml = parser.to_ssml(text)

   # Speak (pyttsx3 handles SSML natively)
   engine.say(ssml)
   engine.runAndWait()

Google Text-to-Speech
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from google.cloud import texttospeech
   from ssmd import SSMD

   # Initialize Google TTS client
   client = texttospeech.TextToSpeechClient()

   # Create SSMD parser with Google capabilities
   parser = SSMD(capabilities='google')

   # Create content
   text = """
   *Welcome* to our service.
   [Bonjour](fr) to our French users!
   Please wait ...1s for the next message.
   """

   # Convert to SSML
   ssml = parser.to_ssml(text)

   # Prepare TTS request
   synthesis_input = texttospeech.SynthesisInput(ssml=ssml)
   voice = texttospeech.VoiceSelectionParams(
       language_code="en-US",
       name="en-US-Neural2-J"
   )
   audio_config = texttospeech.AudioConfig(
       audio_encoding=texttospeech.AudioEncoding.MP3
   )

   # Generate speech
   response = client.synthesize_speech(
       input=synthesis_input,
       voice=voice,
       audio_config=audio_config
   )

   # Save to file
   with open("output.mp3", "wb") as f:
       f.write(response.audio_content)

Amazon Polly
~~~~~~~~~~~~

.. code-block:: python

   import boto3
   from ssmd import SSMD

   # Initialize Polly client
   polly = boto3.client('polly')

   # Create SSMD parser with Polly capabilities
   parser = SSMD(capabilities='polly')

   # Create content with Amazon extensions
   text = """
   *Welcome* to our podcast.
   Now for the [secret message](ext: whisper).
   Back to normal voice.
   """

   # Convert to SSML
   ssml = parser.to_ssml(text)

   # Generate speech
   response = polly.synthesize_speech(
       Text=ssml,
       TextType='ssml',
       OutputFormat='mp3',
       VoiceId='Joanna'
   )

   # Save audio
   with open('output.mp3', 'wb') as f:
       f.write(response['AudioStream'].read())

Streaming TTS
-------------

Sentence-by-Sentence Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ssmd import SSMD
   import time

   # Mock TTS engine for demonstration
   class TTSEngine:
       def speak(self, ssml):
           print(f"Speaking: {ssml}")
           time.sleep(0.5)  # Simulate speech duration

   engine = TTSEngine()
   parser = SSMD({'auto_sentence_tags': True})

   # Long document
   document = """
   # Chapter 1: The Beginning

   It was a dark and stormy night.
   The rain fell in torrents.
   Lightning flashed across the sky.

   # Chapter 2: The Discovery

   Suddenly, a sound echoed through the halls.
   What could it be?
   """

   # Load and stream sentences
   doc = parser.load(document)

   print(f"Total sentences: {len(doc)}")

   for i, sentence in enumerate(doc, 1):
       print(f"\n[{i}/{len(doc)}]")
       engine.speak(sentence)

   print("\nPlayback complete!")

Async TTS Streaming
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from ssmd import SSMD

   class AsyncTTSEngine:
       async def speak(self, ssml):
           print(f"Speaking: {ssml[:50]}...")
           await asyncio.sleep(0.5)
           print("Done")

   async def stream_document(doc):
       engine = AsyncTTSEngine()

       for i, sentence in enumerate(doc, 1):
           print(f"\n[Sentence {i}/{len(doc)}]")
           await engine.speak(sentence)

   async def main():
       parser = SSMD({'auto_sentence_tags': True})

       text = """
       Welcome to async TTS.
       Each sentence is processed independently.
       This allows for smooth streaming.
       """

       doc = parser.load(text)
       await stream_document(doc)

   # Run
   asyncio.run(main())

Interactive Story Reader
------------------------

.. code-block:: python

   from ssmd import SSMD
   import pyttsx3

   class StoryReader:
       def __init__(self, tts_engine='pyttsx3'):
           self.parser = SSMD({
               'capabilities': tts_engine,
               'auto_sentence_tags': True,
           })
           self.engine = pyttsx3.init()
           self.current_doc = None
           self.current_index = 0

       def load_story(self, ssmd_text):
           """Load a story from SSMD text."""
           self.current_doc = self.parser.load(ssmd_text)
           self.current_index = 0

       def play(self):
           """Play from current position."""
           if not self.current_doc:
               print("No story loaded")
               return

           while self.current_index < len(self.current_doc):
               sentence = self.current_doc[self.current_index]
               print(f"\n[{self.current_index + 1}/{len(self.current_doc)}]")

               self.engine.say(sentence)
               self.engine.runAndWait()

               self.current_index += 1

               # Interactive control
               cmd = input("(n)ext, (p)rev, (q)uit: ").lower()
               if cmd == 'q':
                   break
               elif cmd == 'p' and self.current_index > 0:
                   self.current_index -= 2  # Go back two, play one forward

       def get_progress(self):
           """Get reading progress."""
           if not self.current_doc:
               return 0
           return (self.current_index / len(self.current_doc)) * 100

   # Usage
   story = """
   # The Adventure Begins

   [Once upon a time](v: 2, r: 2), in a land far away.
   There lived a brave *knight* named Sir Galahad.
   He faced many challenges ...1s but never gave up.

   # The Quest

   One day, the king summoned him.
   ++Go forth++ said the king, ++and save our kingdom++!
   """

   reader = StoryReader()
   reader.load_story(story)
   reader.play()

Content Management System
--------------------------

SSMD CMS with Database
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ssmd import SSMD
   import sqlite3
   from datetime import datetime

   class SSMDContentManager:
       def __init__(self, db_path='content.db'):
           self.db = sqlite3.connect(db_path)
           self.parser = SSMD()
           self._setup_db()

       def _setup_db(self):
           self.db.execute('''
               CREATE TABLE IF NOT EXISTS content (
                   id INTEGER PRIMARY KEY,
                   title TEXT,
                   ssmd_text TEXT,
                   ssml_cache TEXT,
                   created_at TIMESTAMP,
                   updated_at TIMESTAMP
               )
           ''')
           self.db.commit()

       def create(self, title, ssmd_text):
           """Create new content."""
           ssml = self.parser.to_ssml(ssmd_text)
           now = datetime.now()

           self.db.execute('''
               INSERT INTO content (title, ssmd_text, ssml_cache, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?)
           ''', (title, ssmd_text, ssml, now, now))

           self.db.commit()

       def update(self, content_id, ssmd_text):
           """Update existing content."""
           ssml = self.parser.to_ssml(ssmd_text)
           now = datetime.now()

           self.db.execute('''
               UPDATE content
               SET ssmd_text = ?, ssml_cache = ?, updated_at = ?
               WHERE id = ?
           ''', (ssmd_text, ssml, now, content_id))

           self.db.commit()

       def get_ssml(self, content_id):
           """Get cached SSML for content."""
           cursor = self.db.execute(
               'SELECT ssml_cache FROM content WHERE id = ?',
               (content_id,)
           )
           row = cursor.fetchone()
           return row[0] if row else None

       def get_ssmd(self, content_id):
           """Get SSMD source."""
           cursor = self.db.execute(
               'SELECT ssmd_text FROM content WHERE id = ?',
               (content_id,)
           )
           row = cursor.fetchone()
           return row[0] if row else None

   # Usage
   cms = SSMDContentManager()

   # Create content
   cms.create("Welcome Message", """
   # Welcome to Our Service
   *Thank you* for joining us today!
   """)

   # Get SSML for TTS
   ssml = cms.get_ssml(1)
   print(ssml)

Multi-Language Support
----------------------

Language-Aware TTS
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ssmd import SSMD

   class MultilingualTTS:
       def __init__(self):
           self.parser = SSMD(capabilities='google')

       def create_multilingual_content(self, messages):
           """Create content with multiple languages."""
           parts = []

           for lang, text in messages:
               if lang == 'en':
                   parts.append(text)
               else:
                   parts.append(f"[{text}]({lang})")

           return " ".join(parts)

       def speak_multilingual(self, messages):
           ssmd_text = self.create_multilingual_content(messages)
           ssml = self.parser.to_ssml(ssmd_text)
           return ssml

   # Usage
   tts = MultilingualTTS()

   messages = [
       ('en', '*Welcome* to our global service.'),
       ('fr', 'Bienvenue à notre service mondial.'),
       ('de', 'Willkommen zu unserem globalen Service.'),
       ('es', 'Bienvenido a nuestro servicio global.'),
   ]

   ssml = tts.speak_multilingual(messages)
   print(ssml)

Podcast Generator
-----------------

.. code-block:: python

   from ssmd import SSMD
   from pathlib import Path

   class PodcastGenerator:
       def __init__(self, output_dir='podcasts'):
           self.parser = SSMD({
               'capabilities': 'polly',
               'auto_sentence_tags': True,
               'pretty_print': True,
           })
           self.output_dir = Path(output_dir)
           self.output_dir.mkdir(exist_ok=True)

       def generate_episode(self, episode_number, script):
           """Generate podcast episode."""
           # Add production elements
           enhanced_script = f"""
           # Episode {episode_number}

           [Podcast intro music](@intro_music.mp3)

           ...1s

           {script}

           ...2s

           [Outro music](@outro_music.mp3)
           """

           # Convert to SSML
           ssml = self.parser.to_ssml(enhanced_script)

           # Save SSML
           output_file = self.output_dir / f"episode_{episode_number}.ssml"
           output_file.write_text(ssml)

           return output_file

   # Usage
   podcast = PodcastGenerator()

   script = """
   *Welcome* to Tech Talks!
   Today we're discussing artificial intelligence.

   Our guest is Dr. Smith, an expert in machine learning.
   [Welcome to the show](v: 4), Doctor Smith!

   ...500ms

   Thank you for having me.
   """

   ssml_file = podcast.generate_episode(42, script)
   print(f"Generated: {ssml_file}")

Testing and Validation
-----------------------

SSMD Linter
~~~~~~~~~~~

.. code-block:: python

   from ssmd import SSMD

   class SSMDLinter:
       def __init__(self):
           self.parser = SSMD()

       def lint(self, ssmd_text):
           """Validate SSMD and provide feedback."""
           issues = []

           # Try to convert
           try:
               ssml = self.parser.to_ssml(ssmd_text)
           except Exception as e:
               issues.append(f"Conversion error: {e}")
               return issues

           # Check for common issues
           if '*' in ssmd_text and '**' not in ssmd_text:
               if ssmd_text.count('*') % 2 != 0:
                   issues.append("Unmatched asterisks for emphasis")

           # Check for very long pauses
           if '...10s' in ssmd_text or '...10000ms' in ssmd_text:
               issues.append("Warning: Very long pause detected")

           # Success
           if not issues:
               issues.append("✓ No issues found")

           return issues

   # Usage
   linter = SSMDLinter()

   text = """
   *Hello world
   This has an unclosed emphasis tag.
   """

   issues = linter.lint(text)
   for issue in issues:
       print(issue)

Complete Application Example
-----------------------------

Voice Assistant with SSMD
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ssmd import SSMD
   import random

   class VoiceAssistant:
       def __init__(self, name="Assistant", tts_engine='google'):
           self.name = name
           self.parser = SSMD(capabilities=tts_engine)

       def greet(self, user_name=None):
           greetings = [
               "*Hello*!",
               "Good day!",
               "*Welcome* back!",
           ]

           greeting = random.choice(greetings)

           if user_name:
               message = f"{greeting} {user_name}."
           else:
               message = greeting

           return self.parser.to_ssml(message)

       def error(self, message):
           return self.parser.to_ssml(f"--Sorry-- ...300ms {message}")

       def success(self, message):
           return self.parser.to_ssml(f"*Great*! {message}")

       def thinking(self):
           return self.parser.to_ssml("...500ms Let me think ...500ms")

       def announce(self, title, message):
           ssmd = f"""
           # {title}

           ...300ms

           {message}
           """
           return self.parser.to_ssml(ssmd)

   # Usage
   assistant = VoiceAssistant(name="Jarvis")

   print(assistant.greet("John"))
   print(assistant.thinking())
   print(assistant.success("Task completed successfully"))
   print(assistant.error("I couldn't find that file"))
   print(assistant.announce("Weather Update", "It's sunny with a high of 72 degrees"))

See Also
--------

* Check the `examples/` directory in the repository for more runnable examples
* Visit :doc:`api` for complete API documentation
* See :doc:`capabilities` for TTS engine integration details
