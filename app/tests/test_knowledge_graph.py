import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from main import app
from database import get_db
from models import PatientProfile

client = TestClient(app)

def test_ingest_knowledge_graph_success():
    # Mock the database session
    mock_db = MagicMock()
    
    # Mock the patient query to return a dummy patient
    mock_patient = PatientProfile(id=1, full_name="John Doe")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_patient
    
    # Override the dependency
    app.dependency_overrides[get_db] = lambda: mock_db
    
    payload = {
        "patient_id": 1,
        "hospital_id": 10,
        "extracted_data": {
            "diagnoses": ["Asthma"],
            "medications": ["Albuterol"],
            "allergies": ["Dust"],
            "lab_results": []
        }
    }
    
    response = client.post("/knowledge-graph/ingest", json=payload)
    
    assert response.status_code == 201
    assert response.json()["message"] == "Knowledge Graph entities successfully ingested."
    assert response.json()["entities_inserted"] == 3
    
    # Verify db.add_all was called
    mock_db.add_all.assert_called_once()
    mock_db.commit.assert_called_once()
    
    # Clean up
    app.dependency_overrides.clear()

def test_ingest_knowledge_graph_patient_not_found():
    mock_db = MagicMock()
    
    # Mock query to return None (patient not found)
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    payload = {
        "patient_id": 999,
        "extracted_data": {
            "diagnoses": ["Asthma"]
        }
    }
    
    response = client.post("/knowledge-graph/ingest", json=payload)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Patient not found"
    
    # Clean up
    app.dependency_overrides.clear()

def test_ingest_knowledge_graph_no_entities():
    mock_db = MagicMock()
    mock_patient = PatientProfile(id=1)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_patient
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    payload = {
        "patient_id": 1,
        "extracted_data": {} # Empty data
    }
    
    response = client.post("/knowledge-graph/ingest", json=payload)
    
    assert response.status_code == 201
    assert response.json()["message"] == "No valid entities found in the extracted data to ingest."
    
    # db.add_all should NOT be called
    mock_db.add_all.assert_not_called()
    
    app.dependency_overrides.clear()
