from fastapi.testclient import TestClient
import models
from auth import create_access_token

def test_register_patient_full(client: TestClient, db):
    # Setup Super Admin
    admin_user = models.User(username="superadmin_pat", email="sap@test.com", role="Super Admin")
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    token = create_access_token(data={"sub": admin_user.username})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/patients/register", json={
        "username": "newpatient",
        "password": "securepassword",
        "email": "newpat@test.com",
        "full_name": "John Doe",
        "blood_group": "O+"
    }, headers=headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "John Doe"
    assert "health_id" in data
    
def test_get_all_patients(client: TestClient, db):
    admin_user = models.User(username="superadmin_pat2", email="sap2@test.com", role="Super Admin")
    db.add(admin_user)
    db.commit()
    
    token = create_access_token(data={"sub": admin_user.username})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/patients/list", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_patient_profile(client: TestClient, db):
    # Setup Patient
    pat_user = models.User(username="testpat_prof", email="tpp@test.com", role="Patient")
    db.add(pat_user)
    db.commit()
    db.refresh(pat_user)
    
    profile = models.PatientProfile(user_id=pat_user.id, health_id="H-PROF-123", full_name="Jane Doe", qr_code_path="/tmp/test.png")
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    token = create_access_token(data={"sub": pat_user.username})
    headers = {"Authorization": f"Bearer {token}"}
    
    # As patient, they shouldn't need health_id
    response = client.get("/patients/profile", headers=headers)
    if response.status_code != 200:
        print(f"DEBUG Profile: user.id={pat_user.id}, profile.user_id={profile.user_id}")
        print(f"DEBUG Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["health_id"] == "H-PROF-123"

def test_update_patient_profile(client: TestClient, db):
    pat_user = models.User(username="testpat_upd", email="tpu@test.com", role="Patient")
    db.add(pat_user)
    db.commit()
    db.refresh(pat_user)
    
    profile = models.PatientProfile(user_id=pat_user.id, health_id="H-UPD-123", full_name="Old Name", qr_code_path="/tmp/test.png")
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    token = create_access_token(data={"sub": pat_user.username})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.put("/patients/update?health_id=H-UPD-123", json={
        "full_name": "New Name",
        "blood_group": "A-"
    }, headers=headers)
    
    if response.status_code != 200:
        print(f"DEBUG Update: profile.health_id={profile.health_id}")
        print(f"DEBUG Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["full_name"] == "New Name"
    assert response.json()["blood_group"] == "A-"
