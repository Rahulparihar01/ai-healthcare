from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional

from database import get_db
from models import PatientProfile, Hospital
from ai_pipeline.entity_mapper import map_extracted_data_to_models

router = APIRouter(
    prefix="/knowledge-graph",
    tags=["Knowledge Graph"]
)

class IngestDataRequest(BaseModel):
    patient_id: int
    hospital_id: Optional[int] = None
    lab_report_id: Optional[int] = None
    extracted_data: Dict[str, Any]

@router.post("/ingest", status_code=status.HTTP_201_CREATED)
def ingest_knowledge_graph_data(request: IngestDataRequest, db: Session = Depends(get_db)):
    """
    Ingests raw extracted JSON data from the AI pipeline, converts it to 
    Knowledge Graph entities (Disease, Medication, Allergy, LabResult), 
    and saves them to the database.
    """
    # Verify patient exists
    patient = db.query(PatientProfile).filter(PatientProfile.id == request.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    # Map data to models
    models_to_save = map_extracted_data_to_models(
        extracted_data=request.extracted_data,
        patient_id=request.patient_id,
        lab_report_id=request.lab_report_id
    )
    
    if not models_to_save:
        return {"message": "No valid entities found in the extracted data to ingest."}
        
    # Save to database
    try:
        db.add_all(models_to_save)
        db.commit()
        return {
            "message": "Knowledge Graph entities successfully ingested.",
            "entities_inserted": len(models_to_save)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error during ingestion: {str(e)}")
