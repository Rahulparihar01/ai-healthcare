from models import Disease, Medication, Allergy, LabResult
from typing import List, Dict, Any
from datetime import datetime

def map_extracted_data_to_models(extracted_data: Dict[str, Any], patient_id: int, lab_report_id: int = None) -> List[Any]:
    """
    Takes the structured JSON output from the AI extraction pipeline and 
    maps it to SQLAlchemy Knowledge Graph models ready for DB insertion.
    """
    models_to_save = []
    
    # Map Diagnoses -> Diseases
    diagnoses = extracted_data.get("diagnoses", [])
    for diagnosis in diagnoses:
        disease = Disease(
            patient_id=patient_id,
            disease_name=str(diagnosis).strip(),
            # Status and severity are not explicitly extracted in v1.0 schema yet, 
            # so we'll leave them blank or handle them later with a more advanced prompt.
            status=None,
            severity=None,
            diagnosis_date=None
        )
        models_to_save.append(disease)
        
    # Map Medications -> Medications
    medications = extracted_data.get("medications", [])
    for med in medications:
        medication = Medication(
            patient_id=patient_id,
            medicine_name=str(med).strip(),
            dosage=None,
            frequency=None,
            status="Active" # Assume active by default unless context says otherwise
        )
        models_to_save.append(medication)
        
    # Map Allergies -> Allergies
    allergies = extracted_data.get("allergies", [])
    for allergy_str in allergies:
        allergy = Allergy(
            patient_id=patient_id,
            allergen=str(allergy_str).strip(),
            severity=None,
            reaction=None
        )
        models_to_save.append(allergy)
        
    # Map Lab Results -> LabResults
    lab_results = extracted_data.get("lab_results", [])
    for lab in lab_results:
        # Validate that it's a dict just in case
        if isinstance(lab, dict):
            lab_result = LabResult(
                patient_id=patient_id,
                lab_report_id=lab_report_id,
                biomarker_name=str(lab.get("test_name", "")).strip(),
                value=str(lab.get("value", "")).strip(),
                unit=str(lab.get("unit", "")).strip(),
                reference_range=str(lab.get("reference_range", "")).strip(),
                recorded_at=datetime.utcnow()
            )
            models_to_save.append(lab_result)
            
    return models_to_save
