from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
import sys
import os

from database import engine
import models
from routers import auth, hospital, doctor, facilities, patient, records

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
app.include_router(auth.router)
app.include_router(hospital.router)
app.include_router(doctor.router)
app.include_router(facilities.router)
app.include_router(patient.router)
app.include_router(records.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to HealthID AI API. The platform is secure and functional."}

# Mount static files
app.mount("/public", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "public")), name="public")
