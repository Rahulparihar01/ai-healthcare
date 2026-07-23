from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
from auth import RequireRole, get_current_user

router = APIRouter(prefix="/timeline", tags=["Timeline"])

@router.get("/{health_id}")
def get_medical_timeline(
    health_id: str,
    skip: int = 0,
    limit: int = 20,
    disease_keyword: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    profile = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == health_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    from sqlalchemy import or_
    
    query = db.query(models.TimelineEvent).filter(
        models.TimelineEvent.patient_id == profile.id
    )
    
    if disease_keyword:
        query = query.filter(
            or_(
                models.TimelineEvent.title.ilike(f"%{disease_keyword}%"),
                models.TimelineEvent.summary.ilike(f"%{disease_keyword}%")
            )
        )
        
    events = query.order_by(models.TimelineEvent.event_date.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "reference_id": e.reference_id,
            "event_date": e.event_date.isoformat() if e.event_date else None,
            "title": e.title,
            "summary": e.summary
        }
        for e in events
    ]

@router.get("/{health_id}/biomarkers")
def get_biomarker_trends(
    health_id: str,
    biomarker: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    profile = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == health_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    results = db.query(models.LabResult).filter(
        models.LabResult.patient_id == profile.id,
        models.LabResult.biomarker_name.ilike(f"%{biomarker}%")
    ).order_by(models.LabResult.recorded_at.asc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": r.id,
            "biomarker_name": r.biomarker_name,
            "value": r.value,
            "unit": r.unit,
            "recorded_at": r.recorded_at.isoformat() if r.recorded_at else None
        }
        for r in results
    ]
