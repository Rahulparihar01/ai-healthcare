from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/identity/sessions", tags=["Identity - Sessions"])

class SessionResponse(BaseModel):
    id: int
    session_token: str
    ip_address: str | None
    user_agent: str | None
    device_id: str | None
    is_active: bool

    class Config:
        from_attributes = True

@router.get("/current", response_model=List[SessionResponse])
def get_current_sessions(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = db.query(models.UserSession).filter(
        models.UserSession.user_id == current_user.id,
        models.UserSession.is_active == True
    ).all()
    return sessions

@router.delete("/{session_id}")
def logout_session(session_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(models.UserSession).filter(
        models.UserSession.id == session_id,
        models.UserSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session.is_active = False
    
    # Audit log
    audit_log = models.AuditLog(
        user_id=current_user.id,
        action="LOGOUT",
        status="SUCCESS"
    )
    db.add(audit_log)
    
    db.commit()
    return {"message": "Session logged out"}

@router.delete("/all")
def logout_all_devices(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(models.UserSession).filter(
        models.UserSession.user_id == current_user.id,
        models.UserSession.is_active == True
    ).update({"is_active": False})
    
    # Also revoke refresh tokens
    db.query(models.RefreshToken).filter(
        models.RefreshToken.user_id == current_user.id,
        models.RefreshToken.is_revoked == False
    ).update({"is_revoked": True})
    
    # Audit log
    audit_log = models.AuditLog(
        user_id=current_user.id,
        action="LOGOUT_ALL_DEVICES",
        status="SUCCESS"
    )
    db.add(audit_log)
    
    db.commit()
    return {"message": "Logged out from all devices"}
