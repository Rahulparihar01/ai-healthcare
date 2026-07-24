from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import pytest
import models
from auth import create_access_token

def test_prevent_double_booking(client: TestClient, db):
    # Setup users, patient, doctor
    user = models.User(username="testdoc", email="testdoc@test.com", role="Doctor")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    doctor = models.DoctorProfile(user_id=user.id)
    db.add(doctor)
    
    patient_user = models.User(username="testpatient", email="testpatient@test.com", role="Patient")
    db.add(patient_user)
    db.commit()
    db.refresh(patient_user)
    
    patient = models.PatientProfile(user_id=patient_user.id, health_id="H-123")
    db.add(patient)
    db.commit()
    db.refresh(doctor)
    db.refresh(patient)
    
    # Generate token
    token = create_access_token(data={"sub": user.username})
    headers = {"Authorization": f"Bearer {token}"}
    
    start_time = datetime.utcnow() + timedelta(days=1)
    
    # Book first appointment
    response = client.post("/appointments/create", json={
        "patient_health_id": "H-123",
        "doctor_id": doctor.id,
        "start_time": start_time.isoformat()
    }, headers=headers)
    
    assert response.status_code == 200
    
    # Attempt to double book
    response2 = client.post("/appointments/create", json={
        "patient_health_id": "H-123",
        "doctor_id": doctor.id,
        "start_time": (start_time + timedelta(minutes=15)).isoformat()
    }, headers=headers)
    
    assert response2.status_code == 409
    assert "already has an appointment" in response2.json()["detail"]
