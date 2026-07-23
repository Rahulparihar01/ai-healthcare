from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
import sys
import os

from database import engine
import models
from routers import hospital, doctor, facilities, patient, records, departments, knowledge_graph, copilot, alerts, timeline
from routers.identity import authentication, authorization, verification, profile, sessions, devices, recovery, audit

# Alembic will handle database schema creation
# models.Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="HealthID AI Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers
# Include Identity Service routers
app.include_router(authentication.router)
app.include_router(authorization.router)
app.include_router(verification.router)
app.include_router(profile.router)
app.include_router(sessions.router)
app.include_router(devices.router)
app.include_router(recovery.router)
app.include_router(audit.router)
app.include_router(hospital.router)
app.include_router(doctor.router)
app.include_router(facilities.router)
app.include_router(departments.router)
app.include_router(patient.router)
app.include_router(records.router)
app.include_router(knowledge_graph.router)
app.include_router(copilot.router)
app.include_router(alerts.router)
app.include_router(timeline.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to HealthID AI API. The platform is secure and functional."}

# Mount static files
app.mount("/public", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "public")), name="public")
