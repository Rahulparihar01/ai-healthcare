import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from main import app
import models
from database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_core_modules.db"
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

def test_five_core_modules_flow():
    db = TestingSessionLocal()
    
    # 1. Create Patient & Doctor Users
    patient_user = models.User(username="patient1", hashed_password="pwd", email="p1@example.com", is_email_verified=True, role="Patient")
    doctor_user = models.User(username="doctor1", hashed_password="pwd", email="d1@example.com", is_email_verified=True, role="Doctor")
    admin_user = models.User(username="superadmin", hashed_password="pwd", email="admin@example.com", is_email_verified=True, role="Super Admin")
    
    db.add_all([patient_user, doctor_user, admin_user])
    db.commit()

    patient_profile = models.PatientProfile(
        user_id=patient_user.id,
        full_name="Jane Doe",
        health_id="12345678901234",
        gender="Female"
    )
    db.add(patient_profile)
    db.commit()
    patient_profile_id = patient_profile.id
    db.close()

    from auth import get_current_user
    
    # MODULE 1: AUTHENTICATION & REFRESH TOKEN ROTATION
    app.dependency_overrides[get_current_user] = lambda: patient_user
    refresh_token_rec = models.RefreshToken(
        token="test_refresh_token_123",
        user_id=patient_user.id,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db = TestingSessionLocal()
    db.add(refresh_token_rec)
    db.commit()
    db.close()

    refresh_res = client.post("/identity/auth/refresh", json={"refresh_token": "test_refresh_token_123"})
    assert refresh_res.status_code == 200
    assert "access_token" in refresh_res.json()
    assert refresh_res.json()["refresh_token"] != "test_refresh_token_123" # Verified token rotation!

    # MODULE 2: PATIENT TIMELINE & FILTERING
    db = TestingSessionLocal()
    event = models.TimelineEvent(
        patient_id=patient_profile_id,
        event_type="Diagnosis",
        reference_id=1,
        title="Hypertension Diagnosis",
        summary="Patient diagnosed with Stage 1 Hypertension"
    )
    db.add(event)
    db.commit()
    db.close()

    timeline_res = client.get("/timeline/12345678901234?event_type=Diagnosis")
    assert timeline_res.status_code == 200
    timeline_data = timeline_res.json()
    assert len(timeline_data) == 1
    assert timeline_data[0]["title"] == "Hypertension Diagnosis"

    # AI Timeline Summary
    summary_res = client.get("/timeline/12345678901234/summary")
    assert summary_res.status_code == 200
    assert summary_res.json()["total_events"] == 1

    # MODULE 3: AUDIT TRAIL & EXPORT
    app.dependency_overrides[get_current_user] = lambda: admin_user
    audit_rec = models.AuditLog(
        user_id=admin_user.id,
        action="HTTP GET /records/list",
        status="SUCCESS"
    )
    db = TestingSessionLocal()
    db.add(audit_rec)
    db.commit()
    db.close()

    audit_res = client.get("/audit/logs")
    assert audit_res.status_code == 200
    assert len(audit_res.json()) >= 1

    export_res = client.get("/audit/export?format=csv")
    assert export_res.status_code == 200
    assert "text/csv" in export_res.headers["content-type"]

    # MODULE 4: CLINICAL RECORD REVISIONS
    db = TestingSessionLocal()
    diag = models.Diagnosis(
        visit_id=1,
        patient_id=patient_profile_id,
        doctor_id=1,
        condition_name="Hypertension",
        icd10_code="I10"
    )
    db.add(diag)
    db.commit()
    diag_id = diag.id
    db.close()

    app.dependency_overrides[get_current_user] = lambda: admin_user
    update_res = client.put(
        "/records/update?event_type=Diagnosis&reference_id=" + str(diag_id),
        json={"condition_name": "Essential Hypertension", "change_reason": "Refined diagnosis classification"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["message"] == "Record updated successfully"
