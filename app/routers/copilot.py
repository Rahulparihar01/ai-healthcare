from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel

from database import get_db
import models
from auth import RequireRole, get_current_user
from ai_pipeline.copilot_engine import check_prescription_safety, generate_case_history

router = APIRouter(prefix="/copilot", tags=["Copilot Assistive Intelligence"])

class PrescriptionCheckRequest(BaseModel):
    health_id: str
    proposed_medications: List[Dict[str, Any]]

class WarningResponse(BaseModel):
    alert_type: str
    severity: str
    message: str

@router.post("/check-prescription", response_model=List[WarningResponse])
def check_prescription(
    request: PrescriptionCheckRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.DOCTOR.value, models.RoleEnum.SUPER_ADMIN.value]))
):
    profile = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == request.health_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    allergies = db.query(models.Allergy).filter(models.Allergy.patient_id == profile.id).all()
    medications = db.query(models.Medication).filter(models.Medication.patient_id == profile.id).all()
    
    allergy_list = [{"allergen": a.allergen, "severity": a.severity, "reaction": a.reaction} for a in allergies]
    med_list = [{"medicine_name": m.medicine_name, "dosage": m.dosage, "frequency": m.frequency} for m in medications]
    
    warnings = check_prescription_safety(profile.id, allergy_list, med_list, request.proposed_medications)
    return warnings

@router.get("/{health_id}/case-history")
def get_case_history(
    health_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.DOCTOR.value, models.RoleEnum.SUPER_ADMIN.value]))
):
    profile = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == health_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    timeline_events = db.query(models.TimelineEvent).filter(models.TimelineEvent.patient_id == profile.id).order_by(models.TimelineEvent.event_date.asc()).all()
    diseases = db.query(models.Disease).filter(models.Disease.patient_id == profile.id).all()
    lab_results = db.query(models.LabResult).filter(models.LabResult.patient_id == profile.id).order_by(models.LabResult.recorded_at.desc()).limit(20).all()
    
    events_list = [{"event_date": e.event_date.isoformat() if e.event_date else None, "title": e.title, "summary": e.summary} for e in timeline_events]
    diseases_list = [{"disease_name": d.disease_name, "status": d.status} for d in diseases]
    labs_list = [{"biomarker_name": l.biomarker_name, "value": l.value, "unit": l.unit} for l in lab_results]
    
    history_text = generate_case_history(events_list, labs_list, diseases_list)
    return {"health_id": profile.health_id, "case_history": history_text}
