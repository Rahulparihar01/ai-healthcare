from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from database import get_db
import models
from auth import RequireRole, get_password_hash
from typing import Optional

router = APIRouter(prefix="/doctors", tags=["Doctors"])

class DoctorProfileCreate(BaseModel):
    user_id: int
    department: str
    specialization: str
    license_number: str
    medical_council: str

class DoctorProfileResponse(DoctorProfileCreate):
    id: int
    class Config:
        from_attributes = True

class DoctorFullRegister(BaseModel):
    username: str
    password: str
    email: str
    phone_number: str = None
    hospital_id: int
    department: str
    specialization: str
    license_number: str
    medical_council: str

@router.post("/create", response_model=DoctorProfileResponse, status_code=status.HTTP_201_CREATED)
def create_doctor_profile(
    profile: DoctorProfileCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.SUPER_ADMIN.value, models.RoleEnum.HOSPITAL_ADMIN.value]))
):
    # Verify user exists and is a Doctor
    user = db.query(models.User).filter(models.User.id == profile.user_id).first()
    if not user or user.role != models.RoleEnum.DOCTOR.value:
        raise HTTPException(status_code=400, detail="User is not registered as a Doctor")
        
    if current_user.role == models.RoleEnum.HOSPITAL_ADMIN.value:
        if user.hospital_id != current_user.hospital_id:
            raise HTTPException(status_code=403, detail="Cannot create profile for a doctor outside your hospital")

    db_profile = models.DoctorProfile(**profile.model_dump())
    db.add(db_profile)
    
    try:
        db.commit()
        db.refresh(db_profile)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Profile already exists for this user")
        
    return db_profile

@router.get("/profile", response_model=DoctorProfileResponse)
def get_doctor_profile(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(models.DoctorProfile).filter(models.DoctorProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.get("/list", response_model=List[DoctorProfileResponse])
def get_doctors(
    hospital_id: Optional[int] = None, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.DoctorProfile).join(models.User)
    if current_user.role != models.RoleEnum.SUPER_ADMIN.value:
        query = query.filter(models.User.hospital_id == current_user.hospital_id)
    elif hospital_id:
        query = query.filter(models.User.hospital_id == hospital_id)
    return query.all()

@router.put("/update", response_model=DoctorProfileResponse)
def update_doctor_profile(
    user_id: int,
    profile_update: DoctorProfileCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.SUPER_ADMIN.value, models.RoleEnum.HOSPITAL_ADMIN.value]))
):
    profile = db.query(models.DoctorProfile).filter(models.DoctorProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    for key, value in profile_update.model_dump().items():
        setattr(profile, key, value)
        
    db.commit()
    db.refresh(profile)
    return profile

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.SUPER_ADMIN.value, models.RoleEnum.HOSPITAL_ADMIN.value]))
):
    profile = db.query(models.DoctorProfile).filter(models.DoctorProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    db.delete(profile)
    db.commit()
    return None

@router.post("/register", response_model=DoctorProfileResponse, status_code=status.HTTP_201_CREATED)
def register_doctor_full(
    data: DoctorFullRegister,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.SUPER_ADMIN.value, models.RoleEnum.HOSPITAL_ADMIN.value]))
):
    if current_user.role == models.RoleEnum.HOSPITAL_ADMIN.value:
        data.hospital_id = current_user.hospital_id

    # Verify hospital exists
    hospital = db.query(models.Hospital).filter(models.Hospital.id == data.hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
        
    # Check if user exists
    existing_user = db.query(models.User).filter(
        (models.User.username == data.username) | (models.User.email == data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
        
    # 1. Create User
    hashed_password = get_password_hash(data.password)
    db_user = models.User(
        username=data.username,
        email=data.email,
        phone_number=data.phone_number,
        hashed_password=hashed_password,
        role=models.RoleEnum.DOCTOR.value,
        is_email_verified=True,
        hospital_id=data.hospital_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # 2. Create Doctor Profile
    db_profile = models.DoctorProfile(
        user_id=db_user.id,
        department=data.department,
        specialization=data.specialization,
        license_number=data.license_number,
        medical_council=data.medical_council
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    return db_profile
