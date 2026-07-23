from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
from auth import RequireRole, get_current_user

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("/", response_model=List[dict])
def get_alerts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.DOCTOR.value, models.RoleEnum.SUPER_ADMIN.value]))
):
    if current_user.role == models.RoleEnum.SUPER_ADMIN.value:
        alerts = db.query(models.Alert).filter(models.Alert.is_read == False).all()
    else:
        # Fetch alerts assigned to this doctor or unassigned alerts for their hospital
        doctor_profile = db.query(models.DoctorProfile).filter(models.DoctorProfile.user_id == current_user.id).first()
        if not doctor_profile:
            return []
            
        alerts = db.query(models.Alert).filter(
            models.Alert.is_read == False,
            (models.Alert.doctor_id == doctor_profile.id) | (models.Alert.doctor_id == None)
        ).all()
        
    return [
        {
            "id": a.id,
            "patient_id": a.patient_id,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "message": a.message,
            "reference_id": a.reference_id,
            "created_at": a.created_at.isoformat() if a.created_at else None
        }
        for a in alerts
    ]

@router.put("/{alert_id}/read")
def mark_alert_read(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.DOCTOR.value, models.RoleEnum.SUPER_ADMIN.value]))
):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.is_read = True
    db.commit()
    return {"status": "success", "message": "Alert marked as read"}
