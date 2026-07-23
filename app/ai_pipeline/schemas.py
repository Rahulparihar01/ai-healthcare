SUPPORTED_DOCUMENT_TYPES = [
    "Blood Report",
    "CBC",
    "Lipid Profile",
    "Prescription",
    "Discharge Summary",
    "MRI Report",
    "CT Report",
    "X-Ray Report",
    "ECG",
    "Echo",
    "Referral Letter",
    "Clinical Notes",
    "Vaccination Record",
    "Unknown"
]

CLASSIFICATION_SCHEMA = {
    "type": "object",
    "properties": {
        "document_type": {
            "type": "string",
            "enum": SUPPORTED_DOCUMENT_TYPES
        },
        "confidence": {
            "type": "number",
            "description": "Confidence score between 0.0 and 1.0"
        }
    },
    "required": ["document_type", "confidence"]
}

VERSIONED_EXTRACTION_SCHEMA_1_0 = {
    "type": "object",
    "properties": {
        "patient": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"},
                "gender": {"type": "string"},
                "patient_id": {"type": "string"}
            }
        },
        "doctor": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "specialty": {"type": "string"}
            }
        },
        "hospital": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "location": {"type": "string"}
            }
        },
        "diagnoses": {"type": "array", "items": {"type": "string"}},
        "medications": {"type": "array", "items": {"type": "string"}},
        "allergies": {"type": "array", "items": {"type": "string"}},
        "lab_results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "test_name": {"type": "string"},
                    "value": {"type": "string"},
                    "unit": {"type": "string"},
                    "reference_range": {"type": "string"}
                },
                "required": ["test_name", "value"]
            }
        },
        "recommendations": {"type": "array", "items": {"type": "string"}},
        "follow_up": {
            "type": "object",
            "properties": {
                "date": {"type": "string"},
                "instructions": {"type": "string"}
            }
        },
        "summary": {"type": "string", "description": "A 2-3 sentence clinical summary of the document."}
    },
    "required": ["patient", "doctor", "hospital", "diagnoses", "medications", "allergies", "lab_results", "recommendations", "follow_up", "summary"]
}
