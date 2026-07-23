from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict

from database import get_db
import models
from auth import RequireRole, get_current_user, SECRET_KEY, ALGORITHM
from jose import JWTError, jwt

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("/", response_model=List[dict])
def get_alerts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.DOCTOR.value, models.RoleEnum.SUPER_ADMIN.value]))
):
    if current_user.role == models.RoleEnum.SUPER_ADMIN.value:
        alerts = db.query(models.Alert).filter(models.Alert.is_read == False).all()
    else:
        # Fetch alerts assigned to this doctor or unassigned alerts for their hospital
        doctor_profile = db.query(models.DoctorProfile).filter(models.DoctorProfile.user_id == current_user.id).first()
        if not doctor_profile:
            return []
            
        alerts = db.query(models.Alert).filter(
            models.Alert.is_read == False,
            (models.Alert.doctor_id == doctor_profile.id) | (models.Alert.doctor_id == None)
        ).all()
        
    return [
        {
            "id": a.id,
            "patient_id": a.patient_id,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "message": a.message,
            "reference_id": a.reference_id,
            "created_at": a.created_at.isoformat() if a.created_at else None
        }
        for a in alerts
    ]

@router.put("/{alert_id}/read")
def mark_alert_read(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.DOCTOR.value, models.RoleEnum.SUPER_ADMIN.value]))
):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.is_read = True
    db.commit()
    return {"status": "success", "message": "Alert marked as read"}

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_alert(self, user_id: int, message: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    user_id = None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username:
            db = next(get_db())
            user = db.query(models.User).filter(models.User.username == username).first()
            if user:
                user_id = user.id
                await manager.connect(websocket, user_id)
                # Could optionally fetch unread alerts and send them immediately here
                while True:
                    data = await websocket.receive_text()
                    # Keep alive or handle client messages
    except WebSocketDisconnect:
        if user_id:
            manager.disconnect(user_id)
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
