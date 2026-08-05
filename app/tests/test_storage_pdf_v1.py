import pytest
from fastapi.testclient import TestClient
from main import app
from storage import upload_file, generate_presigned_url
from pdf_generator import generate_prescription_pdf, generate_invoice_pdf

client = TestClient(app)

def test_api_v1_versioned_endpoint():
    response = client.get("/api/v1/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_storage_upload_and_presigned_url():
    data = b"sample pdf content %PDF-1.4"
    path = upload_file(data, "test.pdf", "application/pdf")
    assert path is not None
    
    url = generate_presigned_url(path)
    assert url is not None

def test_pdf_generators():
    pres_pdf = generate_prescription_pdf(
        {"medications": [{"name": "Amoxicillin", "dosage": "500mg"}]},
        "John Doe",
        "Dr. Smith"
    )
    assert b"HEALTHID AI" in pres_pdf
    assert b"Amoxicillin" in pres_pdf

    inv_pdf = generate_invoice_pdf(
        {"invoice_number": "INV-101", "amount": 5000, "currency": "USD"},
        "John Doe"
    )
    assert b"INV-101" in inv_pdf
    assert b"50.00" in inv_pdf

def test_sse_task_status_stream():
    response = client.get("/api/v1/sse/task-status/task_123")
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
