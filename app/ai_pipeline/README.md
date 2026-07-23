# HealthID AI - OCR & Intelligence Pipeline

This directory contains the Python backend logic for parsing medical documents, extracting text using OCR, and generating medical insights using LLMs.

## Setup

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the prototype extractor:
   ```bash
   python extractor.py path/to/sample/report.pdf
   ```

## Next Steps
- Integrate real OCR (Tesseract / AWS Textract).
- Hook up OpenAI API for extracting structured conditions and medications.
