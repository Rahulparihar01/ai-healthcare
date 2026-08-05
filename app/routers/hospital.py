from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, List, Optional

from database import get_db
import models
from auth import RequireRole

router = APIRouter(prefix="/hospitals", tags=["Hospitals"])

class HospitalCreate(BaseModel):
    organization_id: Optional[int] = None
    name: str
    address: str
    contact_email: str
    contact_phone: str
    settings: Dict[str, Any] = {}

class HospitalResponse(HospitalCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int

@router.post("/create", response_model=HospitalResponse, status_code=status.HTTP_201_CREATED)
def create_hospital(
    hospital: HospitalCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.SUPER_ADMIN.value]))
):
    db_hospital = models.Hospital(**hospital.model_dump())
    db_hospital.created_by = current_user.id
    db_hospital.updated_by = current_user.id
    db.add(db_hospital)
    db.commit()
    db.refresh(db_hospital)
    return db_hospital

@router.get("/list", response_model=List[HospitalResponse])
def get_hospitals(db: Session = Depends(get_db)):
    return db.query(models.Hospital).all()

@router.put("/update", response_model=HospitalResponse)
def update_hospital(
    hospital_id: int,
    hospital: HospitalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.SUPER_ADMIN.value, models.RoleEnum.HOSPITAL_ADMIN.value]))
):
    db_hospital = db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
    if not db_hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
        
    for key, value in hospital.model_dump().items():
        setattr(db_hospital, key, value)
    
    db_hospital.updated_by = current_user.id
        
    db.commit()
    db.refresh(db_hospital)
    return db_hospital

@router.get("/profile", response_model=HospitalResponse)
def get_hospital(
    hospital_id: int, db: Session = Depends(get_db)):
    db_hospital = db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
    if not db_hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return db_hospital

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_hospital(
    hospital_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.SUPER_ADMIN.value]))
):
    db_hospital = db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
    if not db_hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
        
    db.delete(db_hospital)
    db.commit()
    return None
