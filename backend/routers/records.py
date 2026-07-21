from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
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

class RecordCreate(BaseModel):
    record_type: str # 'visit', 'diagnosis', 'prescription'
    data: Dict[str, Any]
    hospital_id: Optional[int] = None
    visit_id: Optional[int] = None

class TimelineEventResponse(BaseModel):
    id: int
    event_type: str
    reference_id: int
    event_date: datetime
    title: str
    summary: Optional[str]
    
    class Config:
        from_attributes = True

@router.post("/create")
def create_medical_record(
    health_id: str,
    record: RecordCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.DOCTOR.value]))
):
    patient = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == health_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    doctor_profile = db.query(models.DoctorProfile).filter(models.DoctorProfile.user_id == current_user.id).first()
    doctor_id = doctor_profile.id if doctor_profile else None
    hospital_id = record.hospital_id or (doctor_profile.hospital_id if doctor_profile else None)

    timeline_event = None
    created_id = None

    if record.record_type == 'visit':
        db_visit = models.Visit(
            patient_id=patient.id,
            doctor_id=doctor_id,
            hospital_id=hospital_id,
            chief_complaint=record.data.get('chief_complaint'),
            notes=record.data.get('notes'),
            status=record.data.get('status', 'Completed')
        )
        db.add(db_visit)
        db.flush() # get ID without committing
        created_id = db_visit.id
        
        timeline_event = models.TimelineEvent(
            patient_id=patient.id,
            event_type="Visit",
            reference_id=db_visit.id,
            title=f"Visit: {db_visit.chief_complaint or 'General Consultation'}",
            summary=db_visit.notes
        )

    elif record.record_type == 'diagnosis':
        db_diag = models.Diagnosis(
            visit_id=record.visit_id,
            patient_id=patient.id,
            doctor_id=doctor_id,
            condition_name=record.data.get('condition_name'),
            icd10_code=record.data.get('icd10_code'),
            severity=record.data.get('severity'),
            clinical_notes=record.data.get('clinical_notes')
        )
        db.add(db_diag)
        db.flush()
        created_id = db_diag.id
        
        timeline_event = models.TimelineEvent(
            patient_id=patient.id,
            event_type="Diagnosis",
            reference_id=db_diag.id,
            title=f"Diagnosis: {db_diag.condition_name}",
            summary=f"Severity: {db_diag.severity}. {db_diag.clinical_notes}"
        )

    elif record.record_type == 'prescription':
        db_pres = models.Prescription(
            visit_id=record.visit_id,
            patient_id=patient.id,
            doctor_id=doctor_id,
            medications=record.data.get('medications', []),
            instructions=record.data.get('instructions')
        )
        db.add(db_pres)
        db.flush()
        created_id = db_pres.id
        
        med_names = [m.get('name') for m in record.data.get('medications', []) if m.get('name')]
        summary = f"Prescribed: {', '.join(med_names)}" if med_names else "Prescription issued"
        
        timeline_event = models.TimelineEvent(
            patient_id=patient.id,
            event_type="Prescription",
            reference_id=db_pres.id,
            title="Prescription Issued",
            summary=summary
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid record_type")

    if timeline_event:
        db.add(timeline_event)
        
    db.commit()
    
    return {"message": f"{record.record_type.capitalize()} created successfully", "id": created_id}

@router.post("/upload")
async def upload_report(
    health_id: str,
    record_type: str = Form(...), # 'lab_report', 'radiology', 'document'
    visit_id: Optional[int] = Form(None),
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
    
    safe_filename = f"{health_id}_{int(datetime.utcnow().timestamp())}_{file.filename}"
    file_path = os.path.join(upload_dir, safe_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        extracted_data = extract_information(file_path)
        file_url = f"/public/uploads/{safe_filename}"
        
        created_id = None
        timeline_event = None
        
        if record_type == 'lab_report':
            db_lab = models.LabReport(
                visit_id=visit_id,
                patient_id=patient.id,
                test_name=extracted_data.get("report_category", "General Lab Test"),
                results=extracted_data,
                file_url=file_url,
                status="Completed"
            )
            db.add(db_lab)
            db.flush()
            created_id = db_lab.id
            
            timeline_event = models.TimelineEvent(
                patient_id=patient.id,
                event_type="LabReport",
                reference_id=db_lab.id,
                title=f"Lab Report: {db_lab.test_name}",
                summary="Lab results uploaded and available for review."
            )
            
        elif record_type == 'radiology':
            db_rad = models.Radiology(
                visit_id=visit_id,
                patient_id=patient.id,
                scan_type=extracted_data.get("report_category", "Radiology Scan"),
                file_url=file_url,
                ai_analysis=extracted_data
            )
            db.add(db_rad)
            db.flush()
            created_id = db_rad.id
            
            timeline_event = models.TimelineEvent(
                patient_id=patient.id,
                event_type="Radiology",
                reference_id=db_rad.id,
                title=f"Radiology Scan: {db_rad.scan_type}",
                summary="Radiology images and AI analysis available."
            )
            
        else: # document
            db_doc = models.MedicalDocument(
                patient_id=patient.id,
                uploader_id=current_user.id,
                document_type=extracted_data.get("report_category", "Medical Document"),
                file_url=file_url,
                extracted_data=extracted_data
            )
            db.add(db_doc)
            db.flush()
            created_id = db_doc.id
            
            timeline_event = models.TimelineEvent(
                patient_id=patient.id,
                event_type="Document",
                reference_id=db_doc.id,
                title=f"Document Uploaded: {db_doc.document_type}",
                summary="External medical document added to records."
            )
            
        if timeline_event:
            db.add(timeline_event)
            
        db.commit()
        return {"message": "Upload successful", "id": created_id, "file_url": file_url}

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=List[TimelineEventResponse])
def get_patient_timeline(
    health_id: str,
    event_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    patient = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == health_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    query = db.query(models.TimelineEvent).filter(models.TimelineEvent.patient_id == patient.id)
    
    if event_type:
        query = query.filter(models.TimelineEvent.event_type == event_type)
        
    events = query.order_by(models.TimelineEvent.event_date.desc()).all()
    return events

@router.get("/profile")
def get_record_profile(
    event_type: str,
    reference_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Fetch the full detail payload for a specific timeline event reference."""
    record = None
    if event_type == 'Visit':
        record = db.query(models.Visit).filter(models.Visit.id == reference_id).first()
    elif event_type == 'Diagnosis':
        record = db.query(models.Diagnosis).filter(models.Diagnosis.id == reference_id).first()
    elif event_type == 'Prescription':
        record = db.query(models.Prescription).filter(models.Prescription.id == reference_id).first()
    elif event_type == 'LabReport':
        record = db.query(models.LabReport).filter(models.LabReport.id == reference_id).first()
    elif event_type == 'Radiology':
        record = db.query(models.Radiology).filter(models.Radiology.id == reference_id).first()
    elif event_type == 'Document':
        record = db.query(models.MedicalDocument).filter(models.MedicalDocument.id == reference_id).first()
        
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    return record

@router.put("/update")
def update_record(
    event_type: str,
    reference_id: int,
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.DOCTOR.value]))
):
    """Update fields on a specific record."""
    record = None
    if event_type == 'Visit':
        record = db.query(models.Visit).filter(models.Visit.id == reference_id).first()
    elif event_type == 'Diagnosis':
        record = db.query(models.Diagnosis).filter(models.Diagnosis.id == reference_id).first()
    elif event_type == 'Prescription':
        record = db.query(models.Prescription).filter(models.Prescription.id == reference_id).first()
    elif event_type == 'LabReport':
        record = db.query(models.LabReport).filter(models.LabReport.id == reference_id).first()
    elif event_type == 'Radiology':
        record = db.query(models.Radiology).filter(models.Radiology.id == reference_id).first()
    elif event_type == 'Document':
        record = db.query(models.MedicalDocument).filter(models.MedicalDocument.id == reference_id).first()
        
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    for key, value in data.items():
        if hasattr(record, key):
            setattr(record, key, value)
            
    # Optionally append an updated event to the timeline
    timeline_event = models.TimelineEvent(
        patient_id=record.patient_id,
        event_type=event_type,
        reference_id=reference_id,
        title=f"Updated {event_type}",
        summary=f"Record #{reference_id} was updated."
    )
    db.add(timeline_event)
    
    db.commit()
    return {"message": "Record updated successfully"}
