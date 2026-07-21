from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel
import secrets
import random
import os

from database import get_db
import models
from auth import get_password_hash, verify_password, create_access_token, create_refresh_token, REFRESH_TOKEN_EXPIRE_DAYS, get_current_user
from utils import send_email_otp

router = APIRouter(prefix="/auth", tags=["Authentication"])

class UserRegister(BaseModel):
    username: str
    password: str
    email: str
    phone_number: str = None
    role: str = models.RoleEnum.PATIENT.value
    hospital_id: int | None = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    phone_number: str | None = None
    role: str
    hospital_id: int | None = None
    is_email_verified: bool
    is_active: bool

    class Config:
        from_attributes = True

class RefreshRequest(BaseModel):
    refresh_token: str

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
    # Invalidate existing unused OTPs to prevent replay or confusion
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

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing_user_by_username = db.query(models.User).filter(models.User.username == user.username).first()
    existing_user_by_email = db.query(models.User).filter(models.User.email == user.email).first()

    if existing_user_by_username and existing_user_by_username.is_email_verified:
        raise HTTPException(status_code=400, detail="Username already registered and verified. Please login.")
    if existing_user_by_email and existing_user_by_email.is_email_verified:
        raise HTTPException(status_code=400, detail="Email already registered and verified. Please login.")
        
    hashed_password = get_password_hash(user.password)
    
    db_user = existing_user_by_username or existing_user_by_email
    if db_user:
        # Update existing unverified user
        db_user.username = user.username
        db_user.email = user.email
        db_user.hashed_password = hashed_password
        db_user.role = user.role
        db_user.phone_number = user.phone_number
        db_user.hospital_id = user.hospital_id
    else:
        db_user = models.User(
            username=user.username, 
            hashed_password=hashed_password,
            email=user.email,
            phone_number=user.phone_number,
            role=user.role,
            hospital_id=user.hospital_id
        )
        db.add(db_user)
        
    db.commit()
    db.refresh(db_user)
    
    # Generate and send OTP
    otp_code = generate_db_otp(db, db_user.id, "email")
    email_sent = send_email_otp(db_user.email, otp_code)
    
    if not email_sent:
        # Raise error so frontend knows it failed
        raise HTTPException(status_code=500, detail="Registration saved, but failed to send OTP email. Please check SMTP settings.")
    
    return {"message": "User registered successfully. Please verify your email with the OTP sent to you."}

@router.post("/verify-otp")
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
        # Don't reveal user existence
        return {"message": "If that email is registered, a password reset OTP has been sent."}
        
    otp_code = generate_db_otp(db, user.id, "password_reset")
    send_email_otp(user.email, otp_code)
    
    return {"message": "If that email is registered, a password reset OTP has been sent."}

@router.post("/reset-password")
def reset_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
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
    db.commit()
    
    return {"message": "Password has been reset successfully"}

@router.post("/token", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Ensure they are verified before allowing login
    if not user.is_email_verified and user.role != models.RoleEnum.SUPER_ADMIN.value:
        raise HTTPException(status_code=403, detail="Email not verified. Please verify your email first.")
        
    access_token = create_access_token(data={"sub": user.username})
    refresh_token_str = create_refresh_token()
    
    expires = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    db_refresh_token = models.RefreshToken(
        token=refresh_token_str,
        user_id=user.id,
        expires_at=expires
    )
    db.add(db_refresh_token)
    db.commit()
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token_str, 
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    db_token = db.query(models.RefreshToken).filter(
        models.RefreshToken.token == request.refresh_token,
        models.RefreshToken.is_revoked == False
    ).first()
    
    if not db_token or db_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
        
    user = db.query(models.User).filter(models.User.id == db_token.user_id).first()
    access_token = create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "refresh_token": request.refresh_token,
        "token_type": "bearer"
    }

@router.get("/profile", response_model=UserProfile)
def get_user_profile(current_user: models.User = Depends(get_current_user)):
    """Returns the authenticated user's profile details."""
    return current_user
