from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel

from database import get_db
import models
from auth import RequireRole, get_current_user
from datetime import datetime
from ai_pipeline.copilot_engine import check_prescription_safety, generate_case_history, explain_abnormal_lab

router = APIRouter(prefix="/copilot", tags=["Copilot Assistive Intelligence"])

class PrescriptionCheckRequest(BaseModel):
    health_id: str
    proposed_medications: List[Dict[str, Any]]

class WarningResponse(BaseModel):
    alert_type: str
    severity: str
    message: str

@router.post("/check-prescription", response_model=List[WarningResponse])
async def check_prescription(
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
    
    warnings = await check_prescription_safety(profile.id, allergy_list, med_list, request.proposed_medications)
    return warnings

@router.get("/{health_id}/case-history")
async def get_case_history(
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
    
    latest_event_date = timeline_events[-1].event_date if timeline_events and timeline_events[-1].event_date else None
    
    if profile.cached_case_history and profile.case_history_updated_at:
        if latest_event_date and profile.case_history_updated_at >= latest_event_date:
            return {"health_id": profile.health_id, "case_history": profile.cached_case_history, "cached": True}
        elif not latest_event_date:
            return {"health_id": profile.health_id, "case_history": profile.cached_case_history, "cached": True}
            
    history_text = await generate_case_history(events_list, labs_list, diseases_list)
    
    profile.cached_case_history = history_text
    profile.case_history_updated_at = datetime.utcnow()
    db.commit()
    
    return {"health_id": profile.health_id, "case_history": history_text, "cached": False}

@router.get("/explain-lab")
async def explain_lab_value(
    biomarker: str,
    value: str,
    health_id: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.DOCTOR.value, models.RoleEnum.SUPER_ADMIN.value]))
):
    patient_context = "No specific patient context provided."
    if health_id:
        profile = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == health_id).first()
        if profile:
            # Gather some basic context like age, gender, chronic diseases
            diseases = db.query(models.Disease).filter(models.Disease.patient_id == profile.id).all()
            disease_names = [d.disease_name for d in diseases]
            patient_context = f"Patient is {profile.gender}. Chronic conditions: {', '.join(disease_names) if disease_names else 'None'}."

    explanation = await explain_abnormal_lab(biomarker, value, patient_context)
    return {"biomarker": biomarker, "value": value, "explanation": explanation}

class ChatRequest(BaseModel):
    query: str
    health_id: str
    language: str = "English"

@router.post("/chat")
async def copilot_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    from routers.search import semantic_search
    # Fetch top 3 relevant records using semantic search
    context_records = await semantic_search(query=request.query, health_id=request.health_id, limit=3, db=db, current_user=current_user)
    
    context_text = "\n".join([f"- {r['title']}: {r['summary']}" for r in context_records])
    
    from ai_pipeline.copilot_engine import client
    
    system_prompt = (
        f"You are an intelligent medical copilot assistant. Answer the user's question using ONLY the provided context from their medical records. "
        f"If the answer is not in the context, explicitly say so. Be concise. "
        f"IMPORTANT: You MUST reply in the {request.language} language. "
        f"Output MUST be a JSON object with 'answer' (string) and 'confidence_score' (integer 0-100)."
    )
    user_prompt = f"Context:\n{context_text}\n\nQuestion: {request.query}"
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=300
        )
        import json
        result = json.loads(response.choices[0].message.content.strip())
        answer = result.get("answer", "")
        confidence_score = result.get("confidence_score", 100)
        needs_review = confidence_score < 80
        
        patient = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == request.health_id).first()
        
        audit_log = models.AIAuditLog(
            feature_name="doctor_chat",
            input_prompt=user_prompt,
            ai_output=answer,
            reasoning=f"Confidence: {confidence_score}",
            confidence_score=confidence_score,
            patient_id=patient.id if patient else None,
            created_by=current_user.id
        )
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return {
            "answer": answer, 
            "sources": context_records, 
            "confidence_score": confidence_score, 
            "needs_review": needs_review,
            "audit_id": audit_log.id
        }
    except Exception as e:
        print(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate answer")

@router.post("/patient-chat")
async def patient_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    from routers.search import semantic_search
    # Fetch top 3 relevant records using semantic search
    context_records = await semantic_search(query=request.query, health_id=request.health_id, limit=3, db=db, current_user=current_user)
    
    context_text = "\n".join([f"- {r['title']}: {r['summary']}" for r in context_records])
    
    from ai_pipeline.copilot_engine import client
    
    system_prompt = (
        f"You are a helpful, empathetic medical assistant talking directly to a patient. "
        f"Answer the patient's question using ONLY the provided context from their medical records. "
        f"Use simple, non-medical language (around a 6th-grade reading level) to explain things clearly. "
        f"If the answer is not in the context, explicitly say so. Be comforting and concise. "
        f"IMPORTANT: You MUST reply in the {request.language} language. "
        f"Output MUST be a JSON object with 'answer' (string) and 'confidence_score' (integer 0-100)."
    )
    user_prompt = f"Context:\n{context_text}\n\nQuestion: {request.query}"
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=300
        )
        import json
        result = json.loads(response.choices[0].message.content.strip())
        answer = result.get("answer", "")
        confidence_score = result.get("confidence_score", 100)
        needs_review = confidence_score < 80
        
        patient = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == request.health_id).first()
        
        audit_log = models.AIAuditLog(
            feature_name="patient_chat",
            input_prompt=user_prompt,
            ai_output=answer,
            reasoning=f"Confidence: {confidence_score}",
            confidence_score=confidence_score,
            patient_id=patient.id if patient else None,
            created_by=current_user.id
        )
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return {
            "answer": answer, 
            "sources": context_records, 
            "confidence_score": confidence_score, 
            "needs_review": needs_review,
            "audit_id": audit_log.id
        }
    except Exception as e:
        print(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate answer")
