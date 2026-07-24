from fastapi.testclient import TestClient
import models
from auth import create_access_token

def test_get_patient_timeline(client: TestClient, db):
    doc_user = models.User(username="timeline_doc", email="td@test.com", role="Doctor")
    db.add(doc_user)
    db.commit()
    db.refresh(doc_user)
    
    pat_user = models.User(username="timeline_pat", email="tp@test.com", role="Patient")
    db.add(pat_user)
    db.commit()
    db.refresh(pat_user)
    
    patient = models.PatientProfile(user_id=pat_user.id, health_id="H-TL-123")
    db.add(patient)
    db.commit()
    db.refresh(patient)
    
    # Needs valid doctor-patient assignment or super admin
    admin_user = models.User(username="timeline_sa", email="tsa@test.com", role="Super Admin")
    db.add(admin_user)
    db.commit()
    
    # Add timeline events
    event1 = models.TimelineEvent(patient_id=patient.id, event_type="Visit", title="Checkup")
    event2 = models.TimelineEvent(patient_id=patient.id, event_type="Prescription", title="Rx")
    db.add(event1)
    db.add(event2)
    db.commit()
    
    token = create_access_token(data={"sub": admin_user.username})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/timeline/H-TL-123", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert any(e["title"] == "Checkup" for e in data)
