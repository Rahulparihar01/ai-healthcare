import json
from openai import OpenAI
from langsmith.wrappers import wrap_openai
from langsmith import traceable
import os
from dotenv import load_dotenv
load_dotenv()
@traceable(name="Generate Clinical Summary")
def generate_clinical_summary(document_type: str, extracted_text: str) -> str:
    """
    Generates a document-type-specific clinical summary using LLM.
    """
    client = wrap_openai(OpenAI(api_key=os.environ.get("OPENAI_API_KEY")))
    
    prompts = {
        "blood_test": "You are a medical assistant. Summarize the following blood test results. Highlight any abnormal biomarkers, out-of-range values, and state if everything else is normal.",
        "lab_report": "You are a medical assistant. Summarize the following lab report results. Highlight any abnormal biomarkers, out-of-range values, and state if everything else is normal.",
        "mri": "You are a medical assistant. Summarize the following MRI report. Focus on clinical impressions, anomalies, and recommendations.",
        "ct_scan": "You are a medical assistant. Summarize the following CT scan report. Focus on clinical impressions, anomalies, and recommendations.",
        "ecg": "You are a medical assistant. Summarize the following ECG report. Focus on clinical impressions, anomalies, and recommendations.",
        "discharge_summary": "You are a medical assistant. Summarize the following discharge summary. Summarize the diagnosis, prescribed treatments, and follow-up care.",
        "prescription": "You are a medical assistant. Summarize the following prescription. Highlight the prescribed medications, dosages, and instructions.",
    }
    
    system_prompt = prompts.get(document_type.lower(), "You are a medical assistant. Summarize the following medical document.")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Document text:\n{extracted_text}"}
            ],
            max_tokens=250,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI Summarization failed: {e}")
        return "AI processing failed to generate a summary."

def extract_summary(extracted_data: dict) -> str:
    """
    Extracts the clinical summary from the structured JSON output.
    """
    return extracted_data.get("summary", "AI processing completed without summary.")
