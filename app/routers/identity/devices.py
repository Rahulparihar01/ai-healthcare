from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/identity/devices", tags=["Identity - Devices"])

class DeviceResponse(BaseModel):
    id: int
    device_id: str
    device_name: str | None
    device_type: str | None
    is_trusted: bool
    last_login_ip: str | None
    last_login_at: datetime | None

    class Config:
        from_attributes = True

@router.get("/", response_model=List[DeviceResponse])
def get_user_devices(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    devices = db.query(models.UserDevice).filter(
        models.UserDevice.user_id == current_user.id
    ).all()
    return devices

@router.delete("/{device_id}")
def remove_device(device_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    device = db.query(models.UserDevice).filter(
        models.UserDevice.id == device_id,
        models.UserDevice.user_id == current_user.id
    ).first()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    db.delete(device)
    
    # Audit log
    audit_log = models.AuditLog(
        user_id=current_user.id,
        action="REMOVE_DEVICE",
        status="SUCCESS"
    )
    db.add(audit_log)
    
    db.commit()
    return {"message": "Device removed successfully"}
