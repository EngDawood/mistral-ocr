# Mistral OCR - Advanced PDF Processing & Audio Transcription

## 🌍 مقدمة باللغة العربية

هذا المشروع يوفر سكريبتات Python متقدمة للتفاعل مع Mistral AI API لمعالجة OCR لملفات PDF، مع إمكانيات المعالجة الدفعية وتتبع التكاليف. يدعم النظام معالجة النصوص العربية والمستندات متعددة اللغات بكفاءة عالية، بالإضافة إلى تحويل الصوت إلى نص باستخدام نماذج Voxtral المتقدمة.

This project provides advanced Python scripts for OCR processing, PDF text extraction, audio transcription, and document processing using Mistral AI API. Features batch processing, cost tracking, multilingual support, and speech-to-text capabilities.

## 📸 Example Input & Output Screenshots

![OCR Processing Example](screenshot/input.png)

### Example Output Files
See the example output screenshots in the `screenshot/` directory with `input.png`, `output1.png`, and `output2.png` showing Arabic text processing results.
```markdown
محمد سيد سليمان: أثر العلاج بالحركة في تخفيف شدة أعراض اضطراب تشتت الانتباه المصحوب بفرط الحركة وتحسين سرعة المعالجة لدى الأطفال بالمرحلة الابتدائية

محمد سيد سعيد سليمان<br>كلية التربية والآداب- جامعة الحدود الشمالية<br>قدم المنشر 1438/3/29هـ - وفيل 13 /6/ 1438م

المستخلص: هدفت الدراسة الحالية إلى الكشف عن أثر التمارين البدنية المتمثلة في الرياضة الذهنية من خلال التدريب الحركي في التخفيف من شدة أعراض اضطراب تشتت الانتباه وفرط الحركة (اللانتباهية، فرط الحركة، الاندفاعية)، وفي تحسين سرعة المعالجة لدى الأطفال ذوي اضطراب تشتت الانتباه وفرط الحركة، تكونت عينة الدراسة من (23) طالباً في الصفوف الدراسية من الثاني وحتى السادس الابتدائي، ثم تقسيمهم إلى عينتين: تجريبية (12) طالباً، وضابطة (11) طالبًا، استخدم الباحث ثلاث أدوات للدراسة شملت: قائمة التعرف على اضطراب تشتت الانتباه وفرط الحركة ، مقياس اضطراب تشتت الانتباه وفرط الحركة، اختبارات سرعة المعالجة، حركات الرياضة الذهنية. استخدم الباحث المنهج شبه التجريبي، أشارت نتائج الدراسة إلى : وجود فروق دالة إحصائيًا بين متوسطي درجات المحموعتين التجريبية والضابطة في بُعد تشتت الانتباه لصالح المحموعة التجريبية، عدم وجود فروق دالة إحصائيًا بين متوسطي درجات المحموعتين التجريبية والضابطة في بُعدي الفرط الحركي والاندفاعية ، وجود فروق دالة إحصائياً بين متوسطي درجات المحموعتين التجريبية والضابطة في اختبارات سرعة المعالجة والدرجة الكلية لصالح المحموعة التجريبية، كما أشارت النتائج إلى وجود فروق ذات دلالة إحصائية بين متوسطي درجات المحموعة التجريبية في التطبيقين القبلي والبعدي في بعد تشتت الانتباه والدرجة الكلية لصالح التطبيق البعدي، وعدم وجود فروق ذات دلالة إحصائية بين متوسطي درجات المحموعة التجريبية في التطبيقين القبلي والبعدي في أبعاد فرط الحركة والاندفاعية، وأشارت إلى وجود فروق ذات دلالة إحصائية بين متوسطي درجات المحموعة التجريبية في التطبيقين القبلي والبعدي في اختبارات سرعة المعالجة والدرجة الكلية لصالح التطبيق البعدي.

الكلمات المفتاحية : النشاط البدني، سرعة معالجة المعلومات، تشتت الانتباه، فرط الحركة، الاندفاعية.

 المقدمة 

يعد اضطراب تشتت الانتباه المصحوب بفرط الحركة ADHD من بين الاضطرابات النفسية الأكثر شيوعًا لدى الأطفال، إذ يعدٌّ اضطراباً سلوكياً عصبياً يتصف بمستويات غير ملائمة من اللانتباهية والاندفاعية والنشاط الزائد، ويؤثر هذا الاضطراب في 3-7\% من الأطفال في سن المدرسة، وينتشر بين الإناث و الذكور بمعدل يتراوح بين 3:1 الى 9:2 (2011, American Academy of Pediatrics).

وأصبح مثل هذا الاضطراب محط اهتمام الباحثين والمربين والقائمين على تربية الطفل، نظراً للآثار السلبية التي يحدثها في الطفل على المستوى الاجتماعي والانفعالي والمعرفي والصحي والأسري (Birmbaum,Kessler\&lowe,2005)، وهذه الآثار السلبية ناتجة عن الإفراط في الحركة المصحوب بالسلوك الاندفاعي، بالإضافة إلى نقص الانتباه مما يؤدي إلى التعرض لكثير من المواقف الصعبة أو الخطرة دون تفكير، فضلاً عما يسببه هذا الاضطراب من عبء ماليٍ للأنظمة المدرسية والأسرية والصحية الحكومية، إذ يتطلب مواجهة السلوكيات المزعجة الناتجة عنه، زيادة الحاجة إلى تقديم خدمات تعليمية مختلفة، مثل البرامج التربوية الفردية والإرشاد والتقويم التربوي.

وقد أشارت نتائج العديد من الدراسات إلى أن التكلفة المالية الطبية السنوية للأطفال ذوي هذا الاضطراب أعلى من مثيلتها لدى الأطفال العاديين (Guevera, Lozano, Wickizer, Mell \& Gephart, 2001; Swensen, Birnbaum, Secnik, Marynhenko, Greenberg \& Claxton,2003).

وتستخدم برامج علاجية عديدة تتنوع بين الدوائية والسلوكية لعلاج هذا الاضطراب. إذ يمثل العلاج بالأدوية المنشطة الطريقة الأكثر شيوعًا لعلاج الأعراض الأساسية لهذا الاضطراب، فهذه الأدوية الفعالة تخفف أعراض الاضطراب عن طريق تأثيرها في أنظمة موصلات عصبية خاصة specific

 (NE)

والدوبامين (DA) والمرتبطة بالكاثيكولامين المرتبط بالدوائر العصبية بمنطقة القشرة تحت الجبهية fronto-subcortical. ورغم ذلك فإن ما يقرب من $30 \%$ من الأطفال لا تستجيب للعلاج الدوائي، أو غير قادرين على تحمل الآثار الجانبية المصاحبة له مثل الأرق وفقدان الشهية وتأخر النمو والصداع وآلام البطن وفقدان الوزن والتش痉ات اللاإرادية (Connor,2006;Wigal,Emmerson,Gehricke\&Galassetti,200 (Connor,2006;Wigal,Emmerson,Gehricke\&Galassetti,200) (2014 ,2011).

وأشارت دراسة (Biederman, Monuteaux, Spencer,Wilens\& Faraone,2009) أن الأطفال ذوي اضطراب ADHD أكثر عرضة لمشاكل تعاطي المخدرات لما لهذه الأدوية المنشطة من تأثيرات بيولوجية ينتج عنها تعلق بدني بها، علاوة على أن فوائد هذه الأدوية المحفزة Stimulant medication لا تمتد لمدى زمني طويل
(Hnshaw\&Arnold,2015;Vysniauske,Verburgh,O- (osterlaan\&Molendijk,2016، كما أن فعاليته محدودة بفترة الإدارة النشطة للدواء Chronis, Jones\&Raggi,2006;Pelham\&Fabiano,2008) وتعدُّ التدخلات السلوكية مثل برامج التدريب السلوكي للوالدين، والإدارة السلوكية للطلاب في الصف من المداخل المستندة إلى أدلة تجريبية (Pelham\&Fabiano,2008، ورغم أنها تتسبب في حدوث تقدمٍ في بعض المجالات المحددة والتي لا يصلح لها العلاج الدوائي إلا أن هذا التقدم يعب استمراره بعد انتهاء فترة التدخل السلوكي (Chronis,et al., 2006)، أكثر من ذلك التدخلات السلوكية صعبة نسبياً في التنفيذ ومكلفة من حيث النفقات المالية والزمنية، كما أنها قد تكون أقل فعالية من الأدوية (MTA Cooperative Group,1999) وتشكل عبثاً ثقيلاً على القائمين على تنفيذها كالمعلمين والوالدين، كما تتطلب التزاماً طويل الأمد للحفاظ على مستويات عالية من الدقة والشدة

```

### 📝 Editing Arabic Markdown
For editing Arabic markdown content, use the online Arabic markdown editor at https://app.dawin.io/ - "الآن محرّر دوّن بحلّة جديدة , وتجربة لم تعهدها من قبل , ميزات عديدة بانتظارك! دَوِّن، هو محرّر نصوص عربي لتنسيقات ماركداون (Markdown) صمّم لحلّ مشكلة عدم توفر أي محرر نصوص متقدم يدعم اللغة العربية والاتجاه (Right to left). طوّر بأياد عربية خالصة تكّن للغة العربية احتراما وإجلالًا."


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
