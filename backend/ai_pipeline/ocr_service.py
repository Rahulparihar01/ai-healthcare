import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

def extract_raw_text(file_path: str) -> str:
    """
    Extracts raw text from a PDF or Image using PyMuPDF or pytesseract.
    """
    raw_text = ""
    
    if file_path.lower().endswith(".pdf"):
        try:
            # Extract text using PyMuPDF
            doc = fitz.open(file_path)
            for page in doc:
                text = page.get_text()
                raw_text += text + "\n"
            doc.close()
            
            # If the PDF is scanned and has no text, PyMuPDF might return empty strings.
            # We could fallback to OCR, but for simplicity, we assume digital PDFs mostly.
        except Exception as e:
            print(f"PyMuPDF Extraction failed: {e}")
            
    else:
        # It's an image file
        try:
            image = Image.open(file_path)
            raw_text = pytesseract.image_to_string(image)
        except Exception as e:
            print(f"pytesseract Extraction failed: {e}")
            
    return raw_text.strip()
