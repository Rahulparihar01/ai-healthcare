from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from database import get_db
import models
from auth import RequireRole, get_current_user, get_password_hash
from utils import generate_health_id, generate_qr_code

router = APIRouter(prefix="/patients", tags=["Patients"])

class PatientCreate(BaseModel):
    user_id: int
    full_name: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    organ_donor: bool = False
    known_allergies: List[str] = []
    chronic_diseases: List[str] = []
    current_medications: List[str] = []
    past_surgeries: List[str] = []
    insurance_details: Dict[str, Any] = {}

class PatientListResponse(BaseModel):
    id: int
    health_id: str
    name: str
    phone: Optional[str]
    blood_group: Optional[str]
    
    class Config:
        from_attributes = True

class PatientProfileResponse(BaseModel):
    id: int
    health_id: str
    qr_code_path: str
    hospital_id: Optional[int]
    
    full_name: Optional[str]
    dob: Optional[str]
    gender: Optional[str]
    blood_group: Optional[str]
    address: Optional[str]
    profile_photo: Optional[str]
    
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    emergency_contact_relation: Optional[str]
    organ_donor: bool
    
    known_allergies: List[str]
    chronic_diseases: List[str]
    current_medications: List[str]
    past_surgeries: List[str]
    insurance_details: Dict[str, Any]
    
    status: str
    allow_doctor_access: bool
    allow_hospital_access: bool
    emergency_access: bool
    
    class Config:
        from_attributes = True

class PatientFullRegister(BaseModel):
    username: str
    password: str
    email: str
    phone_number: str = None
    
    full_name: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    relationship: Optional[str] = None
    organ_donor: bool = False
    
    known_allergies: List[str] = []
    chronic_diseases: List[str] = []
    current_medications: List[str] = []
    past_surgeries: List[str] = []
    insurance_details: Dict[str, Any] = {}

class PatientProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    profile_photo: Optional[str] = None
    
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    organ_donor: Optional[bool] = None
    
    known_allergies: List[str] = None
    chronic_diseases: List[str] = None
    current_medications: List[str] = None
    past_surgeries: List[str] = None
    insurance_details: Dict[str, Any] = None
    
    status: Optional[str] = None
    allow_doctor_access: Optional[bool] = None
    allow_hospital_access: Optional[bool] = None
    emergency_access: Optional[bool] = None

@router.post("/create", response_model=PatientProfileResponse, status_code=status.HTTP_201_CREATED)
def register_patient(
    patient: PatientCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.SUPER_ADMIN.value, models.RoleEnum.HOSPITAL_ADMIN.value, models.RoleEnum.RECEPTIONIST.value]))
):
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == patient.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Check if patient profile already exists
    if db.query(models.PatientProfile).filter(models.PatientProfile.user_id == user.id).first():
        raise HTTPException(status_code=400, detail="Patient profile already exists for this user")

    health_id = generate_health_id()
    qr_code_path = generate_qr_code(health_id)

    db_profile = models.PatientProfile(
        user_id=user.id,
        health_id=health_id,
        qr_code_path=qr_code_path,
        hospital_id=current_user.hospital_id if current_user.role != models.RoleEnum.SUPER_ADMIN.value else None,
        full_name=patient.full_name,
        dob=patient.dob,
        gender=patient.gender,
        blood_group=patient.blood_group,
        address=patient.address,
        emergency_contact_name=patient.emergency_contact_name,
        emergency_contact_phone=patient.emergency_contact_phone,
        emergency_contact_relation=patient.emergency_contact_relation,
        organ_donor=patient.organ_donor,
        known_allergies=patient.known_allergies,
        chronic_diseases=patient.chronic_diseases,
        current_medications=patient.current_medications,
        past_surgeries=patient.past_surgeries,
        insurance_details=patient.insurance_details
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    return db_profile

@router.get("/list", response_model=List[PatientListResponse])
def get_all_patients(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.SUPER_ADMIN.value, models.RoleEnum.HOSPITAL_ADMIN.value, models.RoleEnum.RECEPTIONIST.value, models.RoleEnum.DOCTOR.value]))
):
    if current_user.role == models.RoleEnum.SUPER_ADMIN.value:
        profiles = db.query(models.PatientProfile).all()
    else:
        profiles = db.query(models.PatientProfile).join(models.User).filter(
            models.User.hospital_id == current_user.hospital_id
        ).all()
        
    results = []
    for p in profiles:
        user = db.query(models.User).filter(models.User.id == p.user_id).first()
        results.append({
            "id": p.id,
            "health_id": p.health_id,
            "name": user.username if user else "Unknown",
            "phone": user.phone_number if user else None,
            "blood_group": p.blood_group
        })
    return results

@router.get("/profile", response_model=PatientProfileResponse)
def get_patient_profile(
    health_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role == models.RoleEnum.PATIENT.value:
        profile = db.query(models.PatientProfile).filter(models.PatientProfile.user_id == current_user.id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Patient profile not found for this user")
    else:
        if not health_id:
            raise HTTPException(status_code=400, detail="health_id query parameter is required for staff")
        profile = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == health_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Patient not found")
        
    return profile

@router.put("/update", response_model=PatientProfileResponse)
def update_patient_profile(
    health_id: str,
    update_data: PatientProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    profile = db.query(models.PatientProfile).filter(models.PatientProfile.health_id == health_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    # Security: only the patient themselves or admins/doctors can update
    if current_user.role == models.RoleEnum.PATIENT.value and profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")
        
    for key, value in update_data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(profile, key, value)
            
    db.commit()
    db.refresh(profile)
    return profile

@router.post("/register", response_model=PatientProfileResponse, status_code=status.HTTP_201_CREATED)
def register_patient_full(
    data: PatientFullRegister,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.SUPER_ADMIN.value, models.RoleEnum.HOSPITAL_ADMIN.value, models.RoleEnum.RECEPTIONIST.value]))
):
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
        role=models.RoleEnum.PATIENT.value,
        is_email_verified=True, 
        hospital_id=current_user.hospital_id if current_user.role != models.RoleEnum.SUPER_ADMIN.value else None
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # 2. Create Profile & Generate ID
    health_id = generate_health_id()
    qr_code_path = generate_qr_code(health_id)

    db_profile = models.PatientProfile(
        user_id=db_user.id,
        health_id=health_id,
        qr_code_path=qr_code_path,
        hospital_id=current_user.hospital_id if current_user.role != models.RoleEnum.SUPER_ADMIN.value else None,
        full_name=data.full_name,
        dob=data.dob,
        gender=data.gender,
        blood_group=data.blood_group,
        address=data.address,
        emergency_contact_name=data.emergency_contact_name,
        emergency_contact_phone=data.emergency_contact_phone,
        emergency_contact_relation=data.emergency_contact_relation,
        organ_donor=data.organ_donor,
        known_allergies=data.known_allergies,
        chronic_diseases=data.chronic_diseases,
        current_medications=data.current_medications,
        past_surgeries=data.past_surgeries,
        insurance_details=data.insurance_details
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    return db_profile
