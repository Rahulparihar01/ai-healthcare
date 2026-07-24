from fastapi.testclient import TestClient
import models
from auth import create_access_token
import pytest

def test_pending_labs_and_completion(client: TestClient, db):
    user = models.User(username="testlabtech", email="testlabtech@test.com", role="Lab Technician")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    patient_user = models.User(username="testpat_lab", email="testpat_lab@test.com", role="Patient")
    db.add(patient_user)
    db.commit()
    db.refresh(patient_user)
    
    patient = models.PatientProfile(user_id=patient_user.id, health_id="H-LAB-123")
    db.add(patient)
    db.commit()
    
    # Create a pending lab order
    order = models.LabTestOrder(
        patient_id=patient.id,
        tests=[{"name": "CBC"}],
        status="Pending"
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    token = create_access_token(data={"sub": user.username})
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Test fetching pending orders
    res = client.get("/labs/pending", headers=headers)
    assert res.status_code == 200
    orders = res.json()
    assert len(orders) >= 1
    assert any(o["id"] == order.id for o in orders)
    
    # 2. Test completing the order
    res_complete = client.post(f"/labs/orders/{order.id}/complete", json={
        "results": {"WBC": "6.5", "RBC": "4.8"}
    }, headers=headers)
    
    assert res_complete.status_code == 200
    assert "report_id" in res_complete.json()
    
    # Verify status changed
    db.refresh(order)
    assert order.status == "Completed"
    
    # 3. Test it's no longer in pending list
    res_after = client.get("/labs/pending", headers=headers)
    assert not any(o["id"] == order.id for o in res_after.json())
