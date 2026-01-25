# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python CLI tools for PDF OCR processing and audio transcription using the Mistral AI API. Supports batch processing, cost tracking, and multilingual documents (Arabic/English).

**Note:** The MCP server has been split to a separate project: `mistral-mcp`

## Setup

```bash
# Using uv
uv sync

# Or using pip
pip install -e .

# Then configure API key
cp .env.example .env  # Add your MISTRAL_API_KEY
```

## Commands

### PDF to Markdown (recommended for most use cases)
```bash
python pdf_to_txt_new.py document.pdf           # Single file → .md
python pdf_to_txt_new.py document.pdf --txt     # Single file → .txt
python pdf_to_txt_new.py document.pdf --md --clean  # Clean repetitive headers
python pdf_to_txt_new.py ./documents/           # Batch process directory (recursive)
```

### Audio Transcription
```bash
python transcribe_audio.py audio.ogg            # Supports .ogg, .mp3, .wav, .m4a, .flac
```

## Architecture

Two main CLI scripts with shared patterns:

| Script | CLI Command | Purpose | Key Features |
|--------|-------------|---------|--------------|
| `pdf_to_txt_new.py` | `pdf-to-txt` | Advanced PDF processing | Batch mode, skip logic, --txt flag, --clean for markdown |
| `transcribe_audio.py` | `transcribe-audio` | Audio→text | Uses Voxtral model |

### Shared Patterns

- All scripts use `python-dotenv` to load `MISTRAL_API_KEY` from `.env`
- PDF scripts use `Mistral.files.upload()` → `get_signed_url()` → `ocr.process()` workflow
- Output files are written to the same directory as input files
- Batch processing skips PDFs that already have corresponding `.md`/`.txt` files

### Markdown Cleaning (pdf_to_txt_new.py)

Use `--clean` flag with `--md` to clean repetitive elements from academic papers:

- **احتفاظ (Preserves)**: Page numbers (صفحة، ص، Page), journal titles, footnotes, DOI references
- **حذف (Removes)**: Repetitive author names, journal names repeated on every page, duplicate institutional headers
- Uses `markdowncleaner` package with custom Arabic/English academic paper configuration
- Only works with markdown output (`--md` flag required)

**Cleaning Settings Used** (in `markdowncleaner_config.yaml`):
- `min_line_length = 30` - Preserves Arabic text and page numbers
- `remove_duplicate_headlines = True` - Removes repetitive headers (threshold: 2+ occurrences)
- `remove_footnotes_in_text = False` - Preserves footnotes as requested
- `fix_encoding_mojibake = True` - Fixes Arabic text encoding issues
- `crimp_linebreaks = True` - Fixes PDF conversion line break errors
- `remove_references_heuristically = False` - Preserves reference sections

## Environment

- Python 3.13+
- Requires `MISTRAL_API_KEY` in environment or `.env` file
- Get API key from: https://console.mistral.ai/api-keys
- Dependencies: `mistralai`, `python-dotenv`, `markdowncleaner`

## Related Projects

- **mistral-mcp**: MCP server for PDF OCR (separate repository)
