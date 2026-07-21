from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from database import get_db
import models
from auth import RequireRole

router = APIRouter(prefix="/facilities", tags=["Facilities"])

class FacilityCreate(BaseModel):
    name: str
    address: str
    license_number: str
    contact_email: str
    contact_phone: str

class FacilityResponse(FacilityCreate):
    id: int
    class Config:
        from_attributes = True

# --- Laboratory Endpoints ---

@router.post("/labs/create", response_model=FacilityResponse, status_code=status.HTTP_201_CREATED)
def register_lab(
    lab: FacilityCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.SUPER_ADMIN.value]))
):
    db_lab = models.Laboratory(**lab.model_dump())
    db.add(db_lab)
    db.commit()
    db.refresh(db_lab)
    return db_lab

@router.get("/labs/list", response_model=List[FacilityResponse])
def get_labs(db: Session = Depends(get_db)):
    return db.query(models.Laboratory).all()

@router.put("/labs/update", response_model=FacilityResponse)
def update_lab(
    lab_id: int,
    lab: FacilityCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.SUPER_ADMIN.value]))
):
    db_lab = db.query(models.Laboratory).filter(models.Laboratory.id == lab_id).first()
    if not db_lab:
        raise HTTPException(status_code=404, detail="Laboratory not found")
        
    for key, value in lab.model_dump().items():
        setattr(db_lab, key, value)
        
    db.commit()
    db.refresh(db_lab)
    return db_lab

@router.delete("/labs/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_lab(
    lab_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.SUPER_ADMIN.value]))
):
    db_lab = db.query(models.Laboratory).filter(models.Laboratory.id == lab_id).first()
    if not db_lab:
        raise HTTPException(status_code=404, detail="Laboratory not found")
        
    db.delete(db_lab)
    db.commit()
    return None

# --- Pharmacy Endpoints ---

@router.post("/pharmacies/create", response_model=FacilityResponse, status_code=status.HTTP_201_CREATED)
def register_pharmacy(
    pharmacy: FacilityCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.SUPER_ADMIN.value]))
):
    db_pharmacy = models.Pharmacy(**pharmacy.model_dump())
    db.add(db_pharmacy)
    db.commit()
    db.refresh(db_pharmacy)
    return db_pharmacy

@router.get("/pharmacies/list", response_model=List[FacilityResponse])
def get_pharmacies(db: Session = Depends(get_db)):
    return db.query(models.Pharmacy).all()

@router.put("/pharmacies/update", response_model=FacilityResponse)
def update_pharmacy(
    pharmacy_id: int,
    pharmacy: FacilityCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.SUPER_ADMIN.value]))
):
    db_pharmacy = db.query(models.Pharmacy).filter(models.Pharmacy.id == pharmacy_id).first()
    if not db_pharmacy:
        raise HTTPException(status_code=404, detail="Pharmacy not found")
        
    for key, value in pharmacy.model_dump().items():
        setattr(db_pharmacy, key, value)
        
    db.commit()
    db.refresh(db_pharmacy)
    return db_pharmacy

@router.delete("/pharmacies/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_pharmacy(
    pharmacy_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequireRole([models.RoleEnum.SUPER_ADMIN.value]))
):
    db_pharmacy = db.query(models.Pharmacy).filter(models.Pharmacy.id == pharmacy_id).first()
    if not db_pharmacy:
        raise HTTPException(status_code=404, detail="Pharmacy not found")
        
    db.delete(db_pharmacy)
    db.commit()
    return None
