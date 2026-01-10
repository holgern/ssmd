[![PyPI - Version](https://img.shields.io/pypi/v/ssmd)](https://pypi.org/project/ssmd/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ssmd)
![PyPI - Downloads](https://img.shields.io/pypi/dm/ssmd)
[![codecov](https://codecov.io/gh/holgern/ssmd/graph/badge.svg?token=iCHXwbjAXG)](https://codecov.io/gh/holgern/ssmd)

# SSMD - Speech Synthesis Markdown

**SSMD** (Speech Synthesis Markdown) is a lightweight Python library that provides a
human-friendly markdown-like syntax for creating SSML (Speech Synthesis Markup Language)
documents. It's designed to make TTS (Text-to-Speech) content more readable and
maintainable.

## Features

✨ **Markdown-like syntax** - More intuitive than raw SSML 🎯 **Full SSML support** -
All major SSML features covered 🔄 **Bidirectional** - Convert SSMD↔SSML or strip to
plain text 📝 **Document-centric** - Build, edit, and export TTS documents 🎛️ **TTS
capabilities** - Auto-filter features based on engine support 🎨 **Extensible** - Custom
extensions for platform-specific features 🧪 **Spec-driven** - Follows the official SSMD
specification

## Installation

```bash
pip install ssmd
```

Or install from source:

```bash
git clone https://github.com/holgern/ssmd.git
cd ssmd
pip install -e .
```

## Quick Start

### Basic Usage

```python
import ssmd

# Convert SSMD to SSML
ssml = ssmd.to_ssml("Hello *world*!")
print(ssml)
# Output: <speak>Hello <emphasis>world</emphasis>!</speak>

# Strip SSMD markup for plain text
plain = ssmd.to_text("Hello *world* @marker!")
print(plain)
# Output: Hello world!

# Convert SSML back to SSMD
ssmd_text = ssmd.from_ssml('<speak><emphasis>Hello</emphasis></speak>')
print(ssmd_text)
# Output: *Hello*
```

### Document API - Build TTS Content Incrementally

```python
from ssmd import Document

# Create a document and build it piece by piece
doc = Document()
doc.add_sentence("Hello and *welcome* to SSMD!")
doc.add_sentence("This is a great tool for TTS.")
doc.add_paragraph("Let's start a new paragraph here.")

# Export to different formats
ssml = doc.to_ssml()      # SSML output
markdown = doc.to_ssmd()  # SSMD markdown
text = doc.to_text()      # Plain text

# Access document content
print(doc.ssmd)           # Raw SSMD content
print(len(doc))           # Number of sentences
```

### TTS Streaming Integration

Perfect for streaming TTS where you process sentences one at a time:

```python
from ssmd import Document

# Create document with configuration
doc = Document(
    config={'auto_sentence_tags': True},
    capabilities='pyttsx3'  # Auto-filter for pyttsx3 support
)

# Build the document
doc.add_paragraph("# Chapter 1: Introduction")
doc.add_sentence("Welcome to the *amazing* world of SSMD!")
doc.add_sentence("This makes TTS content much easier to write.")
doc.add_paragraph("# Chapter 2: Features")
doc.add_sentence("You can use all kinds of markup.")
doc.add_sentence("Including ...500ms pauses and [special pronunciations](ph: speSl).")

# Iterate through sentences for TTS
for i, sentence in enumerate(doc.sentences(), 1):
    print(f"Sentence {i}: {sentence}")
    # Your TTS engine here:
    # tts_engine.speak(sentence)
    # await tts_engine.wait_until_done()

# Or access specific sentences
print(f"Total sentences: {len(doc)}")
print(f"First sentence: {doc[0]}")
print(f"Last sentence: {doc[-1]}")
```

### Document Editing

```python
from ssmd import Document

# Load from existing content
doc = Document("First sentence. Second sentence. Third sentence.")

# Edit like a list
doc[0] = "Modified first sentence."
del doc[1]  # Remove second sentence

# String operations
doc.replace("sentence", "line")

# Merge documents
doc2 = Document("Additional content.")
doc.merge(doc2)

# Split into individual sentences
sentences = doc.split()  # Returns list of Document objects
```

### TTS Engine Capabilities

SSMD can automatically filter SSML features based on your TTS engine's capabilities.
This ensures compatibility by stripping unsupported tags to plain text.

#### Using Presets

```python
from ssmd import Document

# Use a preset for your TTS engine
doc = Document("*Hello* [world](en)!", capabilities='pyttsx3')
ssml = doc.to_ssml()

# pyttsx3 doesn't support emphasis or language tags, so they're stripped:
# <speak>Hello world!</speak>
```

**Available Presets:**

- `minimal` - Plain text only (no SSML)
- `pyttsx3` - Minimal support (basic prosody only)
- `espeak` - Moderate support (breaks, language, prosody, phonemes)
- `google` / `azure` / `microsoft` - Full SSML support
- `polly` / `amazon` - Full support + Amazon extensions (whisper, DRC)
- `full` - All features enabled

#### Custom Capabilities

```python
from ssmd import Document, TTSCapabilities

# Define exactly what your TTS supports
caps = TTSCapabilities(
    emphasis=False,      # No <emphasis> support
    break_tags=True,     # Supports <break>
    paragraph=True,      # Supports <p>
    language=False,      # No language switching
    prosody=True,        # Supports volume/rate/pitch
    say_as=False,        # No <say-as>
    audio=False,         # No audio files
    mark=False,          # No markers
)

doc = Document("*Hello* world!", capabilities=caps)
```

#### Capability-Aware Streaming

```python
from ssmd import Document

# Create document for specific TTS engine
doc = Document(capabilities='espeak')

# Build content with various features
doc.add_paragraph("# Welcome")
doc.add_sentence("*Hello* world!")
doc.add_sentence("[Bonjour](fr) everyone!")

# All sentences are filtered for eSpeak compatibility
for sentence in doc.sentences():
    # Features eSpeak doesn't support are automatically removed
    tts_engine.speak(sentence)
```

**Comparison of Engine Outputs:**

Same input: `*Hello* world... [this is loud](v: 5)!`

| Engine  | Output                                                                                                                          |
| ------- | ------------------------------------------------------------------------------------------------------------------------------- |
| minimal | `<speak>Hello world... this is loud!</speak>`                                                                                   |
| pyttsx3 | `<speak>Hello world... <prosody volume="x-loud">this is loud</prosody>!</speak>`                                                |
| espeak  | `<speak>Hello world<break time="1000ms"/> <prosody volume="x-loud">this is loud</prosody>!</speak>`                             |
| google  | `<speak><p><emphasis>Hello</emphasis> world<break time="1000ms"/> <prosody volume="x-loud">this is loud</prosody>!</p></speak>` |

See `examples/tts_with_capabilities.py` for a complete demonstration.

## SSMD Syntax Reference

### Text & Emphasis

```python
# Emphasis
ssmd.to_ssml("*emphasized text*")
# → <speak><emphasis>emphasized text</emphasis></speak>
```

### Breaks & Pauses

```python
# Specific time (required - bare ... is preserved as ellipsis)
ssmd.to_ssml("Hello ...500ms world")
ssmd.to_ssml("Hello ...2s world")
ssmd.to_ssml("Hello ...1s world")

# Strength-based
ssmd.to_ssml("Hello ...n world")  # none
ssmd.to_ssml("Hello ...w world")  # weak (x-weak)
ssmd.to_ssml("Hello ...c world")  # comma (medium)
ssmd.to_ssml("Hello ...s world")  # sentence (strong)
ssmd.to_ssml("Hello ...p world")  # paragraph (x-strong)
```

### Paragraphs

```python
text = """First paragraph here.
Second line of first paragraph.

Second paragraph starts here."""

ssmd.to_ssml(text)
# → <speak><p>First paragraph here.
#    Second line of first paragraph.</p><p>Second paragraph starts here.</p></speak>
```

### Language

```python
# Auto-complete language codes
ssmd.to_ssml('[Bonjour](fr) world')
# → <speak><lang xml:lang="fr-FR">Bonjour</lang> world</speak>

# Explicit locale
ssmd.to_ssml('[Cheerio](en-GB)')
# → <speak><lang xml:lang="en-GB">Cheerio</lang></speak>
```

### Phonetic Pronunciation

```python
# X-SAMPA notation (converted to IPA automatically)
ssmd.to_ssml('[tomato](ph: t@meItoU)')

# Direct IPA
ssmd.to_ssml('[tomato](ipa: təˈmeɪtoʊ)')

# Output: <speak><phoneme alphabet="ipa" ph="təˈmeɪtoʊ">tomato</phoneme></speak>
```

### Prosody (Volume, Rate, Pitch)

#### Shorthand Notation

```python
# Volume
ssmd.to_ssml("~silent~")      # silent
ssmd.to_ssml("--whisper--")   # x-soft
ssmd.to_ssml("-soft-")        # soft
ssmd.to_ssml("+loud+")        # loud
ssmd.to_ssml("++very loud++") # x-loud

# Rate
ssmd.to_ssml("<<very slow<<")  # x-slow
ssmd.to_ssml("<slow<")         # slow
ssmd.to_ssml(">fast>")         # fast
ssmd.to_ssml(">>very fast>>")  # x-fast

# Pitch
ssmd.to_ssml("__very low__")   # x-low
ssmd.to_ssml("_low_")          # low
ssmd.to_ssml("^high^")         # high
ssmd.to_ssml("^^very high^^")  # x-high
```

#### Explicit Notation

```python
# Combined (volume, rate, pitch)
ssmd.to_ssml('[loud and fast](vrp: 555)')
# → <prosody volume="x-loud" rate="x-fast" pitch="x-high">loud and fast</prosody>

# Individual attributes
ssmd.to_ssml('[text](v: 5, r: 3, p: 1)')
# → <prosody volume="x-loud" rate="medium" pitch="x-low">text</prosody>

# Relative values
ssmd.to_ssml('[louder](v: +10dB)')
ssmd.to_ssml('[higher](p: +20%)')
```

### Substitution (Aliases)

```python
ssmd.to_ssml('[H2O](sub: water)')
# → <speak><sub alias="water">H2O</sub></speak>

ssmd.to_ssml('[AWS](sub: Amazon Web Services)')
# → <speak><sub alias="Amazon Web Services">AWS</sub></speak>
```

### Say-As

```python
# Telephone numbers
ssmd.to_ssml('[+1-555-0123](as: telephone)')

# Dates with format
ssmd.to_ssml('[31.12.2024](as: date, format: "dd.mm.yyyy")')

# Spell out
ssmd.to_ssml('[NASA](as: character)')

# Numbers
ssmd.to_ssml('[123](as: cardinal)')
ssmd.to_ssml('[1st](as: ordinal)')

# Expletives (beeped)
ssmd.to_ssml('[damn](as: expletive)')
```

### Audio Files

```python
# With description
ssmd.to_ssml('[doorbell](https://example.com/sounds/bell.mp3)')
# → <audio src="https://example.com/sounds/bell.mp3"><desc>doorbell</desc></audio>

# With fallback text
ssmd.to_ssml('[cat purring](cat.ogg Sound file not loaded)')
# → <audio src="cat.ogg"><desc>cat purring</desc>Sound file not loaded</audio>

# No description
ssmd.to_ssml('[](beep.mp3)')
# → <audio src="beep.mp3"></audio>
```

### Markers

```python
ssmd.to_ssml('I always wanted a @animal cat as a pet.')
# → <speak>I always wanted a <mark name="animal"/> cat as a pet.</speak>

# Markers are removed in plain text (with smart whitespace handling)
ssmd.to_text('word @marker word')
# → "word word" (not "word  word")
```

### Headings

```python
doc = Document(config={
    'heading_levels': {
        1: [('emphasis', 'strong'), ('pause', '300ms')],
        2: [('emphasis', 'moderate'), ('pause', '75ms')],
        3: [('prosody', {'rate': 'slow'}), ('pause', '50ms')],
    }
})

doc.add("""
# Chapter 1
## Section 1.1
### Subsection
""")

ssml = doc.to_ssml()
```

### Extensions (Platform-Specific)

```python
# Amazon Polly whisper effect
ssmd.to_ssml('[whispered text](ext: whisper)')
# → <speak><amazon:effect name="whispered">whispered text</amazon:effect></speak>

# Custom extensions
doc = Document(config={
    'extensions': {
        'custom': lambda text: f'<custom-tag>{text}</custom-tag>'
    }
})
```

## API Reference

### Module Functions

#### `ssmd.to_ssml(ssmd_text, **config)` → `str`

Convert SSMD markup to SSML.

**Parameters:**

- `ssmd_text` (str): SSMD markdown text
- `**config`: Optional configuration parameters

**Returns:** SSML string

#### `ssmd.to_text(ssmd_text, **config)` → `str`

Convert SSMD to plain text (strips all markup).

**Parameters:**

- `ssmd_text` (str): SSMD markdown text
- `**config`: Optional configuration parameters

**Returns:** Plain text string

#### `ssmd.from_ssml(ssml_text, **config)` → `str`

Convert SSML to SSMD format.

**Parameters:**

- `ssml_text` (str): SSML XML string
- `**config`: Optional configuration parameters

**Returns:** SSMD markdown string

### Document Class

#### `Document(content="", config=None, capabilities=None)`

Main document container for building and managing TTS content.

**Parameters:**

- `content` (str): Optional initial SSMD content
- `config` (dict): Configuration options
- `capabilities` (TTSCapabilities | str): TTS capabilities preset or object

**Building Methods:**

- `add(text)` → Add text without separator (returns self for chaining)
- `add_sentence(text)` → Add text with `\n` separator
- `add_paragraph(text)` → Add text with `\n\n` separator

**Export Methods:**

- `to_ssml()` → Export to SSML string
- `to_ssmd()` → Export to SSMD string
- `to_text()` → Export to plain text

**Class Methods:**

- `Document.from_ssml(ssml, **config)` → Create from SSML
- `Document.from_text(text, **config)` → Create from text

**Properties:**

- `ssmd` → Raw SSMD content
- `config` → Configuration dict
- `capabilities` → TTS capabilities

**List-like Interface:**

- `len(doc)` → Number of sentences
- `doc[i]` → Get sentence by index (SSML)
- `doc[i] = text` → Replace sentence
- `del doc[i]` → Delete sentence
- `doc += text` → Append content

**Iteration:**

- `sentences()` → Iterator yielding SSML sentences
- `sentences(as_documents=True)` → Iterator yielding Document objects

**Editing Methods:**

- `insert(index, text, separator="")` → Insert text at index
- `remove(index)` → Remove sentence
- `clear()` → Remove all content
- `replace(old, new, count=-1)` → Replace text

**Advanced Methods:**

- `merge(other_doc, separator="\n\n")` → Merge another document
- `split()` → Split into sentence Documents
- `get_fragment(index)` → Get raw fragment by index

## Real-World TTS Example

```python
import asyncio
from ssmd import Document

# Your TTS engine (example with pyttsx3, kokoro-tts, etc.)
class TTSEngine:
    async def speak(self, ssml: str):
        """Speak SSML text."""
        # Implementation depends on your TTS engine
        pass

    async def wait_until_done(self):
        """Wait for speech to complete."""
        pass

async def read_document(content: str, tts: TTSEngine):
    """Read an SSMD document sentence by sentence."""
    doc = Document(content, config={'auto_sentence_tags': True})

    print(f"Reading document with {len(doc)} sentences...")

    for i in range(len(doc)):
        sentence = doc[i]
        print(f"[{i+1}/{len(doc)}] Speaking...")
        await tts.speak(sentence)
        await tts.wait_until_done()

    print("Done!")

# Usage
document = """
# Welcome
Hello and *welcome* to our presentation!
Today we'll discuss some exciting topics.

# Topic 1
First ...500ms let's talk about SSMD.
It makes writing TTS content [much easier](v: 4, p: 4)!

# Conclusion
Thank you for listening @end_marker!
"""

# Run async
# await read_document(document, tts_engine)
```

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=ssmd --cov-report=html

# Run specific test file
pytest tests/test_basic.py -v
```

### Code Quality

```bash
# Format with ruff
ruff format ssmd/ tests/

# Lint
ruff check ssmd/ tests/

# Type check
mypy ssmd/
```

## Specification

This implementation follows the
[SSMD Specification](https://github.com/machisuji/ssmd/blob/master/SPECIFICATION.md)
with additional features inspired by the JavaScript implementation.

### Implemented Features

✅ Text ✅ Emphasis (`*text*`) ✅ Break (`...500ms`, `...2s`, `...n/w/c/s/p`) ✅
Language (`[text](en)`, `[text](en-GB)`) ✅ Mark (`@marker`) ✅ Paragraph (`\n\n`) ✅
Phoneme (`[text](ph: xsampa)`, `[text](ipa: ipa)`) ✅ Prosody shorthand (`++loud++`,
`>>fast>>`, `^^high^^`) ✅ Prosody explicit (`[text](vrp: 555)`, `[text](v: 5)`) ✅
Substitution (`[text](sub: alias)`) ✅ Say-as (`[text](as: telephone)`) ✅ Audio
(`[desc](url.mp3 alt)`) ✅ Headings (`# ## ###`) ✅ Extensions (`[text](ext: whisper)`)
✅ Auto-sentence tags (`<s>`) ✅ **SSML ↔ SSMD bidirectional conversion**

## Related Projects

- **[SSMD (Ruby)](https://github.com/machisuji/ssmd)** - Original reference
  implementation
- **[SSMD (JavaScript)](https://github.com/fabien88/ssmd)** - JavaScript implementation
- **[Speech Markdown](https://www.speechmarkdown.org/)** - Alternative specification

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Original SSMD specification by [machisuji](https://github.com/machisuji)
- JavaScript implementation by [fabien88](https://github.com/fabien88)
- X-SAMPA to IPA conversion table from the Ruby implementation

## Links

- **Homepage:** https://github.com/holgern/ssmd
- **PyPI:** https://pypi.org/project/ssmd/
- **Issues:** https://github.com/holgern/ssmd/issues
- **Documentation:** https://ssmd.readthedocs.io/
