import pytest
from fastapi.testclient import TestClient
from main import app
import models
from database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_permissions.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_role_permissions_flow():
    db = TestingSessionLocal()
    
    # 1. Create Super Admin and Doctor users
    admin = models.User(username="admin_user", hashed_password="pwd", role="Super Admin")
    doctor = models.User(username="doctor_user", hashed_password="pwd", role="Doctor")
    receptionist = models.User(username="recept_user", hashed_password="pwd", role="Receptionist")
    
    db.add_all([admin, doctor, receptionist])
    db.commit()
    db.close()

    from auth import get_current_user
    
    # 2. Test Seed Permissions
    app.dependency_overrides[get_current_user] = lambda: admin
    seed_res = client.post("/identity/authorization/seed")
    assert seed_res.status_code == 200

    # 3. List All Permissions
    perms_res = client.get("/identity/authorization/permissions")
    assert perms_res.status_code == 200
    perms = perms_res.json()
    assert len(perms) > 0
    perm_names = [p["name"] for p in perms]
    assert "diagnosis.create" in perm_names
    assert "invoice.create" in perm_names

    # 4. Get My Permissions for Doctor
    app.dependency_overrides[get_current_user] = lambda: doctor
    doc_perms_res = client.get("/identity/authorization/my-permissions")
    assert doc_perms_res.status_code == 200
    doc_data = doc_perms_res.json()
    assert doc_data["role"] == "Doctor"
    assert "diagnosis.create" in doc_data["permissions"]

    # 5. Get Role Permissions for Receptionist
    app.dependency_overrides[get_current_user] = lambda: admin
    recept_perms_res = client.get("/identity/authorization/roles/Receptionist/permissions")
    assert recept_perms_res.status_code == 200
    recept_perms = [p["name"] for p in recept_perms_res.json()]
    assert "invoice.create" in recept_perms
    assert "diagnosis.create" not in recept_perms # Receptionist cannot create diagnosis

    # 6. Dynamically Assign Permission to Receptionist (Super Admin Action)
    diagnosis_perm = next(p for p in perms if p["name"] == "diagnosis.create")
    invoice_perm = next(p for p in perms if p["name"] == "invoice.create")
    
    update_payload = {"permission_ids": [diagnosis_perm["id"], invoice_perm["id"]]}
    update_res = client.post("/identity/authorization/roles/Receptionist/permissions", json=update_payload)
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert "diagnosis.create" in updated_data["assigned_permissions"]
