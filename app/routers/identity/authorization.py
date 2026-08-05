from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database import get_db
import models
from auth import get_current_user
from auth_middleware import require_permission, seed_default_permissions, DEFAULT_ROLE_PERMISSIONS

router = APIRouter(prefix="/identity/authorization", tags=["Identity - Authorization"])

class PermissionSchema(BaseModel):
    id: int
    name: str
    resource: str
    action: str
    description: Optional[str]

    class Config:
        from_attributes = True

class RolePermissionUpdate(BaseModel):
    permission_ids: List[int]

@router.post("/seed")
def trigger_seed_permissions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission("hospital.manage"))
):
    """Seed initial permissions and default role permissions into database."""
    seed_default_permissions(db)
    return {"message": "Permissions seeded successfully"}

@router.get("/permissions", response_model=List[PermissionSchema])
def list_all_permissions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """List all available system permissions."""
    seed_default_permissions(db)
    return db.query(models.Permission).all()

@router.get("/my-permissions")
def get_my_permissions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """List permissions granted to the current logged-in user's role."""
    seed_default_permissions(db)
    
    if current_user.role == models.RoleEnum.SUPER_ADMIN.value:
        all_perms = db.query(models.Permission).all()
        return {
            "role": current_user.role,
            "permissions": [p.name for p in all_perms]
        }

    role_perms = db.query(models.RolePermission).filter(
        models.RolePermission.role == current_user.role
    ).all()

    perm_names = [rp.permission.name for rp in role_perms if rp.permission]
    
    # Fallback to default if DB role_permissions count is 0
    if not perm_names:
        perm_names = [p for p, roles in DEFAULT_ROLE_PERMISSIONS.items() if current_user.role in roles]

    return {
        "role": current_user.role,
        "permissions": list(set(perm_names))
    }

@router.get("/roles/{role}/permissions", response_model=List[PermissionSchema])
def get_role_permissions(
    role: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Retrieve permissions assigned to a specific role."""
    seed_default_permissions(db)
    role_perms = db.query(models.RolePermission).filter(models.RolePermission.role == role).all()
    return [rp.permission for rp in role_perms if rp.permission]

@router.post("/roles/{role}/permissions")
def update_role_permissions(
    role: str,
    payload: RolePermissionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission("consent.override"))
):
    """Grant or update permissions for a role (Super Admin capability)."""
    seed_default_permissions(db)
    
    # Delete existing role permissions for this role
    db.query(models.RolePermission).filter(models.RolePermission.role == role).delete()
    
    # Add new permission mappings
    for perm_id in payload.permission_ids:
        perm = db.query(models.Permission).filter(models.Permission.id == perm_id).first()
        if perm:
            db.add(models.RolePermission(role=role, permission_id=perm.id))
            
    db.commit()
    
    updated_perms = db.query(models.RolePermission).filter(models.RolePermission.role == role).all()
    return {
        "role": role,
        "assigned_permissions": [rp.permission.name for rp in updated_perms if rp.permission]
    }
