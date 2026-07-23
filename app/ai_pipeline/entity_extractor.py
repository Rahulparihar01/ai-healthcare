def extract_entities(extracted_data: dict) -> dict:
    """
    Extracts key medical entities from the unified v1.0 schema output.
    """
    patient = extracted_data.get("patient", {})
    return {
        "patient_name": patient.get("name", "Unknown"),
        "age": patient.get("age", 0),
        "conditions": extracted_data.get("diagnoses", []),
        "medications": extracted_data.get("medications", []),
        "allergies": [] # The new schema didn't explicitly ask for allergies, but we can add it or just omit it.
    }
