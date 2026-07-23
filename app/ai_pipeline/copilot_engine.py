import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "mock-key"))

def check_prescription_safety(patient_id: int, allergies: list, current_medications: list, proposed_medications: list) -> list:
    """
    Checks proposed medications against current medications and allergies.
    Returns a list of warnings (dictionaries with severity, alert_type, message).
    """
    system_prompt = (
        "You are a medical copilot assisting a doctor. "
        "Review the proposed medications against the patient's known allergies and current active medications. "
        "Identify any duplicate therapies, drug-drug interactions, or allergy conflicts. "
        "Return the output strictly as a JSON array of warning objects. "
        "Each warning must have: 'alert_type' (INTERACTION, ALLERGY), 'severity' (HIGH, MEDIUM, LOW), and 'message' (string explanation)."
        "If there are no conflicts, return an empty array []."
    )
    
    user_prompt = f"""
    Allergies: {json.dumps(allergies)}
    Current Medications: {json.dumps(current_medications)}
    Proposed Medications: {json.dumps(proposed_medications)}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=500,
            temperature=0.1
        )
        # Parse output ensuring it's a list (the LLM might wrap it in a dict if using json_object format, so let's handle that)
        content = response.choices[0].message.content.strip()
        data = json.loads(content)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # Try to find a list inside
            for key, val in data.items():
                if isinstance(val, list):
                    return val
            return []
    except Exception as e:
        print(f"Copilot engine failed: {e}")
        return []

def generate_case_history(timeline_events: list, lab_results: list, diseases: list) -> str:
    """
    Synthesizes a chronological, narrative medical history from records.
    """
    system_prompt = (
        "You are a medical copilot. Synthesize a comprehensive but concise narrative case history for a patient "
        "based on their timeline events, diseases, and recent lab results. "
        "Focus on the progression of their health, active issues, and critical findings. "
        "Make it readable for a doctor."
    )
    
    user_prompt = f"""
    Diseases: {json.dumps(diseases)}
    Timeline Events: {json.dumps(timeline_events, default=str)}
    Lab Results: {json.dumps(lab_results, default=str)}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=800,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Copilot engine failed: {e}")
        return "Failed to generate case history."

def compare_medical_reports(report_a: dict, report_b: dict) -> str:
    """
    Analyzes two reports and generates a structured comparison highlighting key changes.
    """
    system_prompt = (
        "You are a medical copilot assisting a doctor. You will be given two medical reports for the same patient, "
        "Report A (older) and Report B (newer). "
        "Compare the two reports and highlight the key changes. "
        "Specifically mention improvements, regressions, or new findings. "
        "Be concise and structure your output in clear bullet points."
    )
    
    user_prompt = f"Report A (Older):\n{json.dumps(report_a)}\n\nReport B (Newer):\n{json.dumps(report_b)}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Comparison failed: {e}")
        return "Failed to compare reports."
