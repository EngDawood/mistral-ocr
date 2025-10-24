# Mistral OCR - Advanced PDF Processing & Audio Transcription

## 🌍 مقدمة باللغة العربية

هذا المشروع يوفر سكريبتات Python متقدمة للتفاعل مع Mistral AI API لمعالجة OCR لملفات PDF، مع إمكانيات المعالجة الدفعية وتتبع التكاليف. يدعم النظام معالجة النصوص العربية والمستندات متعددة اللغات بكفاءة عالية، بالإضافة إلى تحويل الصوت إلى نص باستخدام نماذج Voxtral المتقدمة.

This project provides advanced Python scripts for OCR processing, PDF text extraction, audio transcription, and document processing using Mistral AI API. Features batch processing, cost tracking, multilingual support, and speech-to-text capabilities.

## 🚀 `pdf_to_txt_new.py` - Advanced PDF OCR Converter

**Enhanced PDF to Markdown converter with batch processing, cost tracking, and smart file management.**

### ✨ Key Features

- **🔄 Batch Processing**: Process single files or entire directories recursively
- **💰 Cost Tracking**: Automatic cost calculation ($0.001/page) with detailed CSV logging
- **🧠 Smart Skip Logic**: Automatically skips already processed PDFs
- **🔄 Re-processing**: Interactive confirmation for single file re-processing with unique naming
- **📁 Recursive Directory Support**: Processes PDFs in all subdirectories
- **📂 In-Place Processing**: Processes files from any directory and outputs Markdown files to the same location
- **📊 Comprehensive Logging**: Tracks filename, pages, timestamps, costs, and output paths

### 📋 Usage Examples

#### Single File Processing

```bash
# Basic usage
python pdf_to_txt_new.py document.pdf

# With custom tracking
python pdf_to_txt_new.py document.pdf --track-file my_log.csv --track-format csv
```

#### Directory Processing

```bash
# Process all PDFs in directory (recursive)
python pdf_to_txt_new.py ./documents/

# Process with custom tracking
python pdf_to_txt_new.py ./pdfs --track-file batch_log.txt --track-format txt
```

### 🎯 Processing Behavior

#### Directory Mode

- Recursively finds all `*.pdf` files
- Skips PDFs that already have corresponding `.md` files
- Shows progress: `"Skipping 3 already processed PDF(s), 2 remaining"`
- Processes only new files
- **Outputs Markdown files to the same directory as the source PDFs**

#### Single File Mode

- Checks if PDF has already been processed
- Asks for confirmation: `"File 'document.pdf' has already been processed. Re-process it? (y/N):"`
- Creates uniquely named outputs: `document_1.md`, `document_2.md`, etc.
- **Outputs the Markdown file to the same directory as the source PDF**

### 📊 Cost Tracking

**Automatic Tracking File**: `ocr_usage_tracking.csv` (created next to the script)

```csv
filename,page_count,processing_date,cost_usd,output_path
document.pdf,6,2025-10-24T22:30:38,0.0060,/path/document.md
batch_file.pdf,25,2025-10-24T22:31:15,0.0250,/path/batch_file.md
```

**Cost Calculation**: `$0.001 × page_count`
- 6 pages = $0.0060
- 100 pages = $0.1000
- 1000 pages = $1.0000

### 📁 Output Structure

```
your_directory/
├── pdf_to_txt_new.py
├── ocr_usage_tracking.csv          # Automatic cost tracking
├── documents/
│   ├── report.pdf
│   ├── report.md                    # OCR output (same directory)
│   ├── data.pdf
│   └── data.md                      # OCR output (same directory)
└── subfolder/
    ├── analysis.pdf
    └── analysis.md                  # OCR output (same directory)
```

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

3. **Set up your API key:**
   Copy the example environment file and fill in your API key:
   ```bash
   cp .env.example .env
   ```

   Then edit `.env` with your actual Mistral API key:
   ```
   MISTRAL_API_KEY=your_actual_api_key_here
   ```

   Get your API key from: https://console.mistral.ai/api-keys

## 📋 Requirements

- Python 3.8+
- Mistral AI API key
- Required packages: `mistralai`, `python-dotenv`

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
