from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
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

class DoctorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    hospital_id: int
    department_id: int
    license_number: str | None
    experience: int | None
    qualification: str | None
    consultation_fee: int | None
    availability: Dict[str, Any]
    status: str

@router.post("/onboard", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def onboard_doctor(
    doctor: DoctorCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(RequireRole(["Hospital Admin", "Super Admin"]))
):
    if current_user.role != models.RoleEnum.SUPER_ADMIN.value:
        doctor.hospital_id = current_user.hospital_id
        
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
    return db_doctor

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
        query = query.filter(models.DoctorProfile.hospital_id == current_user.hospital_id)
    else:
        # Patients and Super Admins can view all, or filter by requested hospital_id
        if hospital_id:
            query = query.filter(models.DoctorProfile.hospital_id == hospital_id)
            
    if department_id:
        query = query.filter(models.DoctorProfile.department_id == department_id)
        
    return query.all()
