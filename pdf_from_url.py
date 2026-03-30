#!/usr/bin/env python3
"""
Advanced PDF to Text/Markdown converter using Mistral OCR.

FEATURES:
- Single file processing: Convert individual PDF files to plain text or markdown
- URL processing: Pass PDF URLs directly to Mistral OCR API (no download/upload needed)
- Directory processing: Recursively process all PDFs in directories and subdirectories
- Smart skip logic: Only skip PDFs with existing files of the target extension
- User confirmation: Interactive confirmation for re-processing (only when target file exists)
- Unique naming: Append _1, _2, etc. to avoid overwriting existing files
- Format selection: --txt (default) for plain text, --md for markdown
- No download: URL mode sends URL directly to API, avoiding download and re-upload
- Dependency checking: Automatically checks and offers to install missing packages
- Page selection: Process specific pages using --pages (e.g., --pages 1,8,9,11-20)
- Header/Footer control: Skip header/footer extraction using --header 0 or --footer 0
- Markdown cleaning: Use --clean to remove repetitive headers while preserving page numbers, journal titles, and footnotes

USAGE EXAMPLES:
    # Process single file to plain text (default)
    python pdf_to_txt_new.py document.pdf

    # Process single file to markdown
    python pdf_to_txt_new.py document.pdf --md

    # Process PDF directly from URL (no download needed)
    python pdf_from_url.py --url https://example.com/document.pdf

    # Process URL and convert to markdown
    python pdf_from_url.py --url https://example.com/document.pdf --md

    # Use custom API key
    python pdf_to_txt_new.py document.pdf --api-key your_api_key_here

    # Explicit plain text (same as default)
    python pdf_to_txt_new.py document.pdf --txt

    # Process all PDFs in directory (recursive)
    python pdf_to_txt_new.py ./documents/
    python pdf_to_txt_new.py ./documents/ --md

    # Process specific pages only
    python pdf_to_txt_new.py document.pdf --pages 1,8,9,11-20
    python pdf_to_txt_new.py document.pdf --pages 1-5,10 --md

    # Skip header/footer extraction
    python pdf_to_txt_new.py document.pdf --header 0
    python pdf_to_txt_new.py document.pdf --footer no
    python pdf_to_txt_new.py document.pdf --header false --footer false

    # Clean markdown output (removes repetitive headers)
    python pdf_to_txt_new.py document.pdf --md --clean

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
- Python 3.8+
- MISTRAL_API_KEY environment variable, .env file, or --api-key parameter
- Python packages: mistralai, python-dotenv (auto-checked on startup)

OUTPUT:
- Plain text files (.txt) by default
- Markdown files (.md) with --md flag (preserves headings, tables, figure references)
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

from dotenv import load_dotenv
from mistralai import DocumentURLChunk, Mistral

try:
    from markdowncleaner import MarkdownCleaner
    MARKDOWNCLEANER_AVAILABLE = True
except ImportError:
    MARKDOWNCLEANER_AVAILABLE = False


def check_and_install_dependencies():
    """Check if required packages are installed and offer to install them if missing."""
    missing_packages = []

    # Check for python-dotenv
    try:
        import dotenv
    except ImportError:
        missing_packages.append('python-dotenv')

    # Check for mistralai
    try:
        import mistralai
    except ImportError:
        missing_packages.append('mistralai')

    # Check for markdowncleaner (optional)
    try:
        import markdowncleaner
    except ImportError:
        # markdowncleaner is optional, don't add to missing packages
        pass

    if missing_packages:
        print("\n" + "="*70, file=sys.stderr)
        print("ERROR: Missing required packages", file=sys.stderr)
        print("="*70, file=sys.stderr)
        for pkg in missing_packages:
            print(f"  ✗ {pkg}", file=sys.stderr)

        print("\nTo install missing packages, run one of these commands:", file=sys.stderr)
        print(f"  pip install {' '.join(missing_packages)}", file=sys.stderr)
        print("  pip install -r requirements.txt", file=sys.stderr)

        # Ask user if they want auto-install
        try:
            print("\nWould you like to install them now? (y/N): ", end='', file=sys.stderr)
            sys.stderr.flush()
            response = input().strip().lower()

            if response in ['y', 'yes']:
                print("\nInstalling missing packages...", file=sys.stderr)
                for pkg in missing_packages:
                    try:
                        print(f"  Installing {pkg}...", file=sys.stderr)
                        subprocess.check_call(
                            [sys.executable, '-m', 'pip', 'install', pkg],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE
                        )
                        print(f"  ✓ Successfully installed {pkg}", file=sys.stderr)
                    except subprocess.CalledProcessError as e:
                        print(f"  ✗ Failed to install {pkg}", file=sys.stderr)
                        if e.stderr:
                            print(f"     Error: {e.stderr.decode()}", file=sys.stderr)
                        sys.exit(1)

                print("\n" + "="*70, file=sys.stderr)
                print("✓ All dependencies installed successfully!", file=sys.stderr)
                print("="*70, file=sys.stderr)
                print("\nPlease run the script again to use the newly installed packages.", file=sys.stderr)
                sys.exit(0)
            else:
                print("\nInstallation cancelled. Please install packages manually.", file=sys.stderr)
                sys.exit(1)
        except (EOFError, KeyboardInterrupt):
            print("\n\nInstallation cancelled.", file=sys.stderr)
            sys.exit(1)



def parse_bool_arg(value: str) -> bool:
    """Parse boolean argument from various string formats.

    Args:
        value: String value ('0', '1', 'false', 'true', 'no', 'yes')

    Returns:
        bool: Parsed boolean value

    Examples:
        >>> parse_bool_arg('1')
        True
        >>> parse_bool_arg('0')
        False
        >>> parse_bool_arg('false')
        False
        >>> parse_bool_arg('no')
        False
    """
    value_lower = value.lower().strip()
    if value_lower in ('0', 'false', 'no'):
        return False
    elif value_lower in ('1', 'true', 'yes'):
        return True
    else:
        raise ValueError(f"Invalid boolean value: '{value}' (expected: 0/1, false/true, no/yes)")


def parse_page_spec(page_spec: str) -> set[int]:
    """Parse page specification string into a set of page numbers.

    Args:
        page_spec: String like "1,8,9,11-20" or "1-5,10"

    Returns:
        set[int]: Set of page numbers (1-indexed)

    Examples:
        >>> parse_page_spec("1,8,9,11-20")
        {1, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20}
        >>> parse_page_spec("1-5,10")
        {1, 2, 3, 4, 5, 10}
    """
    pages = set()

    # Split by comma
    parts = page_spec.split(',')

    for part in parts:
        part = part.strip()

        # Check if it's a range (e.g., "11-20")
        if '-' in part:
            try:
                # Check for invalid negative numbers
                if part.startswith('-'):
                    raise ValueError(f"Page numbers must be positive (got '{part}')")

                # Split on '-'
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
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError(f"Invalid page range format: '{part}' (expected format: '11-20')")
                raise
        else:
            # Single page number
            try:
                page_num = int(part)
                if page_num < 1:
                    raise ValueError(f"Page numbers must be positive (got {page_num})")
                pages.add(page_num)
            except ValueError:
                raise ValueError(f"Invalid page number: '{part}' (expected a positive integer)")

    return pages


def markdown_to_text(content: str) -> str:
    """Strip lightweight markdown formatting so the output is plain text."""
    text = re.sub(r"!\[.*?\]\(.*?\)", "", content)  # drop images
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)  # keep link text
    text = re.sub(r"[#*_`~]+", "", text)  # remove emphasis markers
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_markdown_content(content: str) -> str:
    """Clean markdown content using markdowncleaner with YAML configuration for Arabic/English academic papers.
    
    Args:
        content: Markdown content to clean
    
    Returns:
        str: Cleaned markdown content
    """
    if not MARKDOWNCLEANER_AVAILABLE:
        print("  Warning: markdowncleaner not available, skipping cleaning")
        return content
    
    try:
        from markdowncleaner.config.loader import CleaningPatterns
        
        # Look for YAML config file next to the script
        config_path = Path(__file__).parent / "markdowncleaner_config.yaml"
        
        if config_path.exists():
            print(f"  Using config: {config_path.name}")
            # Load custom patterns from YAML file
            custom_patterns = CleaningPatterns.from_yaml(config_path)
            cleaner = MarkdownCleaner(patterns=custom_patterns)
        else:
            print("  Using default markdowncleaner settings (config file not found)")
            # Fallback to default settings
            cleaner = MarkdownCleaner()
        
        # Clean the content directly as a string
        cleaned_content = cleaner.clean_markdown_string(content)
        
        return cleaned_content
        
    except Exception as e:
        print(f"  Warning: Error during markdown cleaning: {e}")
        print("  Falling back to original content")
        return content


def convert_url_to_txt(url: str, model: str, output_path: Path, to_txt: bool = False, api_key: str = None, page_numbers: set[int] = None, extract_header: bool = True, extract_footer: bool = True, clean_markdown: bool = False) -> tuple[Path, int]:
    """Pass a PDF URL directly to Mistral OCR API without downloading.

    Args:
        url: URL of the PDF file
        model: OCR model to use
        output_path: Path for the output file
        to_txt: If True, convert to plain text; if False, keep markdown format
        api_key: Mistral API key (optional, defaults to MISTRAL_API_KEY environment variable)
        page_numbers: Set of page numbers to process (1-indexed). If None, process all pages.
        extract_header: If True, extract header content from PDF (default: True)
        extract_footer: If True, extract footer content from PDF (default: True)
        clean_markdown: If True, clean markdown content to remove repetitive headers (default: False)

    Returns:
        tuple: (output_path, page_count)
    """
    # Use provided api_key or load from environment
    if not api_key:
        load_dotenv()
        api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise EnvironmentError("Set MISTRAL_API_KEY in your environment or .env file, or provide --api-key.")

    client = Mistral(api_key=api_key)

    # Pass URL directly to OCR API — no download or upload needed
    ocr_params = {
        "document": DocumentURLChunk(document_url=url),
        "model": model,
        "include_image_base64": False,
    }

    if not extract_header:
        ocr_params["extract_header"] = False
    if not extract_footer:
        ocr_params["extract_footer"] = False

    try:
        response = client.ocr.process(**ocr_params)
    except TypeError as e:
        if "extract_header" in str(e) or "extract_footer" in str(e):
            ocr_params = {
                "document": DocumentURLChunk(document_url=url),
                "model": model,
                "include_image_base64": False,
            }
            response = client.ocr.process(**ocr_params)
            if not extract_header or not extract_footer:
                print("  Note: Header/footer extraction control not supported by current API version")
        else:
            raise

    # Filter pages if page_numbers is specified
    if page_numbers:
        filtered_pages = []
        for idx, page in enumerate(response.pages, start=1):
            if idx in page_numbers:
                filtered_pages.append(page.markdown)

        total_pages = len(response.pages)
        invalid_pages = page_numbers - set(range(1, total_pages + 1))
        if invalid_pages:
            print(f"  Warning: Requested pages {sorted(invalid_pages)} are out of range (PDF has {total_pages} pages)")

        markdown_pages = filtered_pages
        page_count = len(filtered_pages)
    else:
        markdown_pages = [page.markdown for page in response.pages]
        page_count = len(response.pages)

    markdown_content = "\n\n".join(markdown_pages)

    if clean_markdown and not to_txt:
        print("  Cleaning markdown content...")
        markdown_content = clean_markdown_content(markdown_content)

    if to_txt:
        final_content = markdown_to_text(markdown_content)
    else:
        final_content = markdown_content

    output_path.write_text(final_content, encoding="utf-8")
    return output_path, page_count


def convert_pdf_to_txt(pdf_path: Path, model: str, output_path: Path = None, to_txt: bool = False, api_key: str = None, page_numbers: set[int] = None, extract_header: bool = True, extract_footer: bool = True, clean_markdown: bool = False) -> tuple[Path, int]:
    """Upload the PDF, request OCR, and write the markdown or text output.

    Args:
        pdf_path: Path to the PDF file
        model: OCR model to use
        output_path: Custom output path (optional, defaults to pdf_path with .md or .txt extension)
        to_txt: If True, convert to plain text; if False, keep markdown format
        api_key: Mistral API key (optional, defaults to MISTRAL_API_KEY environment variable)
        page_numbers: Set of page numbers to process (1-indexed). If None, process all pages.
        extract_header: If True, extract header content from PDF (default: True)
        extract_footer: If True, extract footer content from PDF (default: True)
        clean_markdown: If True, clean markdown content to remove repetitive headers (default: False)

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

    # Build OCR request parameters
    ocr_params = {
        "document": DocumentURLChunk(document_url=signed_url.url),
        "model": model,
        "include_image_base64": False,
    }

    # Add header/footer extraction if supported (optional parameters)
    if not extract_header:
        ocr_params["extract_header"] = False
    if not extract_footer:
        ocr_params["extract_footer"] = False

    try:
        response = client.ocr.process(**ocr_params)
    except TypeError as e:
        # If extract_header/extract_footer are not supported, retry without them
        if "extract_header" in str(e) or "extract_footer" in str(e):
            ocr_params = {
                "document": DocumentURLChunk(document_url=signed_url.url),
                "model": model,
                "include_image_base64": False,
            }
            response = client.ocr.process(**ocr_params)
            if not extract_header or not extract_footer:
                print("  Note: Header/footer extraction control not supported by current API version")
        else:
            raise

    # Filter pages if page_numbers is specified
    if page_numbers:
        # Convert to list and filter by 1-indexed page numbers
        filtered_pages = []
        for idx, page in enumerate(response.pages, start=1):
            if idx in page_numbers:
                filtered_pages.append(page.markdown)

        # Check if any requested pages are out of range
        total_pages = len(response.pages)
        invalid_pages = page_numbers - set(range(1, total_pages + 1))
        if invalid_pages:
            print(f"  Warning: Requested pages {sorted(invalid_pages)} are out of range (PDF has {total_pages} pages)")

        markdown_pages = filtered_pages
        page_count = len(filtered_pages)
    else:
        markdown_pages = [page.markdown for page in response.pages]
        page_count = len(response.pages)

    markdown_content = "\n\n".join(markdown_pages)

    # Clean markdown content if requested (before converting to text)
    if clean_markdown and not to_txt:
        print("  Cleaning markdown content...")
        markdown_content = clean_markdown_content(markdown_content)

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
        help="URL of PDF file to pass directly to Mistral OCR API (no download).",
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
    parser.add_argument(
        "--pages",
        help="Specific pages to process (e.g., '1,8,9,11-20'). If not specified, all pages are processed.",
    )
    parser.add_argument(
        "--header",
        nargs='?',
        const='1',
        default='1',
        help="Extract header content from PDF. Default: 1 (extract). Use 0/false/no to skip header extraction.",
    )
    parser.add_argument(
        "--footer",
        nargs='?',
        const='1',
        default='1',
        help="Extract footer content from PDF. Default: 1 (extract). Use 0/false/no to skip footer extraction.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean markdown output to remove repetitive headers while preserving page numbers, journal titles, and footnotes. Only works with --md output.",
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

        # Parse page numbers if specified
        page_numbers = None
        if args.pages:
            try:
                page_numbers = parse_page_spec(args.pages)
                print(f"Processing pages: {sorted(page_numbers)}")
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)

        # Parse header/footer extraction options
        try:
            extract_header = parse_bool_arg(args.header)
            extract_footer = parse_bool_arg(args.footer)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        # Determine output extension based on --md flag (default is .txt)
        output_extension = ".md" if args.md else ".txt"
        to_txt = not args.md  # Convert to plain text unless --md is specified

        # Handle URL input — pass URL directly to Mistral OCR API
        if args.url:
            # Derive output filename from URL
            parsed_url = urlparse(args.url)
            filename = unquote(os.path.basename(parsed_url.path))
            if not filename or not filename.lower().endswith('.pdf'):
                filename = "downloaded_document.pdf"
            output_path = Path.cwd() / Path(filename).with_suffix(output_extension)

            if output_path.exists():
                resp = input(f"File '{output_path.name}' already exists. Re-process? (y/N): ").strip().lower()
                if resp not in ['y', 'yes']:
                    print("Skipping processing.")
                    return
                # Find unique filename
                counter = 1
                while True:
                    stem = Path(filename).stem
                    new_name = f"{stem}_{counter}{output_extension}"
                    candidate = Path.cwd() / new_name
                    if not candidate.exists():
                        output_path = candidate
                        break
                    counter += 1
                print(f"Output will be saved as: {output_path.name}")

            print(f"Processing URL: {args.url}")
            clean_markdown = args.clean
            if clean_markdown and to_txt:
                print("  Warning: --clean flag only works with markdown output (--md). Ignoring --clean.")
                clean_markdown = False

            try:
                output_path, page_count = convert_url_to_txt(
                    args.url,
                    args.model,
                    output_path,
                    to_txt,
                    getattr(args, 'api_key', None),
                    page_numbers,
                    extract_header,
                    extract_footer,
                    clean_markdown,
                )
                print(f"  ✓ Completed: {output_path.name} ({page_count} pages)")
                print(f"\nProcessing complete!")
                print(f"Files processed: 1/1")
            except Exception as url_exc:
                print(f"Error processing URL: {url_exc}", file=sys.stderr)
                sys.exit(1)
            return

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
                # Check if cleaning is requested with text output (warn user)
                clean_markdown = args.clean
                if clean_markdown and to_txt:
                    print("  Warning: --clean flag only works with markdown output (--md). Ignoring --clean.")
                    clean_markdown = False
                    
                output_path, page_count = convert_pdf_to_txt(
                    pdf_file,
                    args.model,
                    output_path,
                    to_txt,
                    getattr(args, 'api_key', None),
                    page_numbers,
                    extract_header,
                    extract_footer,
                    clean_markdown
                )

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
    check_and_install_dependencies()
    main()
