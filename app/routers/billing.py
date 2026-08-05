from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import hmac
import hashlib
import json

from database import get_db
import models
from auth import get_current_user, SECRET_KEY
from auth_middleware import require_permission
from routers.records import verify_patient_access

router = APIRouter(prefix="/billing", tags=["Billing & Payments"])

class LineItem(BaseModel):
    description: str
    amount: int # amount in cents / minor currency units

class InvoiceCreate(BaseModel):
    health_id: str
    doctor_id: Optional[int] = None
    visit_id: Optional[int] = None
    description: Optional[str] = "Medical Consultation & Services"
    line_items: List[LineItem]
    currency: Optional[str] = "USD"
    due_in_days: Optional[int] = 14

class PaymentIntentRequest(BaseModel):
    gateway: Optional[str] = "Stripe"

class PaymentConfirmRequest(BaseModel):
    payment_intent_id: str
    payment_method: str # "Card", "Stripe", "Razorpay", "Cash"
    gateway_transaction_id: Optional[str] = None

class InvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_number: str
    patient_id: int
    hospital_id: Optional[int]
    doctor_id: Optional[int]
    visit_id: Optional[int]
    amount: int
    currency: str
    status: str
    description: Optional[str]
    line_items: List[Dict[str, Any]]
    due_date: Optional[datetime]
    paid_at: Optional[datetime]
    payment_method: Optional[str]
    receipt_signature: Optional[str]

@router.post("/invoices/create", response_model=InvoiceResponse)
def create_invoice(
    payload: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission("invoice.create"))
):
    patient = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == payload.health_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    total_amount = sum(item.amount for item in payload.line_items)
    if total_amount <= 0:
        raise HTTPException(status_code=400, detail="Invoice total amount must be greater than zero")

    doctor_profile = None
    if current_user.role == models.RoleEnum.DOCTOR.value:
        doctor_profile = db.query(models.DoctorProfile).filter(models.DoctorProfile.user_id == current_user.id).first()

    hospital_id = patient.hospital_id or current_user.hospital_id
    doctor_id = payload.doctor_id or (doctor_profile.id if doctor_profile else None)
    
    unique_suffix = uuid.uuid4().hex[:6].upper()
    invoice_number = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{unique_suffix}"
    due_date = datetime.utcnow() + timedelta(days=payload.due_in_days or 14)

    invoice = models.Invoice(
        invoice_number=invoice_number,
        patient_id=patient.id,
        hospital_id=hospital_id,
        doctor_id=doctor_id,
        visit_id=payload.visit_id,
        amount=total_amount,
        currency=payload.currency or "USD",
        status="Unpaid",
        description=payload.description,
        line_items=[item.model_dump() for item in payload.line_items],
        due_date=due_date,
        created_by=current_user.id
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice

@router.get("/invoices/patient/{health_id}", response_model=List[InvoiceResponse])
def list_patient_invoices(
    health_id: str,
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    patient = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == health_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    verify_patient_access(patient, current_user, db)
    
    query = db.query(models.Invoice).filter(models.Invoice.patient_id == patient.id)
    if status_filter:
        query = query.filter(models.Invoice.status == status_filter)
        
    invoices = query.order_by(models.Invoice.created_at.desc()).offset(skip).limit(limit).all()
    return invoices

@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice_detail(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    patient = db.query(models.PatientProfile).filter(models.PatientProfile.id == invoice.patient_id).first()
    if patient:
        verify_patient_access(patient, current_user, db)
        
    return invoice

@router.post("/invoices/{invoice_id}/create-payment-intent")
def create_payment_intent(
    invoice_id: int,
    payload: PaymentIntentRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    if invoice.status == "Paid":
        raise HTTPException(status_code=400, detail="Invoice is already paid")
        
    patient = db.query(models.PatientProfile).filter(models.PatientProfile.id == invoice.patient_id).first()
    if patient:
        verify_patient_access(patient, current_user, db)

    payment_intent_id = f"pi_{payload.gateway.lower()}_{uuid.uuid4().hex[:16]}"
    client_secret = f"secret_{uuid.uuid4().hex[:24]}"
    
    txn = models.PaymentTransaction(
        invoice_id=invoice.id,
        gateway=payload.gateway,
        payment_intent_id=payment_intent_id,
        amount=invoice.amount,
        currency=invoice.currency,
        status="Pending",
        gateway_response={"client_secret": client_secret, "intent_created": datetime.utcnow().isoformat()}
    )
    db.add(txn)
    db.commit()
    
    return {
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "amount": invoice.amount,
        "currency": invoice.currency,
        "payment_intent_id": payment_intent_id,
        "client_secret": client_secret,
        "gateway": payload.gateway,
        "status": "requires_payment_method"
    }

@router.post("/invoices/{invoice_id}/confirm-payment", response_model=InvoiceResponse)
def confirm_payment(
    invoice_id: int,
    payload: PaymentConfirmRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    if invoice.status == "Paid":
        return invoice
        
    patient = db.query(models.PatientProfile).filter(models.PatientProfile.id == invoice.patient_id).first()
    if patient:
        verify_patient_access(patient, current_user, db)

    txn = db.query(models.PaymentTransaction).filter(
        models.PaymentTransaction.invoice_id == invoice.id,
        models.PaymentTransaction.payment_intent_id == payload.payment_intent_id
    ).first()

    if not txn:
        txn = models.PaymentTransaction(
            invoice_id=invoice.id,
            gateway=payload.payment_method,
            payment_intent_id=payload.payment_intent_id,
            amount=invoice.amount,
            currency=invoice.currency,
            status="Pending"
        )
        db.add(txn)
        db.flush()

    tx_id = payload.gateway_transaction_id or f"txn_{uuid.uuid4().hex[:12]}"
    txn.status = "Success"
    txn.gateway_transaction_id = tx_id
    txn.gateway_response = {
        "status": "succeeded",
        "payment_method": payload.payment_method,
        "completed_at": datetime.utcnow().isoformat()
    }

    # Generate Digital Receipt Signature
    receipt_data = {
        "invoice_number": invoice.invoice_number,
        "patient_id": invoice.patient_id,
        "amount": invoice.amount,
        "currency": invoice.currency,
        "paid_at": datetime.utcnow().isoformat(),
        "transaction_id": tx_id
    }
    receipt_bytes = json.dumps(receipt_data, sort_keys=True).encode('utf-8')
    signature = hmac.new(SECRET_KEY.encode('utf-8'), msg=receipt_bytes, digestmod=hashlib.sha256).hexdigest()

    invoice.status = "Paid"
    invoice.paid_at = datetime.utcnow()
    invoice.payment_method = payload.payment_method
    invoice.receipt_signature = signature
    invoice.updated_by = current_user.id

    db.commit()
    db.refresh(invoice)
    return invoice

@router.get("/invoices/{invoice_id}/receipt")
def get_payment_receipt(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    if invoice.status != "Paid":
        raise HTTPException(status_code=400, detail="Receipt is only available for paid invoices")

    patient = db.query(models.PatientProfile).filter(models.PatientProfile.id == invoice.patient_id).first()
    if patient:
        verify_patient_access(patient, current_user, db)

    return {
        "receipt_header": "OFFICIAL HEALTHCARE PAYMENT RECEIPT",
        "invoice_number": invoice.invoice_number,
        "patient_id": invoice.patient_id,
        "patient_name": patient.full_name if patient else "Patient",
        "health_id": patient.health_id if patient else "",
        "amount": invoice.amount,
        "currency": invoice.currency,
        "formatted_amount": f"{invoice.amount / 100:.2f} {invoice.currency}",
        "paid_at": invoice.paid_at.isoformat() if invoice.paid_at else "",
        "payment_method": invoice.payment_method,
        "line_items": invoice.line_items,
        "digital_signature": invoice.receipt_signature,
        "issuer": "HealthID AI Platform"
    }

from fastapi.responses import Response

@router.get("/invoices/{id}/pdf")
def download_invoice_pdf(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    patient = db.query(models.PatientProfile).filter(models.PatientProfile.id == invoice.patient_id).first()
    patient_name = getattr(patient, 'full_name', f"Patient #{invoice.patient_id}") if patient else f"Patient #{invoice.patient_id}"

    from pdf_generator import generate_invoice_pdf
    inv_data = {
        "invoice_number": invoice.invoice_number,
        "amount": invoice.amount,
        "currency": invoice.currency,
        "status": invoice.status,
        "line_items": invoice.line_items
    }
    pdf_bytes = generate_invoice_pdf(inv_data, patient_name)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={invoice.invoice_number}.pdf"}
    )
