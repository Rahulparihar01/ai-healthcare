from fastapi import Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from database import get_db
from models import User, RoleEnum, Permission, RolePermission
from auth import get_current_user

from sqlalchemy import inspect

# Default mapping from Permission -> Roles (Used for Seeding and Fallback)
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

    # Hospital & Facility Management
    "hospital.create": [RoleEnum.SUPER_ADMIN],
    "hospital.read": [RoleEnum.SUPER_ADMIN, RoleEnum.HOSPITAL_ADMIN, RoleEnum.DOCTOR, RoleEnum.RECEPTIONIST],
    "hospital.manage": [RoleEnum.SUPER_ADMIN, RoleEnum.HOSPITAL_ADMIN],
    "facility.create": [RoleEnum.SUPER_ADMIN, RoleEnum.HOSPITAL_ADMIN],
    "facility.read": [RoleEnum.SUPER_ADMIN, RoleEnum.HOSPITAL_ADMIN, RoleEnum.DOCTOR],
    "doctor.onboard": [RoleEnum.SUPER_ADMIN, RoleEnum.HOSPITAL_ADMIN],
    "admin.seed": [RoleEnum.SUPER_ADMIN],
}

def get_model_attr(obj, attr_name, default=None):
    if obj is None:
        return default
    try:
        insp = inspect(obj)
        if insp:
            if attr_name in insp.dict:
                return insp.dict[attr_name]
            if attr_name in insp.committed_state:
                val = insp.committed_state[attr_name]
                if val is not inspect.NO_VALUE:
                    return val
            if attr_name == 'id' and insp.identity:
                return insp.identity[0]
    except Exception:
        pass
    try:
        return getattr(obj, attr_name, default)
    except Exception:
        return default

def seed_default_permissions(db: Session):
    """Seed initial permissions and role permissions into the database if empty."""
    existing_count = db.query(Permission).count()
    if existing_count > 0:
        return

    for perm_name, roles in DEFAULT_ROLE_PERMISSIONS.items():
        parts = perm_name.split('.')
        resource = parts[0] if len(parts) > 0 else "system"
        action = parts[1] if len(parts) > 1 else "manage"
        
        perm = Permission(
            name=perm_name,
            resource=resource,
            action=action,
            description=f"Allows {action} access on {resource}"
        )
        db.add(perm)
        db.flush()
        
        for role_val in roles:
            rp = RolePermission(role=role_val, permission_id=perm.id)
            db.add(rp)
            
    db.commit()

class require_permission:
    """
    Dependency class to enforce fine-grained RBAC permissions dynamically via Database.
    """
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(self, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        user_id = get_model_attr(current_user, 'id')
        username = get_model_attr(current_user, 'username')

        user = None
        if user_id:
            try:
                user = db.query(User).filter(User.id == user_id).first()
            except Exception:
                user = None
        if not user and username:
            try:
                user = db.query(User).filter(User.username == username).first()
            except Exception:
                user = None

        user = user or current_user

        role_val = get_model_attr(user, 'role') or get_model_attr(current_user, 'role') or RoleEnum.PATIENT.value
        role_str = role_val.value if hasattr(role_val, 'value') else str(role_val)

        # Super Admin has all permissions implicitly
        if role_str in ["Super Admin", "SUPER_ADMIN", RoleEnum.SUPER_ADMIN.value]:
            return user
            
        # 1. Try querying DB role_permissions
        perm = db.query(Permission).filter(Permission.name == self.required_permission).first()
        if perm:
            has_role_perm = db.query(RolePermission).filter(
                RolePermission.permission_id == perm.id,
                RolePermission.role == role_str
            ).first()
            if has_role_perm:
                return user

        # 2. Fallback to DEFAULT_ROLE_PERMISSIONS
        allowed_roles = DEFAULT_ROLE_PERMISSIONS.get(self.required_permission, [])
        allowed_role_strs = [r.value if hasattr(r, 'value') else str(r) for r in allowed_roles]
        if role_str in allowed_role_strs:
            return user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Operation not permitted. Missing permission: {self.required_permission}"
        )

