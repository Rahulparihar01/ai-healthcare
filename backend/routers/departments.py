from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from database import get_db
import models
from auth import get_current_user, RequireRole

router = APIRouter(prefix="/departments", tags=["Hospital Departments"])

class DepartmentCreate(BaseModel):
    hospital_id: int
    name: str
    description: str | None = None

class DepartmentResponse(BaseModel):
    id: int
    hospital_id: int
    name: str
    description: str | None
    is_active: bool

    class Config:
        from_attributes = True

@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    department: DepartmentCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(RequireRole(["Hospital Admin", "Super Admin"]))
):
    db_hospital = db.query(models.Hospital).filter(models.Hospital.id == department.hospital_id).first()
    if not db_hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
        
    db_department = models.Department(**department.dict())
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department

@router.get("/", response_model=List[DepartmentResponse])
def get_departments(hospital_id: int = None, db: Session = Depends(get_db)):
    query = db.query(models.Department)
    if hospital_id:
        query = query.filter(models.Department.hospital_id == hospital_id)
    return query.all()
