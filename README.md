# Mistral OCR - Advanced PDF Processing

## 🌍 مقدمة باللغة العربية

هذا المشروع يوفر سكريبتات Python متقدمة للتفاعل مع Mistral AI API لمعالجة OCR لملفات PDF، مع إمكانيات المعالجة الدفعية وتتبع التكاليف. يدعم النظام معالجة النصوص العربية والمستندات متعددة اللغات بكفاءة عالية.

This project provides advanced Python scripts to interact with the Mistral AI API for PDF OCR processing, with batch processing and cost tracking capabilities.

## 🚀 `pdf_to_txt_new.py` - Advanced PDF OCR Converter

**Enhanced PDF to Markdown converter with batch processing, cost tracking, and smart file management.**

### ✨ Key Features

- **🔄 Batch Processing**: Process single files or entire directories recursively
- **💰 Cost Tracking**: Automatic cost calculation ($0.001/page) with detailed CSV logging
- **🧠 Smart Skip Logic**: Automatically skips already processed PDFs
- **🔄 Re-processing**: Interactive confirmation for single file re-processing with unique naming
- **📁 Recursive Directory Support**: Processes PDFs in all subdirectories
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

#### Single File Mode
- Checks if PDF has already been processed
- Asks for confirmation: `"File 'document.pdf' has already been processed. Re-process it? (y/N):"`
- Creates uniquely named outputs: `document_1.md`, `document_2.md`, etc.

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
│   ├── report.md                    # OCR output
│   ├── data.pdf
│   └── data.md                      # OCR output
└── subfolder/
    ├── analysis.pdf
    └── analysis.md                  # OCR output
```

## 📄 `pdf_to_txt.py` - Basic PDF OCR Converter

**Legacy single-file PDF to text converter.**

### Usage
```bash
python pdf_to_txt.py <path_to_pdf_file>
```

## 🛠️ Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/mistral-ocr.git
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
