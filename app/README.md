# 🏥 HealthID AI — Backend API Documentation

The **HealthID AI Backend** is an enterprise-grade, multi-tenant FastAPI application engineered for AI-assisted clinical record keeping, predictive analytics, e-prescriptions, automated billing, and secure health data management.

---

## 🚀 Key Technical Features

### 1. Multi-Tenant Architecture & Granular RBAC
- **Role-Based Access Control**: Enforces strict permissions across 10 roles (`Super Admin`, `Hospital Admin`, `Doctor`, `Nurse`, `Lab Technician`, `Pharmacist`, `Receptionist`, `Patient`, `Family Member`, `Emergency Doctor`).
- **Audit Logging Middleware**: Captures every PHI access and data mutation into `/audit/logs` with user ID, IP address, action, and timestamp.

### 2. AI Clinical Intelligence Pipeline
- **Medical Entity Extraction & ICD-10 Auto-Coding**: Automatically parses uploaded lab reports/PDFs to extract conditions, medications, and ICD-10 codes.
- **Copilot Safety Engine**: Scans e-prescriptions against patient allergies and chronic conditions to raise high-priority interaction alerts.
- **RAG & Semantic Search**: Vector embeddings (`pgvector`) enable natural language clinical history search and timeline summarization.

### 3. High-Performance Infrastructure
- **Redis Response Caching (`app/cache.py`)**: Sub-millisecond response caching for repeat AI timeline summaries with automatic in-memory dictionary fallback.
- **Database Indexing**: Composite SQLAlchemy indexes on high-throughput queries (`TimelineEvent`, `Appointment`, `Invoice`, `AuditLog`).
- **Health & Readiness Monitoring**: `/healthz` (liveness) and `/readyz` (readiness) probes for Docker/Kubernetes deployment.

### 4. Storage & Export Services
- **Cloud Object Storage Adapter (`app/storage.py`)**: Unified interface supporting local disk storage for development and AWS S3 (`s3://`) with presigned URL generation for production.
- **File Security Validation**: Enforces 10MB file size limits and magic bytes header checking (`%PDF`, JPEG `\xff\xd8`, PNG `\x89PNG`).
- **Printable PDF Generator (`app/pdf_generator.py`)**: Generates official e-prescriptions and billing receipts with digital verification signatures.
- **API Versioning**: All core routes are accessible via versioned `/api/v1/` prefixes.

---

## 🛠️ Project Structure

```
app/
├── ai_pipeline/          # OCR, LLM Extractor, Copilot Safety Engine & Embeddings
├── routers/              # Modular API Endpoints
│   ├── identity/         # Auth, Sessions, Devices, Verification, Recovery
│   ├── appointments.py   # Scheduling & Queue Management
│   ├── billing.py        # Invoices, Payments, PDF Exports
│   ├── copilot.py        # Safety Alerts & Interaction Checks
│   ├── doctor.py         # Onboarding & Practitioner Management
│   ├── labs.py           # Lab Orders & Test Result Processing
│   ├── patient.py        # Patient Profiles & HealthID Lookup
│   ├── records.py        # Encounters, Diagnoses, Prescriptions & Uploads
│   ├── sse.py            # Real-Time Task Progress Events
│   └── timeline.py       # Patient Encounters & Cached AI Summaries
├── audit_middleware.py   # Global PHI Audit Logging
├── auth.py               # JWT Tokens & Tenant Scoping
├── cache.py              # Redis Caching Layer with In-Memory Fallback
├── celery_app.py         # Celery Worker for Background AI Processing
├── database.py           # SQLAlchemy Engine & Session Local
├── main.py               # FastAPI App Initialization & Router Mounting
├── models.py             # SQLAlchemy Database Models & Indexes
├── pdf_generator.py      # Report PDF Generator (Receipts & Prescriptions)
├── storage.py            # Local & S3 Storage Adapter
└── tests/                # Automated Pytest Suite (49/49 Passing)
```

---

## ⚙️ Setup & Installation

### 1. Environment Setup
Ensure Python 3.10+ is installed:
```bash
cd app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Running Environment Variables
Set the following environment variables (or configure in `.env`):
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/healthid"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="your_super_secret_jwt_key"
export STORAGE_MODE="local" # "local" or "s3"
```

### 3. Starting the Backend Server
```bash
PYTHONPATH=. uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Running Celery Worker (Background AI Jobs)
```bash
PYTHONPATH=. celery -A celery_app.celery_app worker --loglevel=info
```

---

## 🧪 Running Unit Tests

Run the complete test suite:
```bash
PYTHONPATH=app pytest app/tests/
```

- **Total Test Cases**: 49 tests
- **Coverage**: Identity, Appointments, Billing, Copilot Safety, Health Probes, Redis Caching, PDF Export, and S3 Storage.

---

## 📌 API Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/healthz` \| `/api/v1/healthz` | Server Liveness Check |
| `GET` | `/readyz` \| `/api/v1/readyz` | Database & Cache Readiness Check |
| `POST` | `/api/v1/identity/authentication/login` | User Login & JWT Generation |
| `POST` | `/api/v1/records/create` | Create Encounters, Diagnoses & Prescriptions |
| `POST` | `/api/v1/records/upload` | Upload & Queue Medical Documents (PDF/JPG/PNG) |
| `GET` | `/api/v1/timeline/{health_id}/summary` | Retrieve Cached AI Patient Summary |
| `GET` | `/api/v1/billing/invoices/{id}/pdf` | Download Official Payment Receipt PDF |
| `GET` | `/api/v1/sse/task-status/{task_id}` | Real-Time SSE Stream for AI OCR Progress |
