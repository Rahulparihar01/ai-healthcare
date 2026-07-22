def get_extraction_prompt(document_type: str) -> str:
    """
    Returns a specialized system prompt based on the classified document type.
    """
    base_prompt = (
        "You are a highly accurate medical data extraction AI. "
        "Extract the information from the raw text precisely into the required JSON structure. "
        "If a nested field or object is not present in the text, return an empty string or empty array as appropriate."
    )
    
    specialized_prompts = {
        "Blood Report": "Focus heavily on extracting all items into the 'lab_results' array. Ensure units and reference ranges are captured accurately.",
        "CBC": "Focus heavily on extracting all complete blood count metrics into the 'lab_results' array.",
        "Lipid Profile": "Extract cholesterol, triglycerides, HDL, LDL into 'lab_results'.",
        "Prescription": "Pay close attention to the 'medications' array. Capture dosage and frequency if available. Also look for 'recommendations'.",
        "Discharge Summary": "Ensure 'diagnoses', 'medications', and 'follow_up' instructions are thoroughly documented.",
        "MRI Report": "Focus on 'diagnoses' and 'recommendations'. Summarize the key imaging findings.",
        "CT Report": "Focus on 'diagnoses' and 'recommendations'. Summarize the key imaging findings.",
        "X-Ray Report": "Focus on 'diagnoses' and 'recommendations'. Summarize the key imaging findings.",
        "ECG": "Extract the heart rate, rhythm, and any abnormalities into 'diagnoses' or 'lab_results'.",
        "Echo": "Extract ejection fraction, valve status, and any abnormalities.",
        "Referral Letter": "Focus on the 'doctor' (both referring and referred to if possible), 'diagnoses', and reason for referral.",
        "Clinical Notes": "Extract general 'diagnoses', 'medications', and the physician's 'recommendations'.",
        "Vaccination Record": "Extract the vaccines into 'medications' or 'recommendations'."
    }
    
    specific_instructions = specialized_prompts.get(document_type, "Extract all available information as accurately as possible.")
    
    return f"{base_prompt}\n\nSPECIAL INSTRUCTIONS FOR {document_type.upper()}:\n{specific_instructions}"
