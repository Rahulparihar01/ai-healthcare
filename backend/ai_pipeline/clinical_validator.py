import re
from datetime import datetime

def validate_extraction(extracted_data: dict, confidence: float) -> bool:
    """
    Performs deep clinical validation on the extracted data.
    Ensures required fields exist, dates are valid, numbers are numeric,
    units are normalized, and confidence is above threshold.
    Returns True if valid, False if it Needs Review.
    """
    if not isinstance(extracted_data, dict):
        return False
        
    # 1. Confidence Check
    if confidence < 0.80:
        print(f"Validation Failed: Low confidence score ({confidence})")
        return False
        
    # 2. Required Fields
    required_keys = ["patient", "diagnoses", "medications", "lab_results", "summary"]
    for key in required_keys:
        if key not in extracted_data:
            print(f"Validation Failed: Missing required key '{key}'")
            return False
            
    # 3. Date Validation (follow_up)
    follow_up = extracted_data.get("follow_up", {})
    date_str = follow_up.get("date", "")
    if date_str:
        try:
            # Attempt to parse YYYY-MM-DD
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print(f"Validation Failed: Invalid date format '{date_str}'. Expected YYYY-MM-DD.")
            return False

    # 4. Numeric Validation and Unit Normalization
    unit_map = {
        "mg/dl": "mg/dL",
        "g/l": "g/L",
        "mmol/l": "mmol/L",
        "u/l": "U/L",
        "meq/l": "mEq/L",
        "10^3/ul": "10^3/uL",
        "10^6/ul": "10^6/uL"
    }
    
    for lab in extracted_data.get("lab_results", []):
        value_str = str(lab.get("value", "")).strip()
        unit_str = str(lab.get("unit", "")).strip()
        
        # Numeric check: remove basic operators and spaces
        clean_val = value_str.replace("<", "").replace(">", "").replace("=", "").strip()
        if clean_val:
            try:
                float(clean_val)
            except ValueError:
                # Some values are negative/positive or text like 'Present', we only flag if it's wildly unexpected
                # But for strict validation, let's flag if it contains letters when we expect a number.
                if any(c.isalpha() for c in clean_val) and clean_val.lower() not in ["positive", "negative", "present", "absent", "normal", "abnormal", "trace"]:
                    print(f"Validation Failed: Lab value '{value_str}' is non-numeric/unrecognized.")
                    return False
                    
        # Unit normalization
        if unit_str:
            unit_lower = unit_str.lower()
            if unit_lower in unit_map:
                lab["unit"] = unit_map[unit_lower] # Normalize in-place

    return True
