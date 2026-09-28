from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database import get_db
import models
from auth import get_current_user

router = APIRouter(prefix="/labs", tags=["Lab Technician Portal"])

class LabTestOrderResponse(BaseModel):
    id: int
    visit_id: Optional[int]
    patient_id: int
    doctor_id: Optional[int]
    tests: list
    clinical_notes: Optional[str]
    status: str
    created_at: datetime
    patient_health_id: Optional[str] = None
    patient_name: Optional[str] = None
    
    class Config:
        from_attributes = True

def _serialize_order(order: models.LabTestOrder) -> LabTestOrderResponse:
    return LabTestOrderResponse(
        id=order.id,
        visit_id=order.visit_id,
        patient_id=order.patient_id,
        doctor_id=order.doctor_id,
        tests=order.tests or [],
        clinical_notes=order.clinical_notes,
        status=order.status,
        created_at=order.created_at,
        patient_health_id=order.patient.health_id if order.patient else None,
        patient_name=order.patient.full_name if order.patient else None
    )

@router.get("/pending", response_model=List[LabTestOrderResponse])
def get_pending_lab_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in [models.RoleEnum.SUPER_ADMIN.value, models.RoleEnum.LAB_TECHNICIAN.value]:
        raise HTTPException(status_code=403, detail="Not authorized to view pending lab orders")
        
    orders = db.query(models.LabTestOrder).filter(models.LabTestOrder.status == "Pending").all()
    return [_serialize_order(o) for o in orders]

@router.get("/history", response_model=List[LabTestOrderResponse])
def get_lab_orders_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in [models.RoleEnum.SUPER_ADMIN.value, models.RoleEnum.LAB_TECHNICIAN.value]:
        raise HTTPException(status_code=403, detail="Not authorized to view lab order history")
        
    orders = db.query(models.LabTestOrder).filter(models.LabTestOrder.status != "Pending").order_by(models.LabTestOrder.created_at.desc()).limit(100).all()
    return [_serialize_order(o) for o in orders]

class CompleteOrderRequest(BaseModel):
    results: Optional[dict] = None
    notes: Optional[str] = None
    file_url: Optional[str] = None

@router.post("/orders/{order_id}/complete")
def complete_lab_order(
    order_id: int,
    request: CompleteOrderRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in [models.RoleEnum.SUPER_ADMIN.value, models.RoleEnum.LAB_TECHNICIAN.value]:
        raise HTTPException(status_code=403, detail="Not authorized to complete lab orders")
        
    order = db.query(models.LabTestOrder).filter(models.LabTestOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Lab order not found")
        
    order.status = "Completed"
    
    res_data = request.results or {}
    if request.notes:
        res_data["notes"] = request.notes
        
    # Save the structured results into a new LabReport
    report = models.LabReport(
        visit_id=order.visit_id,
        patient_id=order.patient_id,
        test_name=", ".join([t.get("name", "Unknown Test") for t in (order.tests or [])]),
        results=res_data,
        file_url=request.file_url or "",
        status="Completed",
        processing_status="Completed"
    )
    db.add(report)
    
    # Create a timeline event
    timeline_event = models.TimelineEvent(
        patient_id=order.patient_id,
        event_type="LabReport",
        reference_id=order.id,
        title=f"Lab Results Completed",
        summary=f"Tests fulfilled: {', '.join([t.get('name', 'Test') for t in (order.tests or [])])}."
    )
    db.add(timeline_event)
    
    db.commit()
    db.refresh(report)
    
    # Try to import and trigger notification
    try:
        from notifications_worker import send_email_notification
        patient = db.query(models.PatientProfile).filter(models.PatientProfile.id == order.patient_id).first()
        if patient and patient.user:
            send_email_notification.delay(
                patient.user.email,
                "Your Lab Results are Ready",
                f"Hello {patient.full_name}, your lab results are now available in the portal."
            )
    except (ImportError, Exception) as e:
        print(f"Failed to queue lab notification: {e}")
        
    return {"message": "Lab order completed successfully", "report_id": report.id}
