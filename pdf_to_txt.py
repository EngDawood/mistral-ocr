#!/usr/bin/env python3
"""
Single-file PDF to TXT converter using Mistral OCR.

Reads one PDF, sends it to Mistral, and writes a UTF-8 text file
with the same stem in the same directory. Requires MISTRAL_API_KEY.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
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


def convert_pdf_to_txt(pdf_path: Path, model: str) -> Path:
    """Upload the PDF, request OCR, and write the plain-text output."""
    pdf_path = pdf_path.expanduser().resolve()
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, got: {pdf_path.name}")

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
        include_image_base64=False,
    )

    markdown_pages = [page.markdown for page in response.pages]
    plain_text = markdown_to_text("\n\n".join(markdown_pages))

    output_path = pdf_path.with_suffix(".md")
    output_path.write_text(plain_text, encoding="utf-8")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a PDF to plain text using Mistral OCR.",
    )
    parser.add_argument("pdf", help="Path to the PDF file to convert.")
    parser.add_argument(
        "--model",
        default="mistral-ocr-latest",
        help="OCR model name (default: mistral-ocr-latest).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        output_path = convert_pdf_to_txt(Path(args.pdf), args.model)
    except Exception as exc:  # pragma: no cover - simple CLI error surfacing
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"OCR complete. Text saved to {output_path}")


if __name__ == "__main__":
    main()
