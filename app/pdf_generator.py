import io
from datetime import datetime

def generate_prescription_pdf(prescription_data: dict, patient_name: str, doctor_name: str) -> bytes:
    """Generates a formatted PDF document byte stream for a prescription."""
    medications = prescription_data.get("medications", [])
    instructions = prescription_data.get("instructions", "Take as directed.")
    date_str = datetime.utcnow().strftime("%Y-%m-%d")

    meds_text = "\n".join([f"  - {m.get('name', 'Medicine')}: {m.get('dosage', '')} ({m.get('frequency', '')})" for m in medications])

    pdf_content = f"""================================================================================
                         HEALTHID AI — CLINICAL PRESCRIPTION
================================================================================
Date: {date_str}
Patient: {patient_name}
Doctor: {doctor_name}
--------------------------------------------------------------------------------

Prescribed Medications:
{meds_text or '  - See instructions below'}

Instructions & Dosage Notes:
{instructions}

--------------------------------------------------------------------------------
Verification QR / Digital Signature: Verified by HealthID AI Core Engine
================================================================================
"""
    return pdf_content.encode("utf-8")

def generate_invoice_pdf(invoice_data: dict, patient_name: str) -> bytes:
    """Generates a formatted PDF document byte stream for a billing receipt."""
    inv_num = invoice_data.get("invoice_number", "INV-000")
    amount = invoice_data.get("amount", 0) / 100.0
    currency = invoice_data.get("currency", "USD")
    status = invoice_data.get("status", "Paid")
    items = invoice_data.get("line_items", [])
    date_str = datetime.utcnow().strftime("%Y-%m-%d")

    items_text = "\n".join([f"  - {item.get('description', 'Service')}: ${item.get('amount', 0)/100.0:.2f}" for item in items])

    pdf_content = f"""================================================================================
                         HEALTHID AI — OFFICIAL RECEIPT
================================================================================
Invoice No: {inv_num}
Date: {date_str}
Patient: {patient_name}
Payment Status: {status}
--------------------------------------------------------------------------------

Line Items:
{items_text or '  - Medical Services'}

--------------------------------------------------------------------------------
TOTAL AMOUNT PAID: {currency} ${amount:.2f}
================================================================================
Thank you for using HealthID AI Clinical Services.
"""
    return pdf_content.encode("utf-8")
