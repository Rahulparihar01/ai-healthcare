from fastapi.testclient import TestClient
import models
from auth import create_access_token

def test_list_doctors(client: TestClient, db):
    admin_user = models.User(username="superadmin_doc", email="sad@test.com", role="Super Admin")
    db.add(admin_user)
    db.commit()
    
    token = create_access_token(data={"sub": admin_user.username})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/doctors/list", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_onboard_doctor(client: TestClient, db):
    admin_user = models.User(username="superadmin_doc_onb", email="sdo@test.com", role="Super Admin")
    db.add(admin_user)
    db.commit()
    
    doc_user = models.User(username="new_doctor", email="newdoc@test.com", role="Doctor")
    db.add(doc_user)
    db.commit()
    
    hospital = models.Hospital(name="Test Hospital")
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    
    dept = models.Department(name="Cardiology", hospital_id=hospital.id)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    
    token = create_access_token(data={"sub": admin_user.username})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/doctors/onboard", json={
        "user_id": doc_user.id,
        "hospital_id": hospital.id,
        "department_id": dept.id,
        "license_number": "DOC-123"
    }, headers=headers)
    
    assert response.status_code == 201
