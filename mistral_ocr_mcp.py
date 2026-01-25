#!/usr/bin/env python3
"""
MCP Server for PDF OCR using Mistral AI.

This server provides tools to convert PDF files to text/markdown using Mistral's OCR API.

Tools:
- mistral_ocr_process_pdf: Process a local PDF file
- mistral_ocr_process_url: Download and process PDF from URL
- mistral_ocr_clean_markdown: Clean repetitive content from markdown

Usage:
    python mistral_ocr_mcp.py

Configuration:
    Set MISTRAL_API_KEY environment variable or use .env file.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Literal, Optional
from urllib.parse import urlparse
from urllib.request import urlopen

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mistralai import DocumentURLChunk, Mistral
from pydantic import BaseModel, Field, field_validator, ConfigDict

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("mistral_ocr_mcp")

# Constants
DEFAULT_MODEL = "mistral-ocr-latest"

# Check for markdowncleaner availability
try:
    from markdowncleaner import MarkdownCleaner
    MARKDOWNCLEANER_AVAILABLE = True
except ImportError:
    MARKDOWNCLEANER_AVAILABLE = False


# =============================================================================
# Pydantic Input Models
# =============================================================================

class ProcessPdfInput(BaseModel):
    """Input model for PDF OCR processing."""
    model_config = ConfigDict(str_strip_whitespace=True)

    file_path: str = Field(
        ...,
        description="Absolute path to the PDF file to process"
    )
    output_format: Literal["markdown", "text"] = Field(
        default="text",
        description="Output format: 'markdown' preserves formatting, 'text' is plain text"
    )
    pages: Optional[str] = Field(
        default=None,
        description="Specific pages to process (e.g., '1,8,9,11-20'). If not specified, all pages are processed"
    )
    extract_header: bool = Field(
        default=True,
        description="Extract header content from PDF pages"
    )
    extract_footer: bool = Field(
        default=True,
        description="Extract footer content from PDF pages"
    )
    clean_output: bool = Field(
        default=False,
        description="Clean repetitive headers/footers from markdown output (only applies to markdown format)"
    )
    save_to_file: bool = Field(
        default=True,
        description="Save output to file alongside the PDF. If false, only returns content"
    )
    return_content: bool = Field(
        default=True,
        description="Return full content in JSON response. If False, only file path is returned (useful for large PDFs)"
    )

    @field_validator('file_path')
    @classmethod
    def validate_file_path(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("File path cannot be empty")
        return v.strip()


class ProcessUrlInput(BaseModel):
    """Input model for URL-based PDF processing."""
    model_config = ConfigDict(str_strip_whitespace=True)

    url: str = Field(
        ...,
        description="URL of the PDF file to download and process"
    )
    output_format: Literal["markdown", "text"] = Field(
        default="text",
        description="Output format: 'markdown' or 'text'"
    )
    pages: Optional[str] = Field(
        default=None,
        description="Specific pages to process (e.g., '1,8,9,11-20')"
    )
    extract_header: bool = Field(
        default=True,
        description="Extract header content from PDF pages"
    )
    extract_footer: bool = Field(
        default=True,
        description="Extract footer content from PDF pages"
    )
    clean_output: bool = Field(
        default=False,
        description="Clean repetitive content from markdown output"
    )
    keep_pdf: bool = Field(
        default=False,
        description="Keep the downloaded PDF file after processing"
    )
    output_dir: Optional[str] = Field(
        default=None,
        description="Directory to save output files. Defaults to current working directory"
    )
    return_content: bool = Field(
        default=True,
        description="Return full content in JSON response. If False, only file path is returned (useful for large PDFs)"
    )

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("URL cannot be empty")
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v.strip()


class CleanMarkdownInput(BaseModel):
    """Input model for markdown cleaning utility."""
    model_config = ConfigDict(str_strip_whitespace=True)

    content: str = Field(
        ...,
        description="Markdown content to clean",
        min_length=1
    )
    config_path: Optional[str] = Field(
        default=None,
        description="Path to custom markdowncleaner YAML config. Uses default config if not specified"
    )


# =============================================================================
# Core Utility Functions (extracted from pdf_to_txt_new.py)
# =============================================================================

def parse_page_spec(page_spec: str) -> set[int]:
    """Parse page specification string into a set of page numbers.

    Args:
        page_spec: String like "1,8,9,11-20" or "1-5,10"

    Returns:
        set[int]: Set of page numbers (1-indexed)
    """
    pages = set()
    parts = page_spec.split(',')

    for part in parts:
        part = part.strip()
        if '-' in part:
            if part.startswith('-'):
                raise ValueError(f"Page numbers must be positive (got '{part}')")
            range_parts = part.split('-')
            if len(range_parts) != 2:
                raise ValueError(f"Invalid page range format: '{part}' (expected format: '11-20')")
            start = int(range_parts[0].strip())
            end = int(range_parts[1].strip())
            if start < 1 or end < 1:
                raise ValueError(f"Page numbers must be positive (got {start}-{end})")
            if start > end:
                raise ValueError(f"Invalid page range: {start}-{end} (start must be <= end)")
            pages.update(range(start, end + 1))
        else:
            page_num = int(part)
            if page_num < 1:
                raise ValueError(f"Page numbers must be positive (got {page_num})")
            pages.add(page_num)

    return pages


def markdown_to_text(content: str) -> str:
    """Strip lightweight markdown formatting so the output is plain text."""
    text = re.sub(r"!\[.*?\]\(.*?\)", "", content)  # drop images
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)  # keep link text
    text = re.sub(r"[#*_`~]+", "", text)  # remove emphasis markers
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_markdown_content(content: str, config_path: Optional[Path] = None) -> tuple[str, str]:
    """Clean markdown content using markdowncleaner.

    Returns:
        tuple: (cleaned_content, config_used_description)
    """
    if not MARKDOWNCLEANER_AVAILABLE:
        return content, "skipped (markdowncleaner not installed)"

    try:
        from markdowncleaner.config.loader import CleaningPatterns

        # Determine config path
        if config_path and config_path.exists():
            custom_patterns = CleaningPatterns.from_yaml(config_path)
            cleaner = MarkdownCleaner(patterns=custom_patterns)
            config_used = str(config_path)
        else:
            # Look for default config next to this script
            default_config = Path(__file__).parent / "markdowncleaner_config.yaml"
            if default_config.exists():
                custom_patterns = CleaningPatterns.from_yaml(default_config)
                cleaner = MarkdownCleaner(patterns=custom_patterns)
                config_used = str(default_config)
            else:
                cleaner = MarkdownCleaner()
                config_used = "default (no config file found)"

        cleaned_content = cleaner.clean_markdown_string(content)
        return cleaned_content, config_used

    except Exception as e:
        return content, f"skipped (error: {str(e)})"


def download_pdf_from_url(url: str, output_dir: Optional[Path] = None) -> Path:
    """Download a PDF file from a URL.

    Args:
        url: URL of the PDF file
        output_dir: Directory to save the PDF (optional, defaults to temp directory)

    Returns:
        Path: Path to the downloaded PDF file
    """
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)

    if not filename or not filename.lower().endswith('.pdf'):
        filename = "downloaded_document.pdf"

    if output_dir is None:
        output_dir = Path(tempfile.gettempdir())
    else:
        output_dir = Path(output_dir)

    output_path = output_dir / filename

    with urlopen(url) as response:
        pdf_data = response.read()

    output_path.write_bytes(pdf_data)
    return output_path


def get_api_key() -> str:
    """Get Mistral API key from environment."""
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError(
            "MISTRAL_API_KEY not found. "
            "Set it as an environment variable or in a .env file."
        )
    return api_key


def process_pdf_ocr(
    pdf_path: Path,
    model: str = DEFAULT_MODEL,
    page_numbers: Optional[set[int]] = None,
    extract_header: bool = True,
    extract_footer: bool = True,
) -> tuple[str, int, list[int], list[str]]:
    """Core OCR processing function.

    Returns:
        tuple: (markdown_content, total_pages, pages_processed, warnings)
    """
    api_key = get_api_key()
    client = Mistral(api_key=api_key)

    # Upload file
    file_bytes = pdf_path.read_bytes()
    uploaded = client.files.upload(
        file={"file_name": pdf_path.name, "content": file_bytes},
        purpose="ocr",
    )
    signed_url = client.files.get_signed_url(file_id=uploaded.id, expiry=1)

    # Build OCR request parameters
    ocr_params = {
        "document": DocumentURLChunk(document_url=signed_url.url),
        "model": model,
        "include_image_base64": False,
    }

    if not extract_header:
        ocr_params["extract_header"] = False
    if not extract_footer:
        ocr_params["extract_footer"] = False

    # Process OCR
    try:
        response = client.ocr.process(**ocr_params)
    except TypeError as e:
        # If extract_header/extract_footer not supported, retry without them
        if "extract_header" in str(e) or "extract_footer" in str(e):
            ocr_params = {
                "document": DocumentURLChunk(document_url=signed_url.url),
                "model": model,
                "include_image_base64": False,
            }
            response = client.ocr.process(**ocr_params)
        else:
            raise

    warnings = []
    total_pages = len(response.pages)

    # Filter pages if specified
    if page_numbers:
        filtered_pages = []
        pages_processed = []
        for idx, page in enumerate(response.pages, start=1):
            if idx in page_numbers:
                filtered_pages.append(page.markdown)
                pages_processed.append(idx)

        # Check for invalid pages
        invalid_pages = page_numbers - set(range(1, total_pages + 1))
        if invalid_pages:
            warnings.append(
                f"Requested pages {sorted(invalid_pages)} are out of range (PDF has {total_pages} pages)"
            )

        markdown_pages = filtered_pages
    else:
        markdown_pages = [page.markdown for page in response.pages]
        pages_processed = list(range(1, total_pages + 1))

    markdown_content = "\n\n".join(markdown_pages)
    return markdown_content, total_pages, pages_processed, warnings


# =============================================================================
# MCP Tools
# =============================================================================

@mcp.tool(
    name="mistral_ocr_process_pdf",
    annotations={
        "title": "Process PDF with OCR",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def mistral_ocr_process_pdf(params: ProcessPdfInput) -> str:
    """Process a local PDF file and extract text or markdown using Mistral OCR.

    This tool uploads a PDF to Mistral's OCR service and extracts the content
    as either markdown (preserving formatting, tables, headings) or plain text.

    Args:
        params: ProcessPdfInput with file_path, output_format, pages, etc.

    Returns:
        JSON string with: success, content, page_count, pages_processed,
        output_file, format, cleaned, warnings

    Examples:
        - Process entire PDF: file_path="/path/to/doc.pdf"
        - Specific pages: file_path="/path/to/doc.pdf", pages="1,5-10"
        - Plain text output: file_path="/path/to/doc.pdf", output_format="text"
        - Clean markdown: file_path="/path/to/doc.pdf", clean_output=True
    """
    try:
        # Validate file path
        pdf_path = Path(params.file_path).expanduser().resolve()
        if not pdf_path.exists():
            return json.dumps({
                "success": False,
                "error": f"PDF file not found: {params.file_path}",
                "suggestion": "Please provide an absolute path to an existing PDF file."
            })

        if pdf_path.suffix.lower() != ".pdf":
            return json.dumps({
                "success": False,
                "error": f"Expected a PDF file, got: {pdf_path.suffix}",
                "suggestion": "Ensure the file has a .pdf extension."
            })

        # Parse page specification
        page_numbers = None
        if params.pages:
            try:
                page_numbers = parse_page_spec(params.pages)
            except ValueError as e:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid page specification: {str(e)}",
                    "suggestion": "Use format like '1,5,10-15' for page selection."
                })

        # Process OCR
        markdown_content, total_pages, pages_processed, warnings = process_pdf_ocr(
            pdf_path=pdf_path,
            page_numbers=page_numbers,
            extract_header=params.extract_header,
            extract_footer=params.extract_footer,
        )

        # Clean markdown if requested
        cleaned = False
        config_used = None
        if params.clean_output and params.output_format == "markdown":
            markdown_content, config_used = clean_markdown_content(markdown_content)
            cleaned = "skipped" not in config_used

        # Convert to text if needed
        if params.output_format == "text":
            final_content = markdown_to_text(markdown_content)
        else:
            final_content = markdown_content

        # Save to file if requested
        output_file = None
        if params.save_to_file:
            ext = ".txt" if params.output_format == "text" else ".md"
            output_path = pdf_path.with_suffix(ext)
            output_path.write_text(final_content, encoding="utf-8")
            output_file = str(output_path)

        return json.dumps({
            "success": True,
            "content": final_content if params.return_content else None,
            "page_count": total_pages,
            "pages_processed": pages_processed,
            "output_file": output_file,
            "format": params.output_format,
            "cleaned": cleaned,
            "config_used": config_used,
            "warnings": warnings
        }, ensure_ascii=False)

    except ValueError as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "suggestion": "Check your MISTRAL_API_KEY environment variable."
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"OCR processing failed: {str(e)}",
            "suggestion": "Ensure the PDF is valid and not corrupted."
        })


@mcp.tool(
    name="mistral_ocr_process_url",
    annotations={
        "title": "Process PDF from URL",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def mistral_ocr_process_url(params: ProcessUrlInput) -> str:
    """Download a PDF from a URL and extract text or markdown using Mistral OCR.

    This tool downloads a PDF from the specified URL, processes it with OCR,
    and optionally saves the output. The downloaded PDF can be kept or deleted.

    Args:
        params: ProcessUrlInput with url, output_format, pages, keep_pdf, etc.

    Returns:
        JSON string with: success, content, page_count, pages_processed,
        output_file, pdf_file (if kept), format, cleaned, warnings

    Examples:
        - Process URL: url="https://example.com/doc.pdf"
        - Keep PDF: url="https://example.com/doc.pdf", keep_pdf=True
        - Custom output dir: url="...", output_dir="/path/to/output"
    """
    downloaded_pdf = None
    try:
        # Determine output directory
        output_dir = Path(params.output_dir) if params.output_dir else Path.cwd()
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        # Download PDF
        try:
            downloaded_pdf = download_pdf_from_url(params.url, output_dir)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to download PDF: {str(e)}",
                "suggestion": "Check the URL is accessible and points to a valid PDF."
            })

        # Parse page specification
        page_numbers = None
        if params.pages:
            try:
                page_numbers = parse_page_spec(params.pages)
            except ValueError as e:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid page specification: {str(e)}",
                    "suggestion": "Use format like '1,5,10-15' for page selection."
                })

        # Process OCR
        markdown_content, total_pages, pages_processed, warnings = process_pdf_ocr(
            pdf_path=downloaded_pdf,
            page_numbers=page_numbers,
            extract_header=params.extract_header,
            extract_footer=params.extract_footer,
        )

        # Clean markdown if requested
        cleaned = False
        config_used = None
        if params.clean_output and params.output_format == "markdown":
            markdown_content, config_used = clean_markdown_content(markdown_content)
            cleaned = "skipped" not in config_used

        # Convert to text if needed
        if params.output_format == "text":
            final_content = markdown_to_text(markdown_content)
        else:
            final_content = markdown_content

        # Save output file
        ext = ".txt" if params.output_format == "text" else ".md"
        output_path = downloaded_pdf.with_suffix(ext)
        output_path.write_text(final_content, encoding="utf-8")

        # Handle PDF cleanup
        pdf_file = None
        if params.keep_pdf:
            pdf_file = str(downloaded_pdf)
        else:
            downloaded_pdf.unlink()

        return json.dumps({
            "success": True,
            "content": final_content if params.return_content else None,
            "page_count": total_pages,
            "pages_processed": pages_processed,
            "output_file": str(output_path),
            "pdf_file": pdf_file,
            "format": params.output_format,
            "cleaned": cleaned,
            "config_used": config_used,
            "warnings": warnings
        }, ensure_ascii=False)

    except ValueError as e:
        # Cleanup on error
        if downloaded_pdf and downloaded_pdf.exists() and not params.keep_pdf:
            downloaded_pdf.unlink()
        return json.dumps({
            "success": False,
            "error": str(e),
            "suggestion": "Check your MISTRAL_API_KEY environment variable."
        })
    except Exception as e:
        # Cleanup on error
        if downloaded_pdf and downloaded_pdf.exists() and not params.keep_pdf:
            try:
                downloaded_pdf.unlink()
            except Exception:
                pass
        return json.dumps({
            "success": False,
            "error": f"Processing failed: {str(e)}",
            "suggestion": "Ensure the URL points to a valid PDF file."
        })


@mcp.tool(
    name="mistral_ocr_clean_markdown",
    annotations={
        "title": "Clean Markdown Content",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def mistral_ocr_clean_markdown(params: CleanMarkdownInput) -> str:
    """Clean repetitive content from markdown text.

    This utility tool removes repetitive headers, author names, and other
    noise from OCR-extracted markdown while preserving page numbers,
    journal titles, and footnotes.

    Optimized for Arabic/English academic papers.

    Args:
        params: CleanMarkdownInput with content and optional config_path

    Returns:
        JSON string with: success, content, original_length, cleaned_length, config_used

    Examples:
        - Basic cleaning: content="# Header\n..."
        - Custom config: content="...", config_path="/path/to/config.yaml"
    """
    try:
        if not MARKDOWNCLEANER_AVAILABLE:
            return json.dumps({
                "success": False,
                "error": "markdowncleaner package not installed",
                "suggestion": "Install with: pip install markdowncleaner"
            })

        original_length = len(params.content)

        # Determine config path
        config_path = None
        if params.config_path:
            config_path = Path(params.config_path).expanduser().resolve()
            if not config_path.exists():
                return json.dumps({
                    "success": False,
                    "error": f"Config file not found: {params.config_path}",
                    "suggestion": "Check the path or omit config_path to use defaults."
                })

        cleaned_content, config_used = clean_markdown_content(params.content, config_path)
        cleaned_length = len(cleaned_content)

        return json.dumps({
            "success": True,
            "content": cleaned_content,
            "original_length": original_length,
            "cleaned_length": cleaned_length,
            "reduction_percent": round((1 - cleaned_length / original_length) * 100, 1) if original_length > 0 else 0,
            "config_used": config_used
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Cleaning failed: {str(e)}",
            "suggestion": "Ensure the content is valid markdown text."
        })


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    mcp.run()
