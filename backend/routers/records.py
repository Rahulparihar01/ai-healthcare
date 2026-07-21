from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import sys

from database import get_db
import models
from auth import RequireRole, get_current_user

# Import the extractor from the ai_pipeline (with fallback)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ai_pipeline')))
try:
    from extractor import extract_information
except ImportError:
    def extract_information(path):
        return {"error": "Could not load extractor module.", "report_category": "Unknown"}

router = APIRouter(prefix="/records", tags=["Medical Records"])

class MedicalRecordCreate(BaseModel):
    record_type: str
    notes: str
    structured_data: Dict[str, Any] = {}
    hospital_id: Optional[int] = None

class MedicalRecordResponse(BaseModel):
    id: int
    record_type: str
    notes: str
    date_recorded: datetime
    structured_data: Dict[str, Any]
    
    class Config:
        from_attributes = True

class MedicalReportResponse(BaseModel):
    id: int
    report_category: str
    file_url: str
    ai_summary: Dict[str, Any]
    date_uploaded: datetime
    
    class Config:
        from_attributes = True

@router.post("/create", response_model=MedicalRecordResponse)
def create_medical_record(
    health_id: str,
    record: MedicalRecordCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.DOCTOR.value]))
):
    patient = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == health_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    db_record = models.MedicalRecord(
        patient_id=patient.id,
        doctor_id=current_user.id,
        hospital_id=record.hospital_id,
        record_type=record.record_type,
        notes=record.notes,
        structured_data=record.structured_data
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.post("/upload", response_model=MedicalReportResponse)
async def upload_report(
    health_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.DOCTOR.value, models.RoleEnum.LAB_TECHNICIAN.value]))
):
    patient = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == health_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    if not file.filename.endswith((".pdf", ".jpg", ".png", ".jpeg")):
        raise HTTPException(status_code=400, detail="Invalid file format.")
    
    upload_dir = os.path.join(os.path.dirname(__file__), "..", "public", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename to avoid overwrites
    safe_filename = f"{health_id}_{int(datetime.utcnow().timestamp())}_{file.filename}"
    file_path = os.path.join(upload_dir, safe_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        # Call the OCR/AI stub from ai_pipeline
        extracted_data = extract_information(file_path)
        
        # Save to database
        db_report = models.MedicalReport(
            patient_id=patient.id,
            uploaded_by=current_user.id,
            report_category=extracted_data.get("report_category", "Uncategorized"),
            file_url=f"/public/uploads/{safe_filename}",
            ai_summary=extracted_data
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        
        return db_report

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path) # Cleanup on failure
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/timeline")
def get_patient_timeline(
    health_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    patient = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == health_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    records = db.query(models.MedicalRecord).filter(models.MedicalRecord.patient_id == patient.id).all()
    reports = db.query(models.MedicalReport).filter(models.MedicalReport.patient_id == patient.id).all()
    
    # Combine and sort by date descending
    timeline = []
    for r in records:
        timeline.append({"type": "record", "date": r.date_recorded, "data": MedicalRecordResponse.model_validate(r)})
    for r in reports:
        timeline.append({"type": "report", "date": r.date_uploaded, "data": MedicalReportResponse.model_validate(r)})
        
    timeline.sort(key=lambda x: x["date"], reverse=True)
    
    return {"health_id": health_id, "timeline": timeline}
