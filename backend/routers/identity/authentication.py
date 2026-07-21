from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel
import secrets
import random
import uuid

from database import get_db
import models
from utils import send_email_otp

# We need to import the password functions from somewhere. 
# Previously they were in auth.py which we are deleting.
# Let's move get_password_hash, verify_password, create_access_token, create_refresh_token to a new security.py or keep them in authentication.py.
# For now, I'll put them in here or in security.py. Wait, the old auth.py imported them from `auth`.
# Wait, `auth.py` had: `from auth import get_password_hash, verify_password...` - wait, the file itself was `auth.py`, how did it import from `auth`? 
# Ah, `auth.py` in the root backend directory! Let me check the root directory.

router = APIRouter(prefix="/identity/auth", tags=["Identity - Authentication"])

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

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserRegister, db: Session = Depends(get_db)):
    # Basic registration logic
    # Need get_password_hash from the root auth.py module
    from auth import get_password_hash
    
    existing_user_by_username = db.query(models.User).filter(models.User.username == user.username).first()
    existing_user_by_email = db.query(models.User).filter(models.User.email == user.email).first()

    if existing_user_by_username and existing_user_by_username.is_email_verified:
        raise HTTPException(status_code=400, detail="Username already registered and verified. Please login.")
    if existing_user_by_email and existing_user_by_email.is_email_verified:
        raise HTTPException(status_code=400, detail="Email already registered and verified. Please login.")
        
    hashed_password = get_password_hash(user.password)
    
    db_user = existing_user_by_username or existing_user_by_email
    if db_user:
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
    
    return {"message": "User registered successfully. Please verify your email with the OTP sent to you."}

@router.post("/login", response_model=TokenResponse)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    from auth import verify_password, create_access_token, create_refresh_token, REFRESH_TOKEN_EXPIRE_DAYS
    
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_email_verified and user.role != models.RoleEnum.SUPER_ADMIN.value:
        raise HTTPException(status_code=403, detail="Email not verified. Please verify your email first.")
        
    # Device Tracking & Unknown Device Logic
    user_agent = request.headers.get("user-agent", "Unknown")
    ip_address = request.client.host
    
    device_name = "Unknown Device"
    device_type = "Unknown"
    if "Windows" in user_agent:
        device_type = "Windows"
    elif "Android" in user_agent:
        device_type = "Android"
    elif "iPhone" in user_agent or "iPad" in user_agent:
        device_type = "iPhone"
    elif "Mac OS X" in user_agent:
        device_type = "Mac"
    elif "Linux" in user_agent:
        device_type = "Linux"

    # In a real app, device_id might be sent in headers by the client. We simulate it here by user agent string hash for now.
    device_identifier_hash = str(hash(user_agent))
    
    device = db.query(models.UserDevice).filter(
        models.UserDevice.user_id == user.id,
        models.UserDevice.device_id == device_identifier_hash
    ).first()
    
    if not device:
        # UNKNOWN DEVICE DETECTED
        device = models.UserDevice(
            user_id=user.id,
            device_id=device_identifier_hash,
            device_name=device_name,
            device_type=device_type,
            is_trusted=False,
            last_login_ip=ip_address,
            last_login_at=datetime.utcnow()
        )
        db.add(device)
        # Here we would normally trigger an OTP flow for unknown device:
        # 1. Generate OTP
        # 2. Send Email
        # 3. Notify Patient
        # For this skeleton, we just log it as an audit log.
        
        audit_log = models.AuditLog(
            user_id=user.id,
            action="UNKNOWN_DEVICE_LOGIN",
            ip_address=ip_address,
            status="WARNING"
        )
        db.add(audit_log)
    else:
        device.last_login_ip = ip_address
        device.last_login_at = datetime.utcnow()
        
    # Log successful login
    audit_log = models.AuditLog(
        user_id=user.id,
        action="LOGIN",
        ip_address=ip_address,
        status="SUCCESS"
    )
    db.add(audit_log)

    access_token = create_access_token(data={"sub": user.username})
    refresh_token_str = create_refresh_token()
    
    expires = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    db_refresh_token = models.RefreshToken(
        token=refresh_token_str,
        user_id=user.id,
        expires_at=expires
    )
    db.add(db_refresh_token)
    
    # Session Management
    session_token = str(uuid.uuid4())
    user_session = models.UserSession(
        user_id=user.id,
        session_token=session_token,
        ip_address=ip_address,
        user_agent=user_agent,
        device_id=device.device_id
    )
    db.add(user_session)
    
    db.commit()
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token_str, 
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    from auth import create_access_token
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
