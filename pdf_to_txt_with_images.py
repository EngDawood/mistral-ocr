#!/usr/bin/env python3
"""
Advanced PDF to Markdown converter using Mistral OCR with Image Extraction.

FEATURES:
- Single file processing: Convert individual PDF files to markdown (preserves formatting)
- Directory processing: Recursively process all PDFs in directories and subdirectories
- Image extraction: Extracts embedded images from PDFs and saves them separately
- Smart skip logic: Automatically skip PDFs that have already been processed (have .md files)
- Cost tracking: Automatic cost calculation ($0.001 per page) and logging
- User confirmation: Interactive confirmation for re-processing single files
- Unique naming: Append _1, _2, etc. to avoid overwriting existing files
- Comprehensive logging: CSV tracking file with filename, pages, cost, and timestamps

USAGE EXAMPLES:
    # Process single file
    python pdf_to_txt_with_images.py document.pdf

    # Process all PDFs in directory (recursive)
    python pdf_to_txt_with_images.py ./documents/

    # Custom tracking file
    python pdf_to_txt_with_images.py ./pdfs --track-file my_log.csv --track-format csv

COST TRACKING:
- Automatically creates 'ocr_usage_tracking.csv' next to the script
- Tracks: filename, page_count, processing_date, cost_usd, output_path
- Cost: $0.001 per page (based on Mistral OCR pricing)

DIRECTORY PROCESSING:
- Recursively finds all *.pdf files in subdirectories
- Skips files that already have corresponding *.md files
- Processes only new or unprocessed PDFs
- Shows progress and cost summary

SINGLE FILE PROCESSING:
- Checks if PDF has already been processed (has .md file)
- Asks for confirmation before re-processing
- Creates uniquely named output files (_1, _2, etc.) to avoid overwrites

REQUIREMENTS:
- MISTRAL_API_KEY environment variable or .env file
- Python packages: mistralai, python-dotenv

OUTPUT:
- Markdown files (.md) with extracted text (preserves headings, tables, and figure references)
- Extracted images saved as separate files (PNG/JPG format)
- Automatic cost tracking in CSV format
- Optional custom tracking files
"""
from __future__ import annotations

import argparse
import base64
import csv
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from mistralai import DocumentURLChunk, Mistral


def markdown_to_text(content: str) -> str:
    """Strip lightweight markdown formatting so the output is plain text."""
    text = re.sub(r"!\[.*?\]\(.*?\)", "", content)  # drop images
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)  # keep link text
    text = re.sub(r"[#*_`~]+", "", text)  # remove emphasis markers
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def convert_pdf_to_txt(pdf_path: Path, model: str, output_path: Path = None) -> tuple[Path, int]:
    """Upload the PDF, request OCR, and write the markdown output.

    Args:
        pdf_path: Path to the PDF file
        model: OCR model to use
        output_path: Custom output path (optional, defaults to pdf_path with .md extension)

    Returns:
        tuple: (output_path, page_count)
    """
    pdf_path = pdf_path.expanduser().resolve()
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, got: {pdf_path.name}")

    if output_path is None:
        output_path = pdf_path.with_suffix(".md")

    load_dotenv()
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise EnvironmentError("Set MISTRAL_API_KEY in your environment or .env file.")

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
        include_image_base64=True,  # Enable image extraction
    )

    # Save images separately
    image_count = 0
    for page_idx, page in enumerate(response.pages, start=1):
        if hasattr(page, 'images') and page.images:
            for img in page.images:
                if hasattr(img, 'image_base64') and img.image_base64:
                    img_data = base64.b64decode(img.image_base64)
                    img_id = getattr(img, 'id', f'page{page_idx}_img{image_count}')
                    img_path = pdf_path.parent / f"{pdf_path.stem}_{img_id}.png"
                    img_path.write_bytes(img_data)
                    image_count += 1
                    print(f"  → Extracted image: {img_path.name}")

    page_count = len(response.pages)
    markdown_pages = [page.markdown for page in response.pages]
    # Keep the markdown format to preserve headings, tables, and figure references
    markdown_content = "\n\n".join(markdown_pages)

    output_path.write_text(markdown_content, encoding="utf-8")

    if image_count > 0:
        print(f"  → Extracted {image_count} image(s)")

    return output_path, page_count


def find_pdf_files(input_path: Path) -> list[Path]:
    """Find all PDF files in the given path recursively. If path is a file, return it as a list. If directory, return all PDFs that haven't been processed yet."""
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

        # Filter out PDFs that already have corresponding .md files
        unprocessed_pdfs = []
        for pdf_file in all_pdf_files:
            md_file = pdf_file.with_suffix(".md")
            if not md_file.exists():
                unprocessed_pdfs.append(pdf_file)

        if not unprocessed_pdfs:
            print(f"All {len(all_pdf_files)} PDF files in directory have already been processed.")
            return []

        skipped_count = len(all_pdf_files) - len(unprocessed_pdfs)
        if skipped_count > 0:
            print(f"Skipping {skipped_count} already processed PDF(s), {len(unprocessed_pdfs)} remaining.")

        return sorted(unprocessed_pdfs)  # Sort for consistent processing order
    else:
        raise FileNotFoundError(f"Path not found: {input_path}")


def write_tracking_info(tracking_file: Path, filename: str, page_count: int, output_path: Path, format_type: str) -> None:
    """Write tracking information to a file in txt or csv format."""
    processing_date = datetime.now().isoformat()
    cost_usd = page_count * 0.001  # $0.001 per page according to Mistral OCR pricing

    if format_type.lower() == "csv":
        file_exists = tracking_file.exists()
        with open(tracking_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["filename", "page_count", "processing_date", "cost_usd", "output_path"])
            writer.writerow([filename, page_count, processing_date, f"{cost_usd:.4f}", str(output_path)])
    else:  # txt format
        with open(tracking_file, "a", encoding="utf-8") as f:
            f.write(f"{filename}: {page_count} pages, processed on {processing_date}, cost: ${cost_usd:.4f}, output: {output_path}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert PDF(s) to markdown using Mistral OCR with image extraction. Can process a single PDF file or all PDFs in a directory.",
    )
    parser.add_argument("input", help="Path to PDF file or directory containing PDF files to convert.")
    parser.add_argument(
        "--model",
        default="mistral-ocr-latest",
        help="OCR model name (default: mistral-ocr-latest).",
    )
    parser.add_argument(
        "--track-file",
        type=str,
        help="Path to file for tracking processed files (optional).",
    )
    parser.add_argument(
        "--track-format",
        choices=["txt", "csv"],
        default="txt",
        help="Format for tracking file: txt or csv (default: txt).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        input_path = Path(args.input)

        # Check if it's a single file that might already be processed
        if input_path.is_file() and input_path.suffix.lower() == ".pdf":
            md_file = input_path.with_suffix(".md")
            if md_file.exists():
                response = input(f"File '{input_path.name}' has already been processed. Re-process it? (y/N): ").strip().lower()
                if response not in ['y', 'yes']:
                    print("Skipping processing.")
                    return

        # Find all PDF files to process
        pdf_files = find_pdf_files(input_path)
        total_files = len(pdf_files)

        if total_files == 1:
            print(f"Processing 1 PDF file...")
        else:
            print(f"Processing {total_files} PDF files from directory...")

        # Always write to default tracking file next to the script for cost analysis
        script_dir = Path(__file__).parent
        default_tracking_file = script_dir / "ocr_usage_tracking.csv"

        # Write to custom tracking file if requested
        custom_tracking_file = None
        if args.track_file:
            custom_tracking_file = Path(args.track_file)
            # If custom path is relative, make it relative to script directory
            if not custom_tracking_file.is_absolute():
                custom_tracking_file = script_dir / custom_tracking_file

        processed_count = 0
        total_cost = 0.0

        for pdf_file in pdf_files:
            try:
                # For single files that are being re-processed, modify output filename
                output_path_original = pdf_file.with_suffix(".md")
                if input_path.is_file() and output_path_original.exists():
                    # Find a unique filename by appending _1, _2, etc.
                    counter = 1
                    while True:
                        stem = pdf_file.stem
                        new_name = f"{stem}_{counter}.md"
                        output_path_candidate = pdf_file.parent / new_name
                        if not output_path_candidate.exists():
                            output_path = output_path_candidate
                            break
                        counter += 1
                    print(f"Output will be saved as: {output_path.name}")
                else:
                    output_path = output_path_original

                print(f"Processing: {pdf_file.name}")
                output_path, page_count = convert_pdf_to_txt(pdf_file, args.model, output_path)

                # Write to default tracking file
                write_tracking_info(
                    default_tracking_file,
                    pdf_file.name,
                    page_count,
                    output_path,
                    "csv"  # Always use CSV for automatic tracking for better analysis
                )

                # Write to custom tracking file if requested
                if custom_tracking_file:
                    write_tracking_info(
                        custom_tracking_file,
                        pdf_file.name,
                        page_count,
                        output_path,
                        args.track_format
                    )

                cost_usd = page_count * 0.001
                total_cost += cost_usd
                processed_count += 1

                print(f"  ✓ Completed: {output_path.name} ({page_count} pages, ${cost_usd:.4f})")

            except Exception as file_exc:
                print(f"  ✗ Error processing {pdf_file.name}: {file_exc}", file=sys.stderr)
                continue

        print(f"\nProcessing complete!")
        print(f"Files processed: {processed_count}/{total_files}")
        print(f"Total cost: ${total_cost:.4f}")
        print(f"Usage tracking saved to {default_tracking_file}")

        if custom_tracking_file:
            print(f"Custom tracking saved to {custom_tracking_file}")

    except Exception as exc:  # pragma: no cover - simple CLI error surfacing
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
