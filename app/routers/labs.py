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
    
    class Config:
        from_attributes = True

@router.get("/pending", response_model=List[LabTestOrderResponse])
def get_pending_lab_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in [models.RoleEnum.SUPER_ADMIN.value, models.RoleEnum.LAB_TECHNICIAN.value]:
        raise HTTPException(status_code=403, detail="Not authorized to view pending lab orders")
        
    orders = db.query(models.LabTestOrder).filter(models.LabTestOrder.status == "Pending").all()
    return orders

class CompleteOrderRequest(BaseModel):
    results: dict

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
    
    # Save the structured results into a new LabReport or LabResult
    report = models.LabReport(
        visit_id=order.visit_id,
        patient_id=order.patient_id,
        test_name=", ".join([t.get("name", "Unknown Test") for t in order.tests]),
        results=request.results,
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
        summary="Lab technician uploaded results for pending tests."
    )
    db.add(timeline_event)
    
    db.commit()
    db.refresh(report)
    
    # Try to import and trigger notification (will be implemented next)
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
