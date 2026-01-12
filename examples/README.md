# SSMD Examples Directory

This directory contains example scripts demonstrating SSMD features.

## Quick Start

### Running the Examples

All Python scripts (`.py` files) are executable:

```bash
# From the SSMD root directory
cd /home/nahrstaedt/privat/ebook/ssmd

# Run any example:
python examples/parser_demo.py
python examples/story_reader_demo.py
python examples/sentence_paragraph_detection_demo.py
```

## Available Examples

### 1. Basic Examples

#### `parser_demo.py`

Demonstrates basic SSMD parsing features.

```bash
python examples/parser_demo.py
```

#### `story_reader_demo.py`

Shows how to use SSMD for audiobook/story reading.

```bash
python examples/story_reader_demo.py
```

#### `tts_container_demo.py`

Demonstrates TTS container usage.

```bash
python examples/tts_container_demo.py
```

#### `tts_with_capabilities.py`

Shows capability-based TTS filtering.

```bash
python examples/tts_with_capabilities.py
```

#### `google_tts_styles.py`

Google TTS style examples.

```bash
python examples/google_tts_styles.py
```

### 2. Advanced Examples

#### `sentence_paragraph_detection_demo.py`

**Comprehensive test of sentence and paragraph detection.**

```bash
python examples/sentence_paragraph_detection_demo.py
```

**What it does:**

- Creates complex text with 35 sentences, 12 paragraphs
- Tests: abbreviations, quotes, break markers, punctuation
- Generates properly formatted SSMD files with correct line breaks
- Generates detailed analysis markdown files

**Generates:**

- `complex_text_plain.ssmd` - Formatted plain SSMD
- `complex_text_with_breaks.ssmd` - Formatted SSMD with breaks
- `sentence_detection_plain.md` - Plain text analysis
- `sentence_detection_with_breaks.md` - SSMD breaks analysis

**Features tested:**

- ✅ Abbreviations (Dr., Mr., P.M., U.S., etc.)
- ✅ Quoted speech across sentences
- ✅ Paragraph breaks (double newlines)
- ✅ SSMD break markers (`...s`, `...w`, `...p`)
- ✅ Times, dates, and geographic names
- ✅ Proper SSMD formatting (each sentence on new line)

```

```
