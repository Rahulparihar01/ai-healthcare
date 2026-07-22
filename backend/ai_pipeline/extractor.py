import json
from openai import OpenAI
from dotenv import load_dotenv

from .schemas import VERSIONED_EXTRACTION_SCHEMA_1_0
from .prompts import get_extraction_prompt
from .ocr_service import extract_raw_text
from .document_classifier import classify_document
from .entity_extractor import extract_entities
from .summarizer import extract_summary
from .clinical_validator import validate_extraction

load_dotenv()

def extract_information(file_path: str, status_callback=None) -> dict:
    """
    Orchestrates the two-step AI medical data extraction pipeline.
    """
    if status_callback:
        status_callback("Extracting Text (OCR)...")
        
    print(f"Extracting Raw Text from: {file_path}")
    raw_text = extract_raw_text(file_path)
    
    if not raw_text:
        return {
            "schema_version": "1.0",
            "document_type": "Unknown",
            "confidence": 0.0,
            "patient": {},
            "doctor": {},
            "hospital": {},
            "diagnoses": [],
            "medications": [],
            "lab_results": [],
            "recommendations": [],
            "follow_up": {},
            "summary": "Failed to extract text from the document. The document might be empty or unreadable.",
            "raw_text": ""
        }

    if status_callback:
        status_callback("Classifying Document Type...")
        
    print("Classifying Document Type with LLM...")
    
    # Step 1: Classification
    document_type, confidence = classify_document(raw_text)
    print(f"Document classified as: {document_type} (Confidence: {confidence})")
    
    if status_callback:
        status_callback(f"Extracting {document_type} Data...")
        
    # Step 2: Specialized Extraction
    client = OpenAI()
    system_prompt = get_extraction_prompt(document_type)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Here is the raw text from the medical document:\n\n{raw_text}"
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "medical_report_extraction",
                    "schema": VERSIONED_EXTRACTION_SCHEMA_1_0,
                    "strict": True
                }
            },
            max_tokens=1500
        )
        
        raw_json = response.choices[0].message.content
        extracted_data = json.loads(raw_json)
        
        if status_callback:
            status_callback("Validating Clinical Data...")
            
        # 3. Clinical Validation
        is_valid = validate_extraction(extracted_data, confidence)
        if not is_valid:
            print("Warning: Extraction failed clinical validation.")
            
        if status_callback:
            status_callback("Generating Unified Summary...")
            
        # Assemble Final Unified Output by injecting raw_text, version, and type
        final_output = {
            "schema_version": "1.0",
            "document_type": document_type,
            "confidence": confidence,
            "is_clinically_valid": is_valid,
            "raw_text": raw_text,
            **extracted_data
        }
        
    except Exception as e:
        print(f"OpenAI Extraction failed: {e}")
        final_output = {
            "schema_version": "1.0",
            "document_type": document_type,
            "confidence": confidence,
            "is_clinically_valid": False,
            "patient": {},
            "doctor": {},
            "hospital": {},
            "diagnoses": [],
            "medications": [],
            "lab_results": [],
            "recommendations": [],
            "follow_up": {},
            "summary": f"Failed to parse text: {str(e)}",
            "raw_text": raw_text
        }
            
    return final_output
