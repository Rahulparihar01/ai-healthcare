from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import sys
import hmac
import hashlib
import json

from database import get_db
import models
from auth import get_current_user, SECRET_KEY
from auth_middleware import require_permission

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ai_pipeline')))
from copilot_engine import compare_medical_reports, auto_assign_icd10
from embeddings import generate_embedding

# Import the extractor from the ai_pipeline (with fallback)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ai_pipeline')))
try:
    from extractor import extract_information
    from worker import process_document_background
except ImportError:
    def extract_information(path):
        return {"error": "Could not load extractor module.", "report_category": "Unknown"}
    def process_document_background(record_id, record_type, file_path):
        pass

def verify_patient_access(patient: models.PatientProfile, current_user: models.User, db: Session):
    if current_user.role == models.RoleEnum.SUPER_ADMIN.value or current_user.role == models.RoleEnum.HOSPITAL_ADMIN.value:
        return
    
    if current_user.role == models.RoleEnum.PATIENT.value:
        if patient.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this patient's records")
        return
        
    if current_user.role == models.RoleEnum.DOCTOR.value:
        doctor_profile = db.query(models.DoctorProfile).filter(models.DoctorProfile.user_id == current_user.id).first()
        if doctor_profile:
            assignment = db.query(models.PatientAssignment).filter(
                models.PatientAssignment.doctor_id == doctor_profile.id,
                models.PatientAssignment.patient_id == patient.id,
                models.PatientAssignment.status == "Active"
            ).first()
            if assignment:
                return
                
            consent = db.query(models.PatientConsent).filter(
                models.PatientConsent.patient_id == patient.id,
                models.PatientConsent.provider_id == current_user.id,
                models.PatientConsent.status == "Active"
            ).first()
            if consent:
                return
                
        raise HTTPException(status_code=403, detail="No active assignment or consent for this patient")


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
async def create_medical_record(
    health_id: str,
    record: RecordCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission("diagnosis.create"))
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
        icd10_code = record.data.get('icd10_code')
        if not icd10_code:
            icd10_code = await auto_assign_icd10(
                record.data.get('condition_name', ''), 
                record.data.get('clinical_notes', '')
            )
            
        db_diag = models.Diagnosis(
            visit_id=record.visit_id,
            patient_id=patient.id,
            doctor_id=doctor_id,
            condition_name=record.data.get('condition_name'),
            icd10_code=icd10_code,
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
        # E-Prescription Enhancements: Generate a cryptographic signature
        prescription_payload = {
            "patient_id": patient.id,
            "doctor_id": doctor_id,
            "medications": record.data.get('medications', []),
            "timestamp": datetime.utcnow().isoformat()
        }
        payload_bytes = json.dumps(prescription_payload, sort_keys=True).encode('utf-8')
        signature = hmac.new(SECRET_KEY.encode('utf-8'), msg=payload_bytes, digestmod=hashlib.sha256).hexdigest()
        
        enhanced_instructions = record.data.get('instructions', '')
        enhanced_instructions += f"\n\n--- DIGITAL SIGNATURE ---\nIssuer ID: {doctor_id}\nSignature: {signature}\n-------------------------"
        
        db_pres = models.Prescription(
            visit_id=record.visit_id,
            patient_id=patient.id,
            doctor_id=doctor_id,
            medications=record.data.get('medications', []),
            instructions=enhanced_instructions
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
        if timeline_event.title and timeline_event.summary:
            embedding = await generate_embedding(f"{timeline_event.title} {timeline_event.summary}")
            timeline_event.embedding = embedding
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
    current_user: models.User = Depends(require_permission("document.upload"))
):
    patient = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == health_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    if not file.filename.endswith((".pdf", ".jpg", ".png", ".jpeg")):
        raise HTTPException(status_code=400, detail="Invalid file format.")
    
    upload_dir = os.path.join(os.path.dirname(__file__), "..", "private", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    safe_filename = f"{health_id}_{int(datetime.utcnow().timestamp())}_{file.filename}"
    file_path = os.path.join(upload_dir, safe_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        created_id = None
        timeline_event = None
        
        if record_type == 'lab_report':
            db_lab = models.LabReport(
                visit_id=visit_id,
                patient_id=patient.id,
                test_name="Processing...",
                results={},
                file_url="",
                processing_status="Processing"
            )
            db.add(db_lab)
            db.flush()
            created_id = db_lab.id
            db_lab.file_url = safe_filename
            
            timeline_event = models.TimelineEvent(
                patient_id=patient.id,
                event_type="LabReport",
                reference_id=db_lab.id,
                title=f"Lab Report (Processing)",
                summary="AI is analyzing this document..."
            )
            
        elif record_type == 'radiology':
            db_rad = models.Radiology(
                visit_id=visit_id,
                patient_id=patient.id,
                scan_type="Processing...",
                file_url="",
                ai_analysis={},
                processing_status="Processing"
            )
            db.add(db_rad)
            db.flush()
            created_id = db_rad.id
            db_rad.file_url = safe_filename
            
            timeline_event = models.TimelineEvent(
                patient_id=patient.id,
                event_type="Radiology",
                reference_id=db_rad.id,
                title=f"Radiology Scan (Processing)",
                summary="AI is analyzing this document..."
            )
            
        else: # document
            db_doc = models.MedicalDocument(
                patient_id=patient.id,
                uploader_id=current_user.id,
                document_type="Processing...",
                file_url="",
                extracted_data={},
                processing_status="Processing"
            )
            db.add(db_doc)
            db.flush()
            created_id = db_doc.id
            db_doc.file_url = safe_filename
            
            timeline_event = models.TimelineEvent(
                patient_id=patient.id,
                event_type="Document",
                reference_id=db_doc.id,
                title=f"Document (Processing)",
                summary="AI is analyzing this document..."
            )
            
        if timeline_event:
            db.add(timeline_event)
            
        db.commit()
        
        # Enqueue Celery Task for AI Processing
        if created_id and record_type in ['lab_report', 'radiology', 'document']:
            process_document_background.delay(created_id, record_type, file_path)

        file_url_out = f"/records/download/{record_type if record_type != 'document' else 'document'}/{created_id}"
        return {"message": "Upload successful and queued for processing", "id": created_id, "file_url": file_url_out}

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=List[TimelineEventResponse])
def get_patient_timeline(
    health_id: str,
    event_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    patient = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == health_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    verify_patient_access(patient, current_user, db)
        
    query = db.query(models.TimelineEvent).filter(models.TimelineEvent.patient_id == patient.id)
    
    if event_type:
        query = query.filter(models.TimelineEvent.event_type == event_type)
        
    events = query.order_by(models.TimelineEvent.event_date.desc()).offset(skip).limit(limit).all()
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
        
    patient = db.query(models.PatientProfile).filter(models.PatientProfile.id == record.patient_id).first()
    if patient:
        verify_patient_access(patient, current_user, db)
        
    return record

@router.put("/update")
def update_record(
    event_type: str,
    reference_id: int,
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission("diagnosis.update"))
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
        
    patient = db.query(models.PatientProfile).filter(models.PatientProfile.id == record.patient_id).first()
    if patient:
        verify_patient_access(patient, current_user, db)
        
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

class CompareRequest(BaseModel):
    doc1_id: int
    doc2_id: int

@router.post("/compare")
async def compare_records(
    request: CompareRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission("document.view"))
):
    doc1 = db.query(models.MedicalDocument).filter(models.MedicalDocument.id == request.doc1_id).first()
    doc2 = db.query(models.MedicalDocument).filter(models.MedicalDocument.id == request.doc2_id).first()
    
    if not doc1 or not doc2:
        raise HTTPException(status_code=404, detail="One or both documents not found")
        
    delta = await compare_medical_reports(doc1.extracted_data, doc2.extracted_data)
    return {"doc1_id": doc1.id, "doc2_id": doc2.id, "comparison": delta}

@router.get("/download/{record_type}/{id}")
def download_record_file(
    record_type: str,
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    record = None
    if record_type == 'lab_report':
        record = db.query(models.LabReport).filter(models.LabReport.id == id).first()
    elif record_type == 'radiology':
        record = db.query(models.Radiology).filter(models.Radiology.id == id).first()
    elif record_type == 'document':
        record = db.query(models.MedicalDocument).filter(models.MedicalDocument.id == id).first()
        
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    patient = db.query(models.PatientProfile).filter(models.PatientProfile.id == record.patient_id).first()
    if patient:
        verify_patient_access(patient, current_user, db)
        
    file_path = os.path.join(os.path.dirname(__file__), "..", "private", "uploads", record.file_url)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
        
    return FileResponse(file_path)

