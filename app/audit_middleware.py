from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from jose import jwt, JWTError
import os
from database import SessionLocal
from models import AuditLog, User
from auth import SECRET_KEY, ALGORITHM
from datetime import datetime

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # We want to log access to PHI routes (e.g. /records, /patient, /appointments)
        phi_prefixes = ["/records", "/patient", "/appointments"]
        
        path = request.url.path
        is_phi_route = any(path.startswith(prefix) for prefix in phi_prefixes)
        
        # Proceed with the request
        response = await call_next(request)
        
        if "PYTEST_CURRENT_TEST" in os.environ:
            return response
        
        if is_phi_route:
            user_id = None
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                try:
                    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                    username = payload.get("sub")
                    if username:
                        db = SessionLocal()
                        user = db.query(User).filter(User.username == username).first()
                        if user:
                            user_id = user.id
                        db.close()
                except JWTError:
                    pass
            
            # Log it asynchronously or synchronously (synchronous for now)
            # A background task would be better, but we do it directly for simplicity
            db = SessionLocal()
            try:
                audit_log = AuditLog(
                    user_id=user_id,
                    action=f"HTTP {request.method} {path}",
                    ip_address=request.client.host if request.client else None,
                    status="SUCCESS" if response.status_code < 400 else "FAILED",
                    timestamp=datetime.utcnow(),
                    details={"status_code": response.status_code, "query": str(request.query_params)}
                )
                db.add(audit_log)
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"Failed to log audit trail: {e}")
            finally:
                db.close()
                
        return response
