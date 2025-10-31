# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.html).

## [Unreleased]

## [1.2.0] - 2025-10-31

### Added
- Example OCR output section to README with Arabic text sample
- Screenshot example (screenshot/image.png) showing OCR processing results
- Sample output.md content demonstrating Arabic text processing
- Step-by-step guide for getting free Mistral API key in both English and Arabic READMEs
- Comprehensive example of Arabic PDF processing results

### Changed
- Enhanced README.md with visual examples and usage demonstrations
- Updated README_ar.md with corresponding Arabic examples and API guide
- Improved documentation for new users with clear API access instructions

## [1.1.0] - 2025-10-24

### Added
- Arabic README file (README_ar.md) with full translation
- Arabic introduction section to main README.md
- Arabic Language Support section with multilingual capabilities
- In-place processing documentation showing files are processed from any directory
- Mistral OCR API information including free tier details and limitations
- Links to official OCR cookbooks and resources

### Changed
- Updated repository description to focus on Arabic-English PDF processing
- Enhanced documentation with multilingual support information
- Added comprehensive logging and cost tracking features

## [1.0.0] - 2025-10-24

### Added
- Advanced PDF OCR converter (pdf_to_txt_new.py) with batch processing
- Cost tracking functionality ($0.001/page) with CSV logging
- Smart skip logic to avoid re-processing already converted PDFs
- Interactive confirmation for single file re-processing with unique naming
- Recursive directory support for processing all subdirectories
- Audio transcription tool (transcribe_audio.py) using Voxtral models
- Basic PDF OCR converter (pdf_to_txt.py) for single file processing
- Comprehensive README documentation in English
- .gitignore for proper file exclusions
- requirements.txt for dependency management
- .env.example template for API key configuration

### Features
- Batch processing of PDF files and entire directories
- Cost calculation and tracking with automatic CSV logging
- Smart file management with skip and re-processing logic
- Multilingual support for Arabic and English text
- Audio file transcription with multiple format support
- Command-line interface for easy usage
- UTF-8 encoding support for proper text handling
