import os
import json
from sqlalchemy.orm import Session
from openai import OpenAI
from dotenv import load_dotenv
import models
from database import SessionLocal
from .extractor import extract_information
from .embedding_service import generate_embeddings
from .timeline_generator import generate_timeline_payload

# Absolute import since celery_app is at the root of backend
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from celery_app import celery_app

load_dotenv()



@celery_app.task(name="process_medical_document", bind=True, max_retries=3)
def process_document_background(self, record_id: int, record_type: str, file_path: str):
    """
    Background worker function for asynchronous AI processing.
    """
    print(f"Starting background processing for {record_type} ID: {record_id}")
    db = SessionLocal()
    
    try:
        # 1. Fetch the DB record and corresponding timeline event
        record = None
        event_type_str = ""
        
        if record_type == 'lab_report':
            record = db.query(models.LabReport).filter(models.LabReport.id == record_id).first()
            event_type_str = "LabReport"
        elif record_type == 'radiology':
            record = db.query(models.Radiology).filter(models.Radiology.id == record_id).first()
            event_type_str = "Radiology"
        elif record_type == 'document':
            record = db.query(models.MedicalDocument).filter(models.MedicalDocument.id == record_id).first()
            event_type_str = "Document"
            
        if not record:
            print(f"Record {record_id} of type {record_type} not found.")
            return
            
        timeline_event = db.query(models.TimelineEvent).filter(
            models.TimelineEvent.reference_id == record_id,
            models.TimelineEvent.event_type == event_type_str
        ).first()

        # Define callback to update DB in real-time
        def update_processing_status(status_str: str):
            if record:
                record.processing_status = status_str
            if timeline_event:
                timeline_event.summary = status_str
            db.commit()

        # 2. Extract structured info (OCR + LLM)
        extracted_data = extract_information(file_path, status_callback=update_processing_status)
        summary = extracted_data.get("summary", "AI processing completed.")
        
        # 3. Generate Embeddings (for Search/RAG later)
        # Exclude raw_text to avoid exceeding token limits and focus on high-value structured data
        embedding_payload = {k: v for k, v in extracted_data.items() if k != 'raw_text'}
        text_for_embedding = json.dumps(embedding_payload)
        embedding_vector = generate_embeddings(text_for_embedding)
        
        is_valid = extracted_data.get("is_clinically_valid", True)
        final_status = "Completed" if is_valid else "Needs Review"
        
        # 4. Update the DB Record
        if record_type == 'lab_report':
            record.test_name = extracted_data.get("document_type", record.test_name)
            record.results = extracted_data
            record.processing_status = final_status
        elif record_type == 'radiology':
            record.scan_type = extracted_data.get("document_type", record.scan_type)
            record.ai_analysis = extracted_data
            record.processing_status = final_status
        elif record_type == 'document':
            record.document_type = extracted_data.get("document_type", record.document_type)
            record.extracted_data = extracted_data
            record.embeddings = embedding_vector
            record.processing_status = final_status
            
        # 5. Update Timeline Event
        if timeline_event:
            timeline_payload = generate_timeline_payload(
                event_type_str, 
                extracted_data.get('document_type', 'Unknown'),
                summary
            )
            title = timeline_payload['title']
            if not is_valid:
                title += " (Needs Review)"
            timeline_event.title = title
            timeline_event.summary = timeline_payload['summary']
            
        db.commit()
        print(f"Background processing completed for {record_type} ID: {record_id}")
        
    except Exception as e:
        db.rollback()
        print(f"Background processing failed: {e}")
        
        # Optionally mark as failed if it's the last retry
        if self.request.retries >= self.max_retries:
            if 'record' in locals() and record:
                record.processing_status = "Failed"
                db.commit()
        else:
            raise self.retry(exc=e, countdown=60)
            
    finally:
        db.close()
