# DeepSeek OCR on Simplismart

Process documents at lightning speed with DeepSeek OCR on Simplismart - achieving **800 tokens/second** for accurate text extraction from images, receipts, invoices, and PDFs.

## 📖 Companion Blog

For detailed instructions, check out our companion blog:  
**[DeepSeek OCR on Simplismart: Lightning-Fast Document Processing at 800 Tokens/Second](https://www.simplismart.ai/blog/deepseek-ocr-api-simplismart)**

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Simplismart account and API key ([Sign up here](https://app.simplismart.ai))

### Installation

1. **Clone the repository** (if not already done):
```bash
git clone https://github.com/simpli-smart/cookbook.git
cd cookbook/deepseek-ocr
```

2.  **Create and activate a virtual environment (optional but recommended):**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure API credentials**:
```bash
cp .env-template .env
```

Edit `.env` and add your credentials:
```
SIMPLISMART_API_KEY=your_api_key_here
SIMPLISMART_BASE_URL=your_base_url_here
DEFAULT_HEADERS_ID=your_default_headers_id_here
```

Get your API details from the [Simplismart Playground](https://playground.simplismart.ai) → Select DeepSeek OCR → "Get API details" → "API Usage" tab.

## 📝 Usage Examples

### 1. OCR on Local Images
Extract text from images stored on your machine:
```bash
python ocr_local_image.py
```

### 2. OCR on Image URLs
Process images from publicly accessible URLs:
```bash
python ocr_image_url.py
```

### 3. PDF Text Extraction
Convert multi-page PDFs to text with automatic page handling:
```bash
python pdf_to_txt.py
```


## 🎯 Key Features

- **Lightning Fast**: 800 tokens/second processing speed
- **Context-Aware**: Understands document structure and layout
- **Multilingual**: Supports 100 languages
- **Handwriting Recognition**: Reliable extraction from handwritten documents
- **Easy Integration**: Uses familiar OpenAI SDK interface

## 📚 Resources

- **[Companion Blog Post](https://www.simplismart.ai/blog/deepseek-ocr-api-simplismart)** - Detailed tutorial and examples
- **[DeepSeek OCR Paper](https://arxiv.org/abs/2510.18234)** - Technical architecture details
- **[Simplismart Documentation](https://docs.simplismart.ai)** - Complete API reference
- **[Simplismart Playground](https://playground.simplismart.ai)** - Interactive playground to experiment with different models across modalities.

## Attributions

- Walmart Receipt Sample: https://www.pinterest.com/pin/free-walmart-receipt-template--555209460330534609/
- DeepSeek OCR Paper: https://arxiv.org/abs/2510.18234

## 💬 Support

Have questions? [Contact us](https://www.simplismart.ai/contact) or check our [documentation](https://docs.simplismart.ai).