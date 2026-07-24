from fastapi.testclient import TestClient
import models
from auth import create_access_token
import pytest

def test_create_record(client: TestClient, db):
    user = models.User(username="testdoc_rec", email="testdoc_rec@test.com", role="Doctor")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    doctor = models.DoctorProfile(user_id=user.id)
    db.add(doctor)
    
    patient_user = models.User(username="testpat_rec", email="testpat_rec@test.com", role="Patient")
    db.add(patient_user)
    db.commit()
    db.refresh(patient_user)
    
    patient = models.PatientProfile(user_id=patient_user.id, health_id="H-999")
    db.add(patient)
    db.commit()
    
    # Needs a patient assignment for IDOR bypass
    assign = models.PatientAssignment(doctor_id=doctor.id, patient_id=patient.id, status="Active")
    db.add(assign)
    db.commit()
    
    token = create_access_token(data={"sub": user.username})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/records/create?health_id=H-999", json={
        "record_type": "visit",
        "data": {
            "chief_complaint": "Headache",
            "notes": "Patient complains of severe headache."
        }
    }, headers=headers)
    
    assert response.status_code == 200
    assert response.json()["message"] == "Visit created successfully"
    assert "id" in response.json()

def test_prescription_signature(client: TestClient, db):
    user = models.User(username="testdoc_sig", email="testdoc_sig@test.com", role="Doctor")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    doctor = models.DoctorProfile(user_id=user.id)
    db.add(doctor)
    
    patient_user = models.User(username="testpat_sig", email="testpat_sig@test.com", role="Patient")
    db.add(patient_user)
    db.commit()
    db.refresh(patient_user)
    
    patient = models.PatientProfile(user_id=patient_user.id, health_id="H-SIG")
    db.add(patient)
    db.commit()
    
    assign = models.PatientAssignment(doctor_id=doctor.id, patient_id=patient.id, status="Active")
    db.add(assign)
    db.commit()
    
    token = create_access_token(data={"sub": user.username})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/records/create?health_id=H-SIG", json={
        "record_type": "prescription",
        "data": {
            "medications": [{"name": "Amoxicillin", "dosage": "500mg"}],
            "instructions": "Take twice daily."
        }
    }, headers=headers)
    
    assert response.status_code == 200
    
    # Verify the signature block was appended
    pres = db.query(models.Prescription).filter(models.Prescription.patient_id == patient.id).first()
    assert pres is not None
    assert "--- DIGITAL SIGNATURE ---" in pres.instructions
    assert "Issuer ID:" in pres.instructions
    assert "Signature:" in pres.instructions
