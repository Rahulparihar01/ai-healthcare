from fastapi import Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from database import get_db
from models import User, RoleEnum
from auth import get_current_user

# Temporary mapping from Permission -> Roles (Fallback for Phase 1 Migration)
# This mimics the RBAC-Permission-Matrix.md
DEFAULT_ROLE_PERMISSIONS = {
    # Patient Demographics & Profile
    "patient.create": [RoleEnum.SUPER_ADMIN, RoleEnum.HOSPITAL_ADMIN, RoleEnum.RECEPTIONIST],
    "patient.read": [RoleEnum.SUPER_ADMIN, RoleEnum.HOSPITAL_ADMIN, RoleEnum.DOCTOR, RoleEnum.RECEPTIONIST, RoleEnum.PATIENT],
    "patient.update": [RoleEnum.SUPER_ADMIN, RoleEnum.HOSPITAL_ADMIN, RoleEnum.RECEPTIONIST, RoleEnum.PATIENT],
    
    # Clinical
    "diagnosis.create": [RoleEnum.SUPER_ADMIN, RoleEnum.DOCTOR],
    "diagnosis.read": [RoleEnum.SUPER_ADMIN, RoleEnum.HOSPITAL_ADMIN, RoleEnum.DOCTOR, RoleEnum.PATIENT],
    "diagnosis.update": [RoleEnum.SUPER_ADMIN, RoleEnum.DOCTOR],
    
    "prescription.create": [RoleEnum.SUPER_ADMIN, RoleEnum.DOCTOR],
    "prescription.read": [RoleEnum.SUPER_ADMIN, RoleEnum.HOSPITAL_ADMIN, RoleEnum.DOCTOR, RoleEnum.PATIENT],
    
    # Lab Orders
    "lab_order.create": [RoleEnum.SUPER_ADMIN, RoleEnum.DOCTOR],
    "lab_order.read": [RoleEnum.SUPER_ADMIN, RoleEnum.HOSPITAL_ADMIN, RoleEnum.DOCTOR, RoleEnum.LAB_TECHNICIAN, RoleEnum.PATIENT],
    
    # Lab Results
    "lab_result.upload": [RoleEnum.SUPER_ADMIN, RoleEnum.LAB_TECHNICIAN],
    "lab_result.edit": [RoleEnum.SUPER_ADMIN, RoleEnum.LAB_TECHNICIAN],
    "lab_result.view": [RoleEnum.SUPER_ADMIN, RoleEnum.HOSPITAL_ADMIN, RoleEnum.DOCTOR, RoleEnum.LAB_TECHNICIAN, RoleEnum.PATIENT],

    # Documents
    "document.upload": [RoleEnum.SUPER_ADMIN, RoleEnum.DOCTOR, RoleEnum.PATIENT],
    "document.view": [RoleEnum.SUPER_ADMIN, RoleEnum.HOSPITAL_ADMIN, RoleEnum.DOCTOR, RoleEnum.PATIENT],
    
    # Billing
    "invoice.create": [RoleEnum.SUPER_ADMIN, RoleEnum.HOSPITAL_ADMIN, RoleEnum.RECEPTIONIST],
    "invoice.read": [RoleEnum.SUPER_ADMIN, RoleEnum.HOSPITAL_ADMIN, RoleEnum.RECEPTIONIST, RoleEnum.PATIENT],
    "invoice.update": [RoleEnum.SUPER_ADMIN, RoleEnum.HOSPITAL_ADMIN, RoleEnum.RECEPTIONIST],
    
    # AI Copilot
    "ai.summary": [RoleEnum.SUPER_ADMIN, RoleEnum.HOSPITAL_ADMIN, RoleEnum.DOCTOR, RoleEnum.PATIENT],
    "ai.chat": [RoleEnum.SUPER_ADMIN, RoleEnum.DOCTOR, RoleEnum.PATIENT],
    
    # Consent
    "consent.grant": [RoleEnum.SUPER_ADMIN, RoleEnum.HOSPITAL_ADMIN, RoleEnum.RECEPTIONIST, RoleEnum.PATIENT],
    "consent.revoke": [RoleEnum.SUPER_ADMIN, RoleEnum.PATIENT],
    "consent.override": [RoleEnum.SUPER_ADMIN],
}

class require_permission:
    """
    Dependency class to enforce fine-grained RBAC permissions.
    In Phase 1, this falls back to a hardcoded mapping. In Phase 4,
    this will query the `role_permissions` table.
    """
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(self, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # Super Admin has all permissions implicitly
        if current_user.role == RoleEnum.SUPER_ADMIN:
            return current_user
            
        allowed_roles = DEFAULT_ROLE_PERMISSIONS.get(self.required_permission, [])
        
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Missing permission: {self.required_permission}"
            )
            
        return current_user
