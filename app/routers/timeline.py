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
    event_type: str = None,
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
    
    if event_type and event_type.lower() != "all":
        query = query.filter(models.TimelineEvent.event_type.ilike(f"%{event_type}%"))

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

@router.get("/{health_id}/summary")
def get_timeline_ai_summary(
    health_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Aggregate all timeline events into a structured clinical summary."""
    from cache import cache_get, cache_set
    cache_key = f"timeline_summary_{health_id}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    profile = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == health_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Patient not found")

    events = db.query(models.TimelineEvent).filter(
        models.TimelineEvent.patient_id == profile.id
    ).order_by(models.TimelineEvent.event_date.desc()).limit(30).all()

    if not events:
        res = {"health_id": health_id, "summary": "No clinical timeline events recorded yet."}
        cache_set(cache_key, res, expire_seconds=300)
        return res

    event_titles = [f"- [{e.event_date.strftime('%Y-%m-%d')}] {e.event_type.upper()}: {e.title}" for e in events if e.event_date]
    name_str = getattr(profile, 'full_name', None) or f"{getattr(profile, 'first_name', '')} {getattr(profile, 'last_name', '')}".strip()
    summary_text = f"Patient {name_str} has {len(events)} recorded encounter(s):\n" + "\n".join(event_titles)

    result = {
        "health_id": health_id,
        "patient_name": name_str,
        "total_events": len(events),
        "summary": summary_text
    }
    cache_set(cache_key, result, expire_seconds=300)
    return result

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

