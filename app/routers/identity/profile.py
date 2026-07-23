from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/identity/profile", tags=["Identity - Profile Management"])

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    phone_number: str | None = None
    role: str
    hospital_id: int | None = None
    is_email_verified: bool
    is_active: bool
    recovery_email: str | None = None
    recovery_phone: str | None = None

    class Config:
        from_attributes = True

class ProfileUpdateRequest(BaseModel):
    phone_number: str | None = None
    recovery_email: str | None = None
    recovery_phone: str | None = None

@router.get("/me", response_model=UserProfile)
def get_profile(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.put("/update", response_model=UserProfile)
def update_profile(request: ProfileUpdateRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if request.phone_number is not None:
        current_user.phone_number = request.phone_number
    if request.recovery_email is not None:
        current_user.recovery_email = request.recovery_email
    if request.recovery_phone is not None:
        current_user.recovery_phone = request.recovery_phone
        
    db.commit()
    db.refresh(current_user)
    return current_user
