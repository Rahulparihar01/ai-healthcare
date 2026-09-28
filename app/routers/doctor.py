from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict

from database import get_db
import models
from auth import get_current_user, RequireRole, get_tenant_scope

router = APIRouter(prefix="/doctors", tags=["Doctors"])

class DoctorCreate(BaseModel):
    user_id: int
    hospital_id: int | None = None
    department_id: int
    license_number: str | None = None
    experience: int | None = None
    qualification: str | None = None
    consultation_fee: int | None = None
    availability: Dict[str, Any] = {}

class DoctorFullRegister(BaseModel):
    title: str | None = "Dr."
    name: str | None = None
    username: str | None = None
    password: str
    email: str
    phone_number: str | None = None
    hospital_id: int | None = None
    department: str | None = "General Medicine"
    department_id: int | None = None
    specialization: str | None = None
    experience: int | None = None
    qualification: str | None = None
    consultation_fee: int | None = 5000
    license_number: str | None = None
    medical_council: str | None = None

class DoctorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    hospital_id: int
    department_id: int
    license_number: str | None = None
    experience: int | None = None
    qualification: str | None = None
    specialization: str | None = None
    consultation_fee: int | None = None
    availability: Dict[str, Any] = {}
    status: str = "Active"
    
    # Detailed presentation fields
    name: str | None = None
    username: str | None = None
    email: str | None = None
    phone_number: str | None = None
    department: str | None = None
    department_name: str | None = None

def _serialize_doctor(doc: models.DoctorProfile) -> DoctorResponse:
    dept_name = doc.department.name if doc.department else "General Medicine"
    user_obj = doc.user
    username = user_obj.username if user_obj else "Unknown"
    email = user_obj.email if user_obj else None
    phone = user_obj.phone_number if user_obj else None
    specialization = doc.qualification or dept_name
    return DoctorResponse(
        id=doc.id,
        user_id=doc.user_id,
        hospital_id=doc.hospital_id,
        department_id=doc.department_id,
        license_number=doc.license_number or "",
        experience=doc.experience,
        qualification=doc.qualification,
        specialization=specialization,
        consultation_fee=doc.consultation_fee,
        availability=doc.availability or {},
        status=doc.status or "Active",
        name=username,
        username=username,
        email=email,
        phone_number=phone,
        department=dept_name,
        department_name=dept_name,
    )

def _get_or_create_hospital(db: Session, hospital_id: Optional[int] = None) -> models.Hospital:
    if hospital_id:
        hosp = db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
        if hosp:
            return hosp
            
    hosp = db.query(models.Hospital).first()
    if not hosp:
        hosp = models.Hospital(
            name="HealthID Central Hospital",
            address="100 Medical Center Drive",
            contact_email="admin@healthid.ai",
            contact_phone="+1-800-HEALTH-ID",
            settings={"status": "Active"}
        )
        db.add(hosp)
        db.commit()
        db.refresh(hosp)
    return hosp

@router.post("/onboard", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def onboard_doctor(
    doctor: DoctorCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(RequireRole(["Hospital Admin", "Super Admin"]))
):
    if current_user.role != models.RoleEnum.SUPER_ADMIN.value:
        if not current_user.hospital_id:
            hosp = _get_or_create_hospital(db)
            current_user.hospital_id = hosp.id
            db.commit()
        doctor.hospital_id = current_user.hospital_id
    else:
        if not doctor.hospital_id:
            hosp = _get_or_create_hospital(db)
            doctor.hospital_id = hosp.id

    if not doctor.hospital_id:
        raise HTTPException(status_code=400, detail="hospital_id is required")
    # Ensure user exists
    db_user = db.query(models.User).filter(models.User.id == doctor.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Ensure hospital exists
    db_hospital = db.query(models.Hospital).filter(models.Hospital.id == doctor.hospital_id).first()
    if not db_hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
        
    # Ensure department exists and belongs to hospital
    db_department = db.query(models.Department).filter(
        models.Department.id == doctor.department_id,
        models.Department.hospital_id == doctor.hospital_id
    ).first()
    if not db_department:
        raise HTTPException(status_code=400, detail="Department not found in the selected hospital")

    # Ensure not already a doctor
    existing_doctor = db.query(models.DoctorProfile).filter(models.DoctorProfile.user_id == doctor.user_id).first()
    if existing_doctor:
        raise HTTPException(status_code=400, detail="User is already onboarded as a doctor")

    db_doctor = models.DoctorProfile(**doctor.model_dump())
    db.add(db_doctor)
    
    # Update user role to Doctor
    db_user.role = models.RoleEnum.DOCTOR.value
    db_user.hospital_id = doctor.hospital_id
    
    db.commit()
    db.refresh(db_doctor)
    return _serialize_doctor(db_doctor)

@router.post("/register", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def register_doctor_full(
    data: DoctorFullRegister,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole(["Hospital Admin", "Super Admin"]))
):
    from auth import get_password_hash
    req_hosp_id = current_user.hospital_id if current_user.role != models.RoleEnum.SUPER_ADMIN.value else data.hospital_id
    hosp = _get_or_create_hospital(db, req_hosp_id)
    hospital_id = hosp.id

    if current_user.role == models.RoleEnum.HOSPITAL_ADMIN.value and not current_user.hospital_id:
        current_user.hospital_id = hospital_id
        db.commit()

    title_prefix = (data.title or "Dr.").strip()
    if data.name:
        candidate_username = f"{title_prefix} {data.name.strip()}"
    else:
        candidate_username = data.username or f"{title_prefix} Doctor"

    user_filter = (models.User.username == candidate_username) | (models.User.email == data.email)
    if data.phone_number:
        user_filter = user_filter | (models.User.phone_number == data.phone_number)

    existing_user = db.query(models.User).filter(user_filter).first()
    if existing_user:
        if existing_user.username == candidate_username:
            detail = f"Doctor '{candidate_username}' already exists. Please choose a different name."
        elif existing_user.email == data.email:
            detail = "Email address already registered"
        else:
            detail = "Phone number already registered"
        raise HTTPException(status_code=400, detail=detail)

    dept = None
    if data.department_id:
        dept = db.query(models.Department).filter(models.Department.id == data.department_id).first()
    if not dept:
        dept_name = data.department or data.specialization or "General Medicine"
        dept = db.query(models.Department).filter(
            models.Department.hospital_id == hospital_id,
            models.Department.name.ilike(dept_name)
        ).first()
        if not dept:
            dept = models.Department(hospital_id=hospital_id, name=dept_name)
            db.add(dept)
            db.flush()

    hashed_pw = get_password_hash(data.password)
    new_user = models.User(
        username=candidate_username,
        email=data.email,
        phone_number=data.phone_number,
        hashed_password=hashed_pw,
        role=models.RoleEnum.DOCTOR.value,
        is_email_verified=True,
        hospital_id=hospital_id
    )
    db.add(new_user)
    db.flush()

    spec_name = data.specialization or data.qualification or dept.name
    new_doc = models.DoctorProfile(
        user_id=new_user.id,
        hospital_id=hospital_id,
        department_id=dept.id,
        license_number=data.license_number or "",
        experience=data.experience,
        qualification=spec_name,
        consultation_fee=data.consultation_fee or 5000,
        availability={"days": ["Mon", "Tue", "Wed", "Thu", "Fri"], "hours": "09:00 - 17:00"}
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return _serialize_doctor(new_doc)

@router.get("/list", response_model=List[DoctorResponse])
def get_doctors(
    department_id: int = None, 
    hospital_id: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.DoctorProfile)
    
    # Scoping logic
    if current_user.role in [models.RoleEnum.DOCTOR.value, models.RoleEnum.HOSPITAL_ADMIN.value]:
        # Lock to their own hospital
        hosp_id = current_user.hospital_id or _get_or_create_hospital(db).id
        query = query.filter(models.DoctorProfile.hospital_id == hosp_id)
    else:
        # Patients and Super Admins can view all, or filter by requested hospital_id
        if hospital_id:
            query = query.filter(models.DoctorProfile.hospital_id == hospital_id)
            
    if department_id:
        query = query.filter(models.DoctorProfile.department_id == department_id)
        
    return [_serialize_doctor(d) for d in query.all()]
