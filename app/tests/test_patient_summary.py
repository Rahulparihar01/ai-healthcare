import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from database import Base, get_db
from auth import get_current_user
from models import User, PatientProfile, Disease, Medication, Allergy, LabResult, RoleEnum

# Assuming SQLite in-memory for testing, or similar setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_patient_summary.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_current_user():
    return User(id=2, username="Raj", role=RoleEnum.PATIENT.value, hospital_id=None)

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Create test data
    user = User(id=2, username="Raj", hashed_password="hashed_123456", role=RoleEnum.PATIENT.value)
    db.add(user)
    db.commit()
    
    profile = PatientProfile(
        id=1, 
        user_id=2, 
        health_id="H12345", 
        full_name="Test Patient", 
        dob="1990-01-01", 
        gender="Male", 
        blood_group="O+"
    )
    db.add(profile)
    db.commit()
    
    disease = Disease(patient_id=1, disease_name="Diabetes", status="Chronic", severity="Moderate")
    db.add(disease)
    
    medication = Medication(patient_id=1, medicine_name="Metformin", dosage="500mg", frequency="1/day", status="Active")
    db.add(medication)
    
    allergy = Allergy(patient_id=1, allergen="Penicillin", severity="Severe", reaction="Rash")
    db.add(allergy)
    
    lab_result = LabResult(patient_id=1, biomarker_name="HbA1c", value="6.5", unit="%", reference_range="4.0-5.6")
    db.add(lab_result)
    
    db.commit()
    yield
    db.close()
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

def test_get_patient_health_summary():
    response = client.get("/patients/H12345/health-summary", headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJSYWoiLCJleHAiOjE3ODQ4MDU0ODUsInR5cGUiOiJhY2Nlc3MifQ.jqYrdm0qrmDmZEhXV6wXKYpvIR3ATHHEB0utLdEo57Y"})
    if response.status_code != 200:
        print(response.json())
    assert response.status_code == 200
    data = response.json()
    
    assert data["health_id"] == "H12345"
    assert data["full_name"] == "Test Patient"
    
    assert len(data["diseases"]) == 1
    assert data["diseases"][0]["disease_name"] == "Diabetes"
    
    assert len(data["medications"]) == 1
    assert data["medications"][0]["medicine_name"] == "Metformin"
    
    assert len(data["allergies"]) == 1
    assert data["allergies"][0]["allergen"] == "Penicillin"
    
    assert len(data["recent_lab_results"]) == 1
    assert data["recent_lab_results"][0]["biomarker_name"] == "HbA1c"
