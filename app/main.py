from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
import sys
import os

from database import engine
import models
from routers import hospital, doctor, facilities, patient, records, departments, knowledge_graph, copilot, alerts, timeline, search, analytics, predictions, appointments, labs, billing, sse, audit as top_level_audit
from routers.identity import authentication, authorization, verification, profile, sessions, devices, recovery, audit
from audit_middleware import AuditMiddleware

# Alembic will handle database schema creation
# models.Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="HealthID AI Backend API")

app.add_middleware(AuditMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import APIRouter

v1_router = APIRouter(prefix="/api/v1")

for r in [
    authentication.router, authorization.router, verification.router, profile.router,
    sessions.router, devices.router, recovery.router, audit.router, top_level_audit.router,
    hospital.router, doctor.router, facilities.router, departments.router, patient.router,
    records.router, appointments.router, labs.router, billing.router, knowledge_graph.router,
    copilot.router, alerts.router, timeline.router, search.router, analytics.router, predictions.router,
    sse.router
]:
    app.include_router(r)
    v1_router.include_router(r)

@app.get("/healthz")
@v1_router.get("/healthz")
def health_check():
    """Liveness probe to check if the server is running."""
    return {"status": "ok", "service": "healthid-ai-backend"}

@app.get("/readyz")
@v1_router.get("/readyz")
def readiness_check():
    """Readiness probe to verify database and cache connectivity."""
    db_status = "healthy"
    try:
        from database import SessionLocal
        db = SessionLocal()
        db.execute(models.User.__table__.select().limit(1))
        db.close()
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    cache_status = "healthy"
    try:
        from cache import get_redis_client
        client = get_redis_client()
        if client:
            client.ping()
        else:
            cache_status = "in-memory-fallback"
    except Exception as e:
        cache_status = f"unhealthy: {str(e)}"

    is_ready = db_status == "healthy"
    return {
        "ready": is_ready,
        "database": db_status,
        "cache": cache_status
    }

app.include_router(v1_router)

# Static files are no longer mounted publicly for security reasons.
# Use authenticated endpoints to access resources.
