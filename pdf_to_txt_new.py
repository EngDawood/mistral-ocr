#!/usr/bin/env python3
"""
Advanced PDF to Text/Markdown converter using Mistral OCR.

FEATURES:
- Single file processing: Convert individual PDF files to plain text or markdown
- URL processing: Download and process PDFs directly from URLs
- Directory processing: Recursively process all PDFs in directories and subdirectories
- Smart skip logic: Only skip PDFs with existing files of the target extension
- User confirmation: Interactive confirmation for re-processing (only when target file exists)
- Unique naming: Append _1, _2, etc. to avoid overwriting existing files
- Format selection: --txt (default) for plain text, --md for markdown

USAGE EXAMPLES:
    # Process single file to plain text (default)
    python pdf_to_txt_new.py document.pdf

    # Process single file to markdown
    python pdf_to_txt_new.py document.pdf --md

    # Download and process PDF from URL
    python pdf_to_txt_new.py --url https://example.com/document.pdf

    # Download PDF and convert to markdown
    python pdf_to_txt_new.py --url https://example.com/document.pdf --md

    # Use custom API key
    python pdf_to_txt_new.py document.pdf --api-key your_api_key_here

    # Explicit plain text (same as default)
    python pdf_to_txt_new.py document.pdf --txt

    # Process all PDFs in directory (recursive)
    python pdf_to_txt_new.py ./documents/
    python pdf_to_txt_new.py ./documents/ --md

DIRECTORY PROCESSING:
- Recursively finds all *.pdf files in subdirectories
- Skips files that already have the target extension (.txt or .md)
- If file.txt exists and you run with --md, it will process (different extension)
- Shows progress

SINGLE FILE PROCESSING:
- Checks if PDF has output file with target extension
- Asks for confirmation only if target extension file exists
- Creates uniquely named output files (_1, _2, etc.) when re-processing

REQUIREMENTS:
- MISTRAL_API_KEY environment variable, .env file, or --api-key parameter
- Python packages: mistralai, python-dotenv

OUTPUT:
- Plain text files (.txt) by default
- Markdown files (.md) with --md flag (preserves headings, tables, figure references)
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from dotenv import load_dotenv
from mistralai import DocumentURLChunk, Mistral


def download_pdf_from_url(url: str, output_dir: Path = None) -> Path:
    """Download a PDF file from a URL to a temporary or specified directory.

    Args:
        url: URL of the PDF file
        output_dir: Directory to save the PDF (optional, defaults to temp directory)

    Returns:
        Path: Path to the downloaded PDF file
    """
    # Parse URL to get filename
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)

    # If no filename in URL, generate one
    if not filename or not filename.lower().endswith('.pdf'):
        filename = "downloaded_document.pdf"

    # Determine output directory
    if output_dir is None:
        output_dir = Path(tempfile.gettempdir())
    else:
        output_dir = Path(output_dir)

    output_path = output_dir / filename

    # Download the file
    print(f"Downloading PDF from: {url}")
    with urlopen(url) as response:
        pdf_data = response.read()

    # Save to file
    output_path.write_bytes(pdf_data)
    print(f"Downloaded to: {output_path}")

    return output_path


def markdown_to_text(content: str) -> str:
    """Strip lightweight markdown formatting so the output is plain text."""
    text = re.sub(r"!\[.*?\]\(.*?\)", "", content)  # drop images
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)  # keep link text
    text = re.sub(r"[#*_`~]+", "", text)  # remove emphasis markers
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def convert_pdf_to_txt(pdf_path: Path, model: str, output_path: Path = None, to_txt: bool = False, api_key: str = None) -> tuple[Path, int]:
    """Upload the PDF, request OCR, and write the markdown or text output.

    Args:
        pdf_path: Path to the PDF file
        model: OCR model to use
        output_path: Custom output path (optional, defaults to pdf_path with .md or .txt extension)
        to_txt: If True, convert to plain text; if False, keep markdown format
        api_key: Mistral API key (optional, defaults to MISTRAL_API_KEY environment variable)

    Returns:
        tuple: (output_path, page_count)
    """
    pdf_path = pdf_path.expanduser().resolve()
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, got: {pdf_path.name}")

    if output_path is None:
        output_path = pdf_path.with_suffix(".txt" if to_txt else ".md")

    # Use provided api_key or load from environment
    if not api_key:
        load_dotenv()
        api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise EnvironmentError("Set MISTRAL_API_KEY in your environment or .env file, or provide --api-key.")

    client = Mistral(api_key=api_key)
    file_bytes = pdf_path.read_bytes()
    uploaded = client.files.upload(
        file={"file_name": pdf_path.name, "content": file_bytes},
        purpose="ocr",
    )
    signed_url = client.files.get_signed_url(file_id=uploaded.id, expiry=1)
    response = client.ocr.process(
        document=DocumentURLChunk(document_url=signed_url.url),
        model=model,
        include_image_base64=False,
    )

    page_count = len(response.pages)
    markdown_pages = [page.markdown for page in response.pages]
    markdown_content = "\n\n".join(markdown_pages)

    # Convert to plain text if requested
    if to_txt:
        final_content = markdown_to_text(markdown_content)
    else:
        final_content = markdown_content

    output_path.write_text(final_content, encoding="utf-8")
    return output_path, page_count


def find_pdf_files(input_path: Path, target_ext: str = ".txt") -> list[Path]:
    """Find all PDF files in the given path recursively.

    If path is a file, return it as a list. If directory, return all PDFs that
    haven't been processed yet (only checks for files with target_ext).

    Args:
        input_path: Path to PDF file or directory
        target_ext: Target extension to check for existing files (".txt" or ".md")
    """
    input_path = input_path.expanduser().resolve()

    if input_path.is_file():
        if input_path.suffix.lower() == ".pdf":
            return [input_path]
        else:
            raise ValueError(f"Expected a PDF file, got: {input_path.name}")
    elif input_path.is_dir():
        # Recursively find all PDF files in directory and subdirectories
        all_pdf_files = list(input_path.rglob("*.pdf"))
        if not all_pdf_files:
            raise ValueError(f"No PDF files found in directory: {input_path}")

        # Filter out PDFs that already have corresponding file with target extension
        unprocessed_pdfs = []
        for pdf_file in all_pdf_files:
            target_file = pdf_file.with_suffix(target_ext)
            if not target_file.exists():
                unprocessed_pdfs.append(pdf_file)

        if not unprocessed_pdfs:
            print(f"All {len(all_pdf_files)} PDF files in directory already have {target_ext} files.")
            return []

        skipped_count = len(all_pdf_files) - len(unprocessed_pdfs)
        if skipped_count > 0:
            print(f"Skipping {skipped_count} PDF(s) with existing {target_ext} files, {len(unprocessed_pdfs)} remaining.")

        return sorted(unprocessed_pdfs)  # Sort for consistent processing order
    else:
        raise FileNotFoundError(f"Path not found: {input_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert PDF(s) to text or markdown using Mistral OCR. Can process a single PDF file or all PDFs in a directory.",
    )
    parser.add_argument("input", nargs='?', help="Path to PDF file or directory containing PDF files to convert.")
    parser.add_argument(
        "--url",
        help="URL of PDF file to download and process.",
    )
    parser.add_argument(
        "--model",
        default="mistral-ocr-latest",
        help="OCR model name (default: mistral-ocr-latest).",
    )
    parser.add_argument(
        "--api-key",
        help="Mistral API key (overrides MISTRAL_API_KEY environment variable).",
    )
    format_group = parser.add_mutually_exclusive_group()
    format_group.add_argument(
        "--txt",
        action="store_true",
        help="Convert to plain text (default behavior).",
    )
    format_group.add_argument(
        "--md",
        action="store_true",
        help="Convert to markdown instead of plain text.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        # Validate input arguments
        if not args.input and not args.url:
            print("Error: Please provide either an input path or --url parameter.", file=sys.stderr)
            sys.exit(1)

        if args.input and args.url:
            print("Error: Please provide either an input path or --url parameter, not both.", file=sys.stderr)
            sys.exit(1)

        # Determine output extension based on --md flag (default is .txt)
        output_extension = ".md" if args.md else ".txt"
        to_txt = not args.md  # Convert to plain text unless --md is specified

        # Handle URL input
        if args.url:
            try:
                # Download PDF from URL to current directory
                downloaded_pdf = download_pdf_from_url(args.url, Path.cwd())
                input_path = downloaded_pdf

                # Process single downloaded file
                target_file = input_path.with_suffix(output_extension)
                if target_file.exists():
                    response = input(f"File '{target_file.name}' already exists. Re-process? (y/N): ").strip().lower()
                    if response not in ['y', 'yes']:
                        print("Skipping processing.")
                        return

                pdf_files = [input_path]
            except Exception as download_exc:
                print(f"Error downloading PDF from URL: {download_exc}", file=sys.stderr)
                sys.exit(1)
        else:
            # Handle local file/directory input
            input_path = Path(args.input)

            # Check if it's a single file that might already be processed (only check target extension)
            if input_path.is_file() and input_path.suffix.lower() == ".pdf":
                target_file = input_path.with_suffix(output_extension)
                if target_file.exists():
                    response = input(f"File '{target_file.name}' already exists. Re-process? (y/N): ").strip().lower()
                    if response not in ['y', 'yes']:
                        print("Skipping processing.")
                        return

            # Find all PDF files to process (only skip files with target extension)
            pdf_files = find_pdf_files(input_path, output_extension)

        total_files = len(pdf_files)

        if total_files == 1:
            print(f"Processing 1 PDF file...")
        elif total_files > 1:
            print(f"Processing {total_files} PDF files from directory...")
        else:
            return  # No files to process

        processed_count = 0

        for pdf_file in pdf_files:
            try:
                # For single files that are being re-processed, modify output filename
                output_path_original = pdf_file.with_suffix(output_extension)
                if input_path.is_file() and output_path_original.exists():
                    # Find a unique filename by appending _1, _2, etc.
                    counter = 1
                    while True:
                        stem = pdf_file.stem
                        new_name = f"{stem}_{counter}{output_extension}"
                        output_path_candidate = pdf_file.parent / new_name
                        if not output_path_candidate.exists():
                            output_path = output_path_candidate
                            break
                        counter += 1
                    print(f"Output will be saved as: {output_path.name}")
                else:
                    output_path = output_path_original

                print(f"Processing: {pdf_file.name}")
                output_path, page_count = convert_pdf_to_txt(pdf_file, args.model, output_path, to_txt, getattr(args, 'api_key', None))

                processed_count += 1

                print(f"  ✓ Completed: {output_path.name} ({page_count} pages)")

            except Exception as file_exc:
                print(f"  ✗ Error processing {pdf_file.name}: {file_exc}", file=sys.stderr)
                continue

        print(f"\nProcessing complete!")
        print(f"Files processed: {processed_count}/{total_files}")

    except Exception as exc:  # pragma: no cover - simple CLI error surfacing
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
