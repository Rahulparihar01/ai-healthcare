from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from database import get_db
import models
from auth import RequireRole, get_current_user
from ai_pipeline.embeddings import generate_embedding

router = APIRouter(prefix="/search", tags=["Semantic Search"])

@router.get("/semantic")
async def semantic_search(
    query: str,
    health_id: str = None,
    disease_name: str = None,
    start_date: str = None,
    end_date: str = None,
    event_type: str = None,
    limit: int = Query(5, le=20),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query_embedding = await generate_embedding(query)
    
    stmt = select(models.TimelineEvent)
    
    if health_id:
        profile = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == health_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Patient not found")
        stmt = stmt.filter(models.TimelineEvent.patient_id == profile.id)
        
    if event_type:
        stmt = stmt.filter(models.TimelineEvent.event_type.ilike(f"%{event_type}%"))
        
    if disease_name:
        stmt = stmt.filter(models.TimelineEvent.summary.ilike(f"%{disease_name}%"))
        
    if start_date:
        stmt = stmt.filter(models.TimelineEvent.event_date >= start_date)
        
    if end_date:
        stmt = stmt.filter(models.TimelineEvent.event_date <= end_date)
        
    stmt = stmt.order_by(models.TimelineEvent.embedding.cosine_distance(query_embedding)).limit(limit)
    
    results = db.execute(stmt).scalars().all()
    
    return [
        {
            "id": r.id,
            "event_type": r.event_type,
            "title": r.title,
            "summary": r.summary,
            "event_date": r.event_date.isoformat() if r.event_date else None
        }
        for r in results
    ]
