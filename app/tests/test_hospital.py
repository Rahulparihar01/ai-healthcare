from fastapi.testclient import TestClient
import models
from auth import create_access_token

def test_create_hospital(client: TestClient, db):
    admin_user = models.User(username="superadmin_hosp", email="sah@test.com", role="Super Admin")
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    token = create_access_token(data={"sub": admin_user.username})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/hospitals/create", json={
        "name": "General Hospital",
        "address": "123 Main St",
        "contact_email": "gh@test.com",
        "contact_phone": "555-1234"
    }, headers=headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "General Hospital"
    assert "id" in data

def test_create_lab_pharmacy(client: TestClient, db):
    admin_user = models.User(username="superadmin_fac", email="saf@test.com", role="Super Admin")
    db.add(admin_user)
    db.commit()
    
    token = create_access_token(data={"sub": admin_user.username})
    headers = {"Authorization": f"Bearer {token}"}
    
    res_lab = client.post("/facilities/labs/create", json={
        "name": "Central Lab",
        "address": "456 Oak St",
        "license_number": "LAB-123",
        "contact_email": "lab@test.com",
        "contact_phone": "555-9999"
    }, headers=headers)
    assert res_lab.status_code == 201
    
    res_pharm = client.post("/facilities/pharmacies/create", json={
        "name": "City Pharmacy",
        "address": "789 Pine St",
        "license_number": "PHARM-123",
        "contact_email": "pharm@test.com",
        "contact_phone": "555-8888"
    }, headers=headers)
    assert res_pharm.status_code == 201

def test_list_facilities(client: TestClient, db):
    admin_user = models.User(username="superadmin_fac_list", email="safl@test.com", role="Super Admin")
    db.add(admin_user)
    db.commit()
    
    token = create_access_token(data={"sub": admin_user.username})
    headers = {"Authorization": f"Bearer {token}"}
    
    assert client.get("/hospitals/list", headers=headers).status_code == 200
    assert client.get("/facilities/labs/list", headers=headers).status_code == 200
    assert client.get("/facilities/pharmacies/list", headers=headers).status_code == 200
