# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python CLI tools and MCP server for PDF OCR processing and audio transcription using the Mistral AI API. Supports batch processing, cost tracking, and multilingual documents (Arabic/English).

**Available interfaces:**
- **CLI Tools**: Standalone command-line scripts for direct use
- **MCP Server**: FastMCP-based server exposing OCR capabilities to Claude Desktop and other MCP clients

## Setup

```bash
pip install -r requirements.txt
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

### PDF with Image Extraction
```bash
python pdf_to_txt_with_images.py document.pdf   # Extracts embedded images as separate PNG files
python pdf_to_txt_with_images.py ./pdfs --track-file log.csv --track-format csv
```

### PDF with Validation
```bash
python pdf_to_txt_with_validation.py document.pdf  # Includes OCR output validation warnings
```

### Audio Transcription
```bash
python transcribe_audio.py audio.ogg            # Supports .ogg, .mp3, .wav, .m4a, .flac
```

## Architecture

Five standalone CLI scripts with shared patterns:

| Script | Purpose | Key Features |
|--------|---------|--------------|
| `pdf_to_txt.py` | Basic single-file PDF→markdown | Minimal, no tracking |
| `pdf_to_txt_new.py` | Advanced PDF processing | Batch mode, skip logic, --txt flag, --clean for markdown |
| `pdf_to_txt_with_images.py` | PDF with image extraction | Saves embedded images, cost tracking CSV |
| `pdf_to_txt_with_validation.py` | PDF with output validation | Detects OCR issues (empty output, formatting quirks) |
| `transcribe_audio.py` | Audio→text | Uses Voxtral model |

### Shared Patterns

- All scripts use `python-dotenv` to load `MISTRAL_API_KEY` from `.env`
- PDF scripts use `Mistral.files.upload()` → `get_signed_url()` → `ocr.process()` workflow
- Output files are written to the same directory as input files
- Batch processing skips PDFs that already have corresponding `.md`/`.txt` files

### Markdown Cleaning (pdf_to_txt_new.py)

Use `--clean` flag with `--md` to clean repetitive elements from academic papers:

- **احتفاظ (Preserves)**: Page numbers (صفحة، ص، Page), journal titles, footnotes, DOI references
- **حذف (Removes)**: Repetitive author names, journal names repeated on every page, duplicate institutional headers
- Uses `markdowncleaner` package ([github.com/josk0/markdowncleaner](https://github.com/josk0/markdowncleaner)) with custom Arabic/English academic paper configuration
- Only works with markdown output (`--md` flag required)

**Cleaning Settings Used**:
- `min_line_length = 30` - Preserves Arabic text and page numbers
- `remove_duplicate_headlines = True` - Removes repetitive headers (threshold: 2+ occurrences)
- `remove_footnotes_in_text = False` - Preserves footnotes as requested
- `fix_encoding_mojibake = True` - Fixes Arabic text encoding issues
- `crimp_linebreaks = True` - Fixes PDF conversion line break errors
- `remove_references_heuristically = False` - Preserves reference sections

### Cost Tracking (pdf_to_txt_with_images.py, pdf_to_txt_with_validation.py)

- Creates `ocr_usage_tracking.csv` next to the script
- Tracks: filename, page_count, processing_date, cost_usd, output_path
- Cost: $0.001 per page

## MCP Server (mistral_ocr_mcp.py)

FastMCP-based server that exposes PDF OCR capabilities through the Model Context Protocol.

### Available Tools

| Tool Name | Description | Key Parameters |
|-----------|-------------|----------------|
| `mistral_ocr_process_pdf` | Process local PDF file | `file_path`, `output_format`, `pages`, `clean_output`, `return_content` |
| `mistral_ocr_process_url` | Download and process PDF from URL | `url`, `output_format`, `pages`, `keep_pdf`, `return_content` |
| `mistral_ocr_clean_markdown` | Clean repetitive content from markdown | `content`, `config_path` |

### Configuration

Add to your MCP client config (e.g., Claude Desktop's `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "mistral_ocr_mcp": {
      "type": "stdio",
      "command": "python",
      "args": ["C:\\path\\to\\mistral-ocr\\mistral_ocr_mcp.py"],
      "env": {
        "MISTRAL_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Return Content Parameter

Both `process_pdf` and `process_url` tools support a `return_content` parameter:

- **`return_content: true` (default)**: Full content included in JSON response
  - Best for: Small PDFs, immediate analysis, direct API usage
  - Example response: `{"success": true, "content": "# Full text...", "output_file": "..."}`

- **`return_content: false`**: Only metadata returned, content saved to file
  - Best for: Large PDFs (hundreds of pages), reducing response size, smithery.ai publishing
  - Example response: `{"success": true, "content": null, "output_file": "/path/to/output.txt"}`
  - File is still created - use `output_file` path to read content separately

### Tool Annotations

All tools include MCP annotations for optimal client behavior:
- `readOnlyHint`: Indicates if tool modifies system state
- `idempotentHint: true`: All tools are idempotent (same input → same output)
- `openWorldHint`: Indicates if tool interacts with external services

### Response Format

All tools return JSON with consistent structure:
```json
{
  "success": true,
  "content": "extracted text or null",
  "page_count": 10,
  "pages_processed": [1, 2, 3],
  "output_file": "/path/to/output.txt",
  "cost_usd": 0.01,
  "format": "text|markdown",
  "cleaned": false,
  "warnings": []
}
```

### Running the Server

**Development/Testing:**
```bash
python mistral_ocr_mcp.py  # Starts server in stdio mode
```

**With MCP Inspector (debugging):**
```bash
npx @modelcontextprotocol/inspector python mistral_ocr_mcp.py
```

## Environment

- Python 3.8+
- Requires `MISTRAL_API_KEY` in environment or `.env` file
- Get API key from: https://console.mistral.ai/api-keys
- Dependencies: `mistralai`, `python-dotenv`, `mcp`, `markdowncleaner` (optional)
