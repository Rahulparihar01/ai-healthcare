import pytest
from ai_pipeline.entity_mapper import map_extracted_data_to_models
from models import Disease, Medication, Allergy, LabResult

def test_map_extracted_data_to_models():
    extracted_data = {
        "diagnoses": ["Type 2 Diabetes", "Hypertension"],
        "medications": ["Metformin 500mg", "Lisinopril 10mg"],
        "allergies": ["Penicillin", "Peanuts"],
        "lab_results": [
            {
                "test_name": "HbA1c",
                "value": "7.2",
                "unit": "%",
                "reference_range": "< 5.7"
            }
        ]
    }
    
    patient_id = 1
    lab_report_id = 100
    
    models = map_extracted_data_to_models(extracted_data, patient_id, lab_report_id)
    
    # Check counts
    assert len(models) == 7  # 2 diseases + 2 medications + 2 allergies + 1 lab result
    
    # Filter by type
    diseases = [m for m in models if isinstance(m, Disease)]
    medications = [m for m in models if isinstance(m, Medication)]
    allergies = [m for m in models if isinstance(m, Allergy)]
    lab_results = [m for m in models if isinstance(m, LabResult)]
    
    # Verify Diseases
    assert len(diseases) == 2
    assert diseases[0].disease_name == "Type 2 Diabetes"
    assert diseases[0].patient_id == 1
    assert diseases[1].disease_name == "Hypertension"
    
    # Verify Medications
    assert len(medications) == 2
    assert medications[0].medicine_name == "Metformin 500mg"
    assert medications[0].status == "Active"
    
    # Verify Allergies
    assert len(allergies) == 2
    assert allergies[0].allergen == "Penicillin"
    assert allergies[1].allergen == "Peanuts"
    
    # Verify Lab Results
    assert len(lab_results) == 1
    assert lab_results[0].biomarker_name == "HbA1c"
    assert lab_results[0].value == "7.2"
    assert lab_results[0].unit == "%"
    assert lab_results[0].lab_report_id == 100

def test_map_extracted_data_empty():
    models = map_extracted_data_to_models({}, 1)
    assert len(models) == 0
