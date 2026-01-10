# SSMD - Speech Synthesis Markdown

**SSMD** (Speech Synthesis Markdown) is a lightweight Python library that provides a
human-friendly markdown-like syntax for creating SSML (Speech Synthesis Markup Language)
documents. It's designed to make TTS (Text-to-Speech) content more readable and
maintainable.

## Features

✨ **Markdown-like syntax** - More intuitive than raw SSML 🎯 **Full SSML support** -
All major SSML features covered 🔄 **Bidirectional** - Convert SSMD→SSML or strip to
plain text 📝 **TTS streaming** - Iterate through sentences for real-time TTS 🎨
**Extensible** - Custom extensions for platform-specific features 🧪 **Spec-driven** -
Follows the official SSMD specification

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
plain = ssmd.strip_ssmd("Hello *world* @marker!")
print(plain)
# Output: Hello world!
```

### Advanced Usage with Configuration

```python
from ssmd import SSMD

# Create parser with custom config
parser = SSMD({
    'auto_sentence_tags': True,  # Wrap sentences in <s> tags
    'pretty_print': False,        # Compact output
    'heading_levels': {
        1: [('emphasis', 'strong'), ('pause', '300ms')]
    }
})

# Convert SSMD to SSML
ssml = parser.to_ssml("""
# Welcome
Hello *world*!
This is a test.
""")

print(ssml)
```

### TTS Streaming Integration

Perfect for streaming TTS where you process sentences one at a time:

```python
from ssmd import SSMD

# Load a long document
parser = SSMD({'auto_sentence_tags': True})
doc = parser.load("""
# Chapter 1: Introduction
Welcome to the *amazing* world of SSMD!
This makes TTS content much easier to write.

# Chapter 2: Features
You can use all kinds of markup.
Including ...500ms pauses and [special pronunciations](ph: speSl).
""")

# Iterate through sentences for TTS
for i, sentence in enumerate(doc, 1):
    print(f"Sentence {i}: {sentence}")
    # Your TTS engine here:
    # tts_engine.speak(sentence)
    # await tts_engine.wait_until_done()

# Or access specific sentences
print(f"Total sentences: {len(doc)}")
print(f"First sentence: {doc[0]}")

# Get full SSML or plain text
print(doc.ssml)        # Complete SSML document
print(doc.plain_text)  # Stripped plain text
```

## SSMD Syntax Reference

### Text & Emphasis

```python
# Emphasis
ssmd.to_ssml("*emphasized text*")
# → <speak><emphasis>emphasized text</emphasis></speak>
```

### Breaks & Pauses

```python
# Default break (1000ms)
ssmd.to_ssml("Hello ... world")

# Specific time
ssmd.to_ssml("Hello ...500ms world")
ssmd.to_ssml("Hello ...2s world")

# Strength-based
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
ssmd.strip_ssmd('word @marker word')
# → "word word" (not "word  word")
```

### Headings

```python
parser = SSMD({
    'heading_levels': {
        1: [('emphasis', 'strong'), ('pause', '300ms')],
        2: [('emphasis', 'moderate'), ('pause', '75ms')],
        3: [('prosody', {'rate': 'slow'}), ('pause', '50ms')],
    }
})

ssml = parser.to_ssml("""
# Chapter 1
## Section 1.1
### Subsection
""")
```

### Extensions (Platform-Specific)

```python
# Amazon Polly whisper effect
ssmd.to_ssml('[whispered text](ext: whisper)')
# → <speak><amazon:effect name="whispered">whispered text</amazon:effect></speak>

# Custom extensions
parser = SSMD({
    'extensions': {
        'custom': lambda text: f'<custom-tag>{text}</custom-tag>'
    }
})
```

## Configuration Options

```python
SSMD({
    # Processor control
    'skip': ['emphasis', 'mark'],           # Skip specific processors

    # Output formatting
    'output_speak_tag': True,                # Wrap in <speak> tags
    'pretty_print': False,                   # Pretty-print XML

    # Features
    'auto_sentence_tags': False,             # Auto-wrap sentences in <s>

    # Heading configuration
    'heading_levels': {
        1: [('emphasis', 'strong'), ('pause', '300ms')],
        # ... more levels
    },

    # Custom extensions
    'extensions': {
        'whisper': lambda text: f'<amazon:effect name="whispered">{text}</amazon:effect>',
        # ... more extensions
    }
})
```

## API Reference

### Functions

#### `ssmd.to_ssml(ssmd_text, **config)` → `str`

Convert SSMD markup to SSML.

**Parameters:**

- `ssmd_text` (str): SSMD markdown text
- `**config`: Optional configuration parameters

**Returns:** SSML string

#### `ssmd.strip_ssmd(ssmd_text, **config)` → `str`

Remove SSMD markup, returning plain text.

**Parameters:**

- `ssmd_text` (str): SSMD markdown text
- `**config`: Optional configuration parameters

**Returns:** Plain text string

### Classes

#### `SSMD(config=None)`

Main converter class with configuration support.

**Methods:**

- `to_ssml(ssmd_text)` → Convert to SSML
- `strip(ssmd_text)` → Strip to plain text
- `load(ssmd_text)` → Load as SSMDDocument for iteration
- `sentences(ssmd_text)` → Generator yielding sentences

#### `SSMDDocument`

Document container with sentence iteration support.

**Properties:**

- `ssml` → Full SSML output (lazy loaded)
- `plain_text` → Plain text with markup stripped

**Methods:**

- `sentences()` → Iterator yielding SSML sentences
- `get_sentence(index)` → Get specific sentence by index
- `__len__()` → Total number of sentences
- `__getitem__(index)` → Index access to sentences
- `__iter__()` → Make document iterable

## Real-World TTS Example

```python
import asyncio
from ssmd import SSMD

# Your TTS engine (example with pyttsx3, kokoro-tts, etc.)
class TTSEngine:
    async def speak(self, ssml: str):
        """Speak SSML text."""
        # Implementation depends on your TTS engine
        pass

    async def wait_until_done(self):
        """Wait for speech to complete."""
        pass

async def read_document(ssmd_text: str, tts: TTSEngine):
    """Read an SSMD document sentence by sentence."""
    parser = SSMD({'auto_sentence_tags': True})
    doc = parser.load(ssmd_text)

    print(f"Reading document with {len(doc)} sentences...")

    for i, sentence in enumerate(doc, 1):
        print(f"[{i}/{len(doc)}] Speaking...")
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

✅ Text ✅ Emphasis (`*text*`) ✅ Break (`...`, `...500ms`, `...c/s/p`) ✅ Language
(`[text](en)`, `[text](en-GB)`) ✅ Mark (`@marker`) ✅ Paragraph (`\n\n`) ✅ Phoneme
(`[text](ph: xsampa)`, `[text](ipa: ipa)`) ✅ Prosody shorthand (`++loud++`, `>>fast>>`,
`^^high^^`) ✅ Prosody explicit (`[text](vrp: 555)`, `[text](v: 5)`) ✅ Substitution
(`[text](sub: alias)`) ✅ Say-as (`[text](as: telephone)`) ✅ Audio
(`[desc](url.mp3 alt)`) ✅ Headings (`# ## ###`) ✅ Extensions (`[text](ext: whisper)`)
✅ Auto-sentence tags (`<s>`)

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
