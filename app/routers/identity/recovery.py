from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user
import secrets
import hashlib
from datetime import datetime

router = APIRouter(prefix="/identity/recovery", tags=["Identity - Account Recovery"])

@router.post("/setup-backup-codes")
def setup_backup_codes(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Delete old unused codes
    db.query(models.RecoveryCode).filter(
        models.RecoveryCode.user_id == current_user.id,
        models.RecoveryCode.is_used == False
    ).delete()
    
    codes = []
    for _ in range(10):
        code = secrets.token_hex(4) # 8 character hex code
        codes.append(code)
        
        # Hash code for storage
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        db_code = models.RecoveryCode(
            user_id=current_user.id,
            code_hash=code_hash
        )
        db.add(db_code)
        
    db.commit()
    
    # Audit log
    audit_log = models.AuditLog(
        user_id=current_user.id,
        action="SETUP_BACKUP_CODES",
        status="SUCCESS"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Backup codes generated. Store them safely.", "codes": codes}

# We would also have an endpoint to use backup codes for login here.
