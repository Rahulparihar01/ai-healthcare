from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import csv
import io
import json

from database import get_db
import models
from auth import get_current_user
from auth_middleware import require_permission

router = APIRouter(prefix="/audit", tags=["Audit Trail"])

@router.get("/logs")
def get_audit_logs(
    skip: int = 0,
    limit: int = 50,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission("audit.read"))
):
    """Retrieve filtered audit trail records."""
    query = db.query(models.AuditLog)
    
    if user_id:
        query = query.filter(models.AuditLog.user_id == user_id)
    if action:
        query = query.filter(models.AuditLog.action.ilike(f"%{action}%"))
        
    logs = query.order_by(models.AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "ip_address": log.ip_address,
            "status": log.status,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            "details": log.details
        }
        for log in logs
    ]

@router.get("/export")
def export_audit_logs(
    format: str = Query("json", pattern="^(json|csv)$"),
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission("audit.export"))
):
    """Export audit trail logs in CSV or JSON format for compliance audits."""
    query = db.query(models.AuditLog)
    if user_id:
        query = query.filter(models.AuditLog.user_id == user_id)
        
    logs = query.order_by(models.AuditLog.timestamp.desc()).limit(1000).all()

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Log ID", "User ID", "Action", "IP Address", "Status", "Timestamp", "Details"])
        
        for log in logs:
            writer.writerow([
                log.id,
                log.user_id,
                log.action,
                log.ip_address or "",
                log.status,
                log.timestamp.isoformat() if log.timestamp else "",
                json.dumps(log.details) if log.details else ""
            ])
            
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=audit_trail_export.csv"}
        )

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "ip_address": log.ip_address,
            "status": log.status,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            "details": log.details
        }
        for log in logs
    ]
