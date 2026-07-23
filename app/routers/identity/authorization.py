from fastapi import APIRouter, Depends
from auth import RequireRole
import models

router = APIRouter(prefix="/identity/authorization", tags=["Identity - Authorization"])

# In a real application, you might manage roles, permissions, scopes dynamically here.
# For now, we export the dependencies used across the app to enforce RBAC.

@router.get("/permissions")
def get_my_permissions():
    """Endpoint to list available permissions or scopes."""
    return {
        "roles": [role.value for role in models.RoleEnum]
    }
