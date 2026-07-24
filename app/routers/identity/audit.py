from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/identity/audit", tags=["Identity - Audit Logs"])

class AuditLogResponse(BaseModel):
    id: int
    action: str
    ip_address: str | None
    status: str
    timestamp: datetime
    details: dict | None = None

    class Config:
        from_attributes = True

@router.get("/logs", response_model=List[AuditLogResponse])
def get_audit_logs(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    logs = db.query(models.AuditLog).filter(
        models.AuditLog.user_id == current_user.id
    ).order_by(models.AuditLog.timestamp.desc()).limit(100).all()
    
    return logs

@router.get("/logs/all", response_model=List[AuditLogResponse])
def get_all_audit_logs(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != models.RoleEnum.SUPER_ADMIN.value:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Super Admins can view all audit logs."
        )
        
    logs = db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).limit(500).all()
    return logs
