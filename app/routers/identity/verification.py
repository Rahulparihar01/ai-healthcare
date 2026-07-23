from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from pydantic import BaseModel
from database import get_db
import models
from utils import send_email_otp

router = APIRouter(prefix="/identity/verify", tags=["Identity - Verification"])

class OTPVerifyRequest(BaseModel):
    email: str
    otp_code: str

class PasswordResetRequest(BaseModel):
    email: str
    otp_code: str
    new_password: str

class ForgotPasswordRequest(BaseModel):
    email: str

def generate_db_otp(db: Session, user_id: int, otp_type: str = "email") -> str:
    db.query(models.OTPVerification).filter(
        models.OTPVerification.user_id == user_id,
        models.OTPVerification.type == otp_type,
        models.OTPVerification.is_used == False
    ).update({"is_used": True}, synchronize_session=False)

    otp_code = str(random.randint(100000, 999999))
    expires = datetime.utcnow() + timedelta(minutes=10)
    
    db_otp = models.OTPVerification(
        otp_code=otp_code,
        user_id=user_id,
        type=otp_type,
        expires_at=expires
    )
    db.add(db_otp)
    db.commit()
    return otp_code

@router.post("/email-otp")
def verify_otp(request: OTPVerifyRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    otp_entry = db.query(models.OTPVerification).filter(
        models.OTPVerification.user_id == user.id,
        models.OTPVerification.otp_code == request.otp_code,
        models.OTPVerification.type == "email",
        models.OTPVerification.is_used == False,
        models.OTPVerification.expires_at > datetime.utcnow()
    ).first()
    
    if not otp_entry:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        
    otp_entry.is_used = True
    user.is_email_verified = True
    db.commit()
    
    return {"message": "Email verified successfully"}

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        return {"message": "If that email is registered, a password reset OTP has been sent."}
        
    otp_code = generate_db_otp(db, user.id, "password_reset")
    send_email_otp(user.email, otp_code)
    
    return {"message": "If that email is registered, a password reset OTP has been sent."}

@router.post("/reset-password")
def reset_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    from auth import get_password_hash
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    otp_entry = db.query(models.OTPVerification).filter(
        models.OTPVerification.user_id == user.id,
        models.OTPVerification.otp_code == request.otp_code,
        models.OTPVerification.type == "password_reset",
        models.OTPVerification.is_used == False,
        models.OTPVerification.expires_at > datetime.utcnow()
    ).first()
    
    if not otp_entry:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        
    otp_entry.is_used = True
    user.hashed_password = get_password_hash(request.new_password)
    
    # Audit log
    audit_log = models.AuditLog(
        user_id=user.id,
        action="PASSWORD_CHANGE",
        status="SUCCESS"
    )
    db.add(audit_log)
    
    db.commit()
    
    return {"message": "Password has been reset successfully"}
