import json
from openai import OpenAI
from langsmith.wrappers import wrap_openai
from langsmith import traceable
from .schemas import CLASSIFICATION_SCHEMA

@traceable(run_type="chain", name="Classify Document")
def classify_document(raw_text: str) -> tuple[str, float]:
    """
    Uses a fast LLM call (gpt-4o-mini) to classify the document type from the raw text.
    Returns a tuple of (document_type, confidence_score).
    """
    client = wrap_openai(OpenAI())
    
    # We don't need the entire document to classify it. The first 1500 chars is usually enough.
    text_sample = raw_text[:1500]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical document classifier. Read the text and identify the document type."
                },
                {
                    "role": "user",
                    "content": f"Text sample:\n\n{text_sample}"
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "document_classification",
                    "schema": CLASSIFICATION_SCHEMA,
                    "strict": True
                }
            },
            max_tokens=100
        )
        
        raw_json = response.choices[0].message.content
        data = json.loads(raw_json)
        return data.get("document_type", "Unknown"), data.get("confidence", 0.0)
        
    except Exception as e:
        print(f"Classification failed: {e}")
        return "Unknown", 0.0
