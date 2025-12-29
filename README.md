# Mistral OCR - Advanced PDF Processing & Audio Transcription

## 🌍 مقدمة باللغة العربية

هذا المشروع يوفر سكريبتات Python متقدمة للتفاعل مع Mistral AI API لمعالجة OCR لملفات PDF، مع إمكانيات المعالجة الدفعية وتتبع التكاليف. يدعم النظام معالجة النصوص العربية والمستندات متعددة اللغات بكفاءة عالية، بالإضافة إلى تحويل الصوت إلى نص باستخدام نماذج Voxtral المتقدمة.

This project provides advanced Python scripts for OCR processing, PDF text extraction, audio transcription, and document processing using Mistral AI API. Features batch processing, cost tracking, multilingual support, and speech-to-text capabilities.

### 📝 Editing Arabic Markdown

For editing Arabic markdown content, use the online Arabic markdown editor at https://app.dawin.io/ - "الآن محرّر دوّن بحلّة جديدة , وتجربة لم تعهدها من قبل , ميزات عديدة بانتظارك! دَوِّن، هو محرّر نصوص عربي لتنسيقات ماركداون (Markdown) صمّم لحلّ مشكلة عدم توفر أي محرر نصوص متقدم يدعم اللغة العربية والاتجاه (Right to left). طوّر بأياد عربية خالصة تكّن للغة العربية احتراما وإجلالًا."

## 🚀 `pdf_to_txt_new.py` - Advanced PDF OCR Converter

**Enhanced PDF to Text/Markdown converter with batch processing, URL support, automatic dependency management, and smart file management.**

### ✨ Key Features

- **📄 Flexible Output Formats**: Default plain text (`.txt`) or markdown (`.md`) with `--md` flag
- **🌐 URL Support**: Download and process PDFs directly from URLs with auto-cleanup
- **🔄 Batch Processing**: Process single files or entire directories recursively
- **🧠 Smart Skip Logic**: Only skips PDFs with existing files of the target extension
- **🔄 Re-processing**: Interactive confirmation for single file re-processing with unique naming
- **🔑 Custom API Key**: Use `--api-key` parameter or environment variable
- **♻️ Auto-Cleanup**: Downloaded PDFs are deleted after OCR unless `--keep` flag is used
- **📦 Dependency Checking**: Automatically checks and offers to install missing packages
- **📁 Recursive Directory Support**: Processes PDFs in all subdirectories
- **📂 In-Place Processing**: Outputs files to the same location as source PDFs

### 📋 Usage Examples

#### Single File Processing

```bash
# Process to plain text (default)
python pdf_to_txt_new.py document.pdf

# Process to markdown
python pdf_to_txt_new.py document.pdf --md

# Explicit plain text
python pdf_to_txt_new.py document.pdf --txt

# Use custom API key
python pdf_to_txt_new.py document.pdf --api-key your_api_key_here
```

#### URL Processing

```bash
# Download and process PDF from URL (auto-cleanup)
python pdf_to_txt_new.py --url https://example.com/document.pdf

# Download and convert to markdown
python pdf_to_txt_new.py --url https://example.com/document.pdf --md

# Download and keep the PDF file after OCR
python pdf_to_txt_new.py --url https://example.com/document.pdf --keep
```

#### Directory Processing

```bash
# Process all PDFs in directory (recursive) to text
python pdf_to_txt_new.py ./documents/

# Process all PDFs to markdown
python pdf_to_txt_new.py ./documents/ --md
```

### 🎯 Processing Behavior

#### Directory Mode

- Recursively finds all `*.pdf` files
- **Smart Skip Logic**: Only skips PDFs with existing files of the **target extension**
  - Example: If `file.txt` exists and you run with `--md`, it will still process
- Shows progress: `"Skipping 3 PDF(s) with existing .txt files, 2 remaining"`
- Processes only new files or files without target extension
- **Outputs files to the same directory as the source PDFs**

#### Single File Mode

- Checks if PDF has output file with **target extension only**
  - Example: If `file.txt` exists and you run with `--md`, no confirmation needed
- Asks for confirmation only when target extension file exists
- Creates uniquely named outputs: `document_1.txt`, `document_2.md`, etc.
- **Outputs the file to the same directory as the source PDF**

#### URL Mode

- Downloads PDF from URL to current directory
- Processes downloaded PDF like a local file
- **Auto-cleanup**: Deletes downloaded PDF after OCR (unless `--keep` flag is used)
- Maintains all other processing features

### 📦 Automatic Dependency Management

The script automatically checks for required packages and offers to install them:

```text
======================================================================
ERROR: Missing required packages
======================================================================
  ✗ python-dotenv
  ✗ mistralai

To install missing packages, run one of these commands:
  pip install python-dotenv mistralai
  pip install -r requirements.txt

Would you like to install them now? (y/N):
```

**Features:**
- ✅ Automatic detection of missing packages
- ✅ Interactive installation prompt
- ✅ Clear installation instructions
- ✅ Safe permission-based installation
- ✅ Silent operation when packages are installed

### 📁 Output Structure

```text
your_directory/
├── pdf_to_txt_new.py
├── documents/
│   ├── report.pdf
│   ├── report.txt                   # Default: plain text output
│   ├── data.pdf
│   └── data.md                      # With --md flag
└── subfolder/
    ├── analysis.pdf
    ├── analysis.txt                 # Default output
    └── downloaded_document.pdf      # URL downloads (deleted unless --keep)
```

**Output Format Examples:**
- `python pdf_to_txt_new.py doc.pdf` → `doc.txt` (default)
- `python pdf_to_txt_new.py doc.pdf --md` → `doc.md`
- `python pdf_to_txt_new.py --url https://example.com/file.pdf` → `file.txt` (PDF deleted after)
- `python pdf_to_txt_new.py --url https://example.com/file.pdf --keep` → `file.txt` + `file.pdf` (kept)

### 🎛️ Command Line Options

```bash
python pdf_to_txt_new.py [input] [options]

Arguments:
  input                 Path to PDF file or directory (optional with --url)

Options:
  --url URL            Download and process PDF from URL
  --md                 Convert to markdown instead of plain text
  --txt                Explicitly convert to plain text (default)
  --api-key KEY        Use custom Mistral API key
  --keep               Keep downloaded PDF file after processing
  --model MODEL        OCR model name (default: mistral-ocr-latest)
  -h, --help           Show help message
```

**Common Use Cases:**

| Command | Description |
|---------|-------------|
| `pdf_to_txt_new.py file.pdf` | Process to plain text (default) |
| `pdf_to_txt_new.py file.pdf --md` | Process to markdown |
| `pdf_to_txt_new.py --url https://example.com/doc.pdf` | Download, OCR, delete PDF |
| `pdf_to_txt_new.py --url URL --keep` | Download, OCR, keep PDF |
| `pdf_to_txt_new.py ./docs/` | Process all PDFs in directory |
| `pdf_to_txt_new.py file.pdf --api-key KEY` | Use custom API key |

## 📄 `pdf_to_txt.py` - Basic PDF OCR Converter

**Legacy single-file PDF to text converter.**

### Usage

```bash
python pdf_to_txt.py <path_to_pdf_file>
```

## 🎵 `transcribe_audio.py` - Audio Transcription Tool

**Advanced audio file transcription using Mistral AI's Voxtral models for high-quality speech-to-text conversion.**

### ✨ Key Features

- **🎯 High-Quality Transcription**: Uses Mistral's Voxtral models for accurate speech recognition
- **🌍 Multilingual Support**: Supports multiple languages including Arabic, English, and more
- **📁 Simple File Processing**: Process any audio file with automatic text output
- **🔧 Command-Line Interface**: Easy-to-use CLI with file path input
- **📝 Automatic Output**: Saves transcription to `.txt` file with same base name
- **🛡️ Error Handling**: Comprehensive error handling with user-friendly messages

### 📋 Usage Examples

#### Single Audio File Transcription

```bash
# Basic usage - transcribe any audio file
python transcribe_audio.py audio.ogg
python transcribe_audio.py recording.mp3
python transcribe_audio.py speech.wav
```

### 🎯 Processing Behavior

- **Input**: Any audio file (`.ogg`, `.mp3`, `.wav`, `.m4a`, `.flac`, etc.)
- **Output**: Creates a `.txt` file with the same base name in the same directory
- **Model**: Uses `voxtral-mini-latest` for optimal transcription quality
- **Encoding**: UTF-8 encoding for proper multilingual text support

### 📁 Output Example

```
your_directory/
├── transcribe_audio.py
├── speech.ogg
└── speech.txt              # Transcription output
```

## 🛠️ Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/EngDawood/mistral-ocr.git
   cd mistral-ocr
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get your free Mistral API key:**
   - Visit [Mistral AI Console](https://console.mistral.ai/api-keys)
   - Sign up for a free account
   - Navigate to API Keys section
   - Create a new API key
   - Copy the API key (keep it secure)

4. **Set up your API key:**
   Copy the example environment file and fill in your API key:
   ```bash
   cp .env.example .env
   ```

   Then edit `.env` with your actual Mistral API key:
   ```
   MISTRAL_API_KEY=your_actual_api_key_here
   ```

## 📋 Requirements

- Python 3.8+
- Mistral AI API key (get free at [console.mistral.ai](https://console.mistral.ai/api-keys))
- Required packages: `mistralai`, `python-dotenv` (auto-checked by `pdf_to_txt_new.py`)

## 🔗 Mistral OCR API Information

**Free Tier**: Mistral offers general OCR processing for up to 1,000 pages for free.

**API Limitations**:
- Uploaded document files must not exceed 50 MB in size
- Documents should be no longer than 1,000 pages

**OCR Resources & Cookbooks**:
- [Tool Usage Guide](https://colab.research.google.com/github/mistralai/cookbook/blob/main/mistral/ocr/tool_usage.ipynb)
- [Batch OCR Guide](https://colab.research.google.com/github/mistralai/cookbook/blob/main/mistral/ocr/batch_ocr.ipynb)

## 🌍 Arabic Language Support

This project fully supports Arabic text processing and multilingual documents. The system has been tested with:

- **Mixed Arabic and English texts**
- **UTF-8 encoding for Arabic content**
- **Proper right-to-left text direction handling**

### 📝 Important Notes for Arabic Users

- Ensure PDF files are saved with UTF-8 encoding
- The system preserves correct Arabic text ordering
- Multilingual documents can be processed efficiently
- Arabic README available: [README_ar.md](README_ar.md)

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is open source. Please check the license file for details.
