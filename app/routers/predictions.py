from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import RequireRole
from ai_pipeline.predictive_engine import (
    calculate_health_score,
    predict_readmission_risk,
    detect_early_disease_signals,
    predict_medication_adherence
)

router = APIRouter(prefix="/predict", tags=["Predictive Analytics"])

def _get_patient_data(health_id: str, db: Session):
    patient = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == health_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    diseases = db.query(models.Disease).filter(models.Disease.patient_id == patient.id).all()
    medications = db.query(models.Medication).filter(models.Medication.patient_id == patient.id).all()
    
    return {
        "age": 45, # Mock age
        "gender": patient.gender,
        "diseases": [d.disease_name for d in diseases if d.status == "Chronic"],
        "medications": [m.medicine_name for m in medications if m.status == "Active"]
    }

@router.get("/health-score/{health_id}")
async def get_health_score(
    health_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.DOCTOR.value, models.RoleEnum.SUPER_ADMIN.value]))
):
    patient_data = _get_patient_data(health_id, db)
    return await calculate_health_score(patient_data)

@router.get("/readmission-risk/{health_id}")
async def get_readmission_risk(
    health_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.DOCTOR.value, models.RoleEnum.SUPER_ADMIN.value]))
):
    patient_data = _get_patient_data(health_id, db)
    return await predict_readmission_risk(patient_data)

@router.get("/early-signals/{health_id}")
async def get_early_signals(
    health_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.DOCTOR.value, models.RoleEnum.SUPER_ADMIN.value]))
):
    patient_data = _get_patient_data(health_id, db)
    return await detect_early_disease_signals(patient_data)

@router.get("/preventive-recommendations/{health_id}")
async def get_preventive_recommendations(
    health_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.DOCTOR.value, models.RoleEnum.SUPER_ADMIN.value]))
):
    patient_data = _get_patient_data(health_id, db)
    return await predict_medication_adherence(patient_data)
