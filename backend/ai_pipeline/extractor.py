import os
import json
import base64
from openai import OpenAI
from dotenv import load_dotenv

# Load env variables (expects OPENAI_API_KEY)
load_dotenv()

# We will use pdf2image to convert PDFs to images if necessary, 
# but for MVP we assume the file could be an image or we just send it as vision
from pdf2image import convert_from_path

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_information(file_path: str) -> dict:
    """
    Uses OpenAI GPT-4o (Vision) to extract medical information from the document.
    """
    client = OpenAI() # Automatically reads OPENAI_API_KEY from environment
    print(f"Processing document with AI: {file_path}")
    
    # Simple check: if it's a PDF, we convert the first page to a temporary image
    temp_image_path = None
    if file_path.lower().endswith(".pdf"):
        print("Converting PDF to Image...")
        pages = convert_from_path(file_path, 200, first_page=1, last_page=1)
        temp_image_path = file_path + ".jpg"
        pages[0].save(temp_image_path, 'JPEG')
        image_to_process = temp_image_path
    else:
        image_to_process = file_path
        
    base64_image = encode_image(image_to_process)
    
    # We use Structured Outputs via Function Calling / JSON mode
    schema = {
        "type": "object",
        "properties": {
            "report_category": {
                "type": "string",
                "enum": ["Blood Report", "MRI", "CT Scan", "X-Ray", "ECG", "Ultrasound", "Prescription", "Discharge Summary", "Unknown"]
            },
            "patient_name": {"type": "string"},
            "age": {"type": "number"},
            "conditions": {"type": "array", "items": {"type": "string"}},
            "medications": {"type": "array", "items": {"type": "string"}},
            "allergies": {"type": "array", "items": {"type": "string"}},
            "summary": {"type": "string", "description": "A 2-3 sentence clinical summary of the document."}
        },
        "required": ["report_category", "patient_name", "conditions", "medications", "allergies", "summary"]
    }

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a highly accurate medical data extraction AI. You will be provided an image of a medical document (lab report, prescription, etc.). Read the document and extract the information precisely into the required JSON structure. If a field like 'allergies' is not present in the document, return an empty array."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "medical_report_extraction",
                    "schema": schema,
                    "strict": True
                }
            },
            max_tokens=1000
        )
        
        raw_json = response.choices[0].message.content
        extracted_data = json.loads(raw_json)
        
    except Exception as e:
        print(f"OpenAI Extraction failed: {e}")
        extracted_data = {
            "report_category": "Unknown",
            "patient_name": "Error reading document",
            "age": 0,
            "conditions": [],
            "medications": [],
            "allergies": [],
            "summary": f"Failed to parse document: {str(e)}"
        }
    finally:
        # Cleanup temporary image if we made one from a PDF
        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path)
            
    return extracted_data
