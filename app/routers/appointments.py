from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
import models
from auth import get_current_user
from auth_middleware import require_permission

router = APIRouter(prefix="/appointments", tags=["Appointments"])

class AppointmentCreate(BaseModel):
    patient_health_id: str
    doctor_id: int
    hospital_id: Optional[int] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    notes: Optional[str] = None

class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    doctor_id: int
    hospital_id: Optional[int]
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    notes: Optional[str]

@router.post("/create", response_model=AppointmentResponse)
def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    patient = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == appointment.patient_health_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    doctor = db.query(models.DoctorProfile).filter(models.DoctorProfile.id == appointment.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
        
    end_time = appointment.end_time or (appointment.start_time + timedelta(minutes=30))
    
    # Check for double booking
    overlapping = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == doctor.id,
        models.Appointment.status == "Scheduled",
        models.Appointment.start_time < end_time,
        models.Appointment.end_time > appointment.start_time
    ).first()
    
    if overlapping:
        raise HTTPException(status_code=409, detail="Doctor already has an appointment during this time slot")
        
    db_apt = models.Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        hospital_id=appointment.hospital_id or doctor.hospital_id,
        start_time=appointment.start_time,
        end_time=end_time,
        status="Scheduled",
        notes=appointment.notes
    )
    db.add(db_apt)
    db.commit()
    db.refresh(db_apt)
    
    try:
        from notifications_worker import send_email_notification
        if patient.user:
            send_email_notification.delay(
                patient.user.email,
                "Appointment Scheduled",
                f"Hello {patient.full_name}, your appointment is scheduled for {appointment.start_time.strftime('%Y-%m-%d %H:%M')}."
            )
    except (ImportError, Exception) as e:
        print(f"Failed to queue notification: {e}")
    
    return db_apt

@router.get("/list", response_model=List[AppointmentResponse])
def list_appointments(
    doctor_id: Optional[int] = None,
    patient_health_id: Optional[str] = None,
    date: Optional[datetime] = Query(None, description="Filter by exact date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Appointment)
    
    if doctor_id:
        query = query.filter(models.Appointment.doctor_id == doctor_id)
        
    if patient_health_id:
        patient = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == patient_health_id).first()
        if patient:
            query = query.filter(models.Appointment.patient_id == patient.id)
            
    if date:
        next_day = date + timedelta(days=1)
        query = query.filter(
            models.Appointment.start_time >= date,
            models.Appointment.start_time < next_day
        )
        
    return query.order_by(models.Appointment.start_time.asc()).all()

@router.put("/{id}/status")
def update_appointment_status(
    id: int,
    status: str = Query(..., pattern="^(Scheduled|Completed|Cancelled|No-Show)$"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    apt = db.query(models.Appointment).filter(models.Appointment.id == id).first()
    if not apt:
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    apt.status = status
    db.commit()
    return {"message": f"Appointment status updated to {status}"}
