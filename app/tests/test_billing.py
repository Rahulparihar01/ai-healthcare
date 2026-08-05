import pytest
from fastapi.testclient import TestClient
from main import app
import models
from database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_billing.db"
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

def test_invoice_and_payment_flow():
    db = TestingSessionLocal()
    
    # 1. Create Patient User & Patient Profile
    patient_user = models.User(username="billing_patient", hashed_password="hashed_pwd", role="Patient")
    db.add(patient_user)
    db.commit()
    db.refresh(patient_user)
    
    patient = models.PatientProfile(
        user_id=patient_user.id,
        health_id="99-8888-7777-6666",
        full_name="Jane Billing",
        status="Active"
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    patient_health_id = patient.health_id

    # 2. Create Admin User (Authorized to create invoices)
    admin_user = models.User(username="billing_admin", hashed_password="hashed_pwd", role="Hospital Admin")
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    db.close()

    # Override get_current_user for Admin
    from auth import get_current_user
    app.dependency_overrides[get_current_user] = lambda: admin_user

    # 3. Create Invoice
    invoice_payload = {
        "health_id": "99-8888-7777-6666",
        "description": "General Consultation & Diagnostic Test",
        "currency": "USD",
        "line_items": [
            {"description": "Doctor Fee", "amount": 4000},
            {"description": "Lab Test Fee", "amount": 2500}
        ]
    }
    
    response = client.post("/billing/invoices/create", json=invoice_payload)
    assert response.status_code == 200, response.text
    inv_data = response.json()
    assert inv_data["status"] == "Unpaid"
    assert inv_data["amount"] == 6500
    assert inv_data["invoice_number"].startswith("INV-")
    invoice_id = inv_data["id"]

    # 4. Override get_current_user for Patient
    app.dependency_overrides[get_current_user] = lambda: patient_user

    # 5. List Patient Invoices
    list_res = client.get(f"/billing/invoices/patient/{patient_health_id}")
    assert list_res.status_code == 200
    invoices = list_res.json()
    assert len(invoices) == 1
    assert invoices[0]["id"] == invoice_id

    # 6. Create Payment Intent
    intent_res = client.post(f"/billing/invoices/{invoice_id}/create-payment-intent", json={"gateway": "Stripe"})
    assert intent_res.status_code == 200
    intent_data = intent_res.json()
    assert "payment_intent_id" in intent_data
    assert intent_data["amount"] == 6500
    payment_intent_id = intent_data["payment_intent_id"]

    # 7. Confirm Payment
    confirm_payload = {
        "payment_intent_id": payment_intent_id,
        "payment_method": "Card",
        "gateway_transaction_id": "txn_stripe_test_123"
    }
    confirm_res = client.post(f"/billing/invoices/{invoice_id}/confirm-payment", json=confirm_payload)
    assert confirm_res.status_code == 200
    paid_inv = confirm_res.json()
    assert paid_inv["status"] == "Paid"
    assert paid_inv["payment_method"] == "Card"
    assert paid_inv["receipt_signature"] is not None

    # 8. Fetch Receipt
    receipt_res = client.get(f"/billing/invoices/{invoice_id}/receipt")
    assert receipt_res.status_code == 200
    receipt = receipt_res.json()
    assert receipt["invoice_number"] == inv_data["invoice_number"]
    assert receipt["amount"] == 6500
    assert receipt["digital_signature"] == paid_inv["receipt_signature"]
