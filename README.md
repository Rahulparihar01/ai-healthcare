# 🏥 HealthID AI — Enterprise Clinical Record & Copilot Platform

An advanced, multi-tenant AI-powered medical record, clinical intelligence, and patient identity platform. HealthID AI provides secure patient identity management with QR codes, multi-tenant organizational scoping with granular RBAC, fault-tolerant background AI document extraction, sub-second Redis response caching, hands-free voice dictation, multi-language i18n (English & Hindi), and PWA offline request queueing.

---

## 📁 Project Architecture & Monorepo Structure

```
ai-healthcare/
├── app/                  # FastAPI Backend Engine (Python 3.10+)
│   ├── ai_pipeline/      # AI Extractor, Copilot Safety Engine & Embeddings
│   ├── routers/          # Modular API Endpoints (/api/v1/)
│   ├── audit_middleware.py # Global PHI Audit Logging
│   ├── cache.py          # Redis AI Response Caching Layer
│   ├── models.py         # SQLAlchemy Database Models & Composite Indexes
│   ├── pdf_generator.py  # E-Prescription & Receipt PDF Generator
│   ├── storage.py        # AWS S3 & Local Storage Adapter
│   ├── tests/            # Pytest Suite (49/49 Passing)
│   └── README.md         # Detailed Backend Documentation
├── frontend/             # React (Vite) Glassmorphic PWA
│   ├── src/
│   │   ├── components/   # Role-Based Dashboards & UI
│   │   ├── context/      # Auth & Language (i18n) Providers
│   │   └── hooks/        # Voice Input (Web Speech API) & State Hooks
│   └── README.md         # Detailed Frontend Documentation
├── docs/                 # Product Specifications & CIP Sprint Tracking
├── docker-compose.yml    # Infrastructure (PostgreSQL & Redis)
├── dev.sh                # Unified Local Startup Script
└── HealthID_AI_PRD.md    # Product Requirements Document
```

> 📖 **Sub-Directory Documentation**:
> - For deep-dive backend configuration and endpoints, see [app/README.md](app/README.md).
> - For frontend component hierarchy and PWA offline sync, see [frontend/README.md](frontend/README.md).

---

## 🚀 Core Features & Production Capabilities

### 1. 🛡️ Security, Governance & Auditability
- **Multi-Tenant Scoping**: Strict tenant isolation across Organizations, Hospitals, and Clinics.
- **Granular RBAC**: Role-based access control supporting 10 distinct roles (`Super Admin`, `Hospital Admin`, `Doctor`, `Nurse`, `Lab Technician`, `Pharmacist`, `Receptionist`, `Patient`, `Family Member`, `Emergency Doctor`).
- **Global PHI Audit Logging**: Automatic request interception logging every data access and mutation into `/audit/logs` with user ID, IP address, and timestamp.
- **File Upload Security**: Enforces a 10MB file limit, MIME validation, and magic byte header verification (`%PDF`, JPEG `\xff\xd8`, PNG `\x89PNG`).

### 2. ⚡ High-Performance Core Engine
- **Database Composite Indexing**: Optimized compound indexes on `TimelineEvent`, `Appointment`, `Invoice`, and `AuditLog` tables.
- **Redis Response Caching (`app/cache.py`)**: Sub-second cached responses for repeat patient AI summaries with automatic in-memory fallback.
- **Observability & Probes**: `/healthz` (liveness) and `/readyz` (readiness) probes for Kubernetes & container health checks.
- **API Versioning**: Standardized `/api/v1/` prefixing across all router endpoints.

### 3. 🤖 AI Clinical Intelligence & Copilot
- **Automated Entity Extraction**: Extracts diagnoses, medications, dosages, and ICD-10 codes from uploaded lab reports and medical PDFs.
- **Copilot Safety Engine**: Scans active prescriptions against known patient allergies and medical history to prevent adverse drug interactions.
- **Async Task Pipeline**: Background Celery worker processes long-running OCR tasks with Server-Sent Events (`/api/v1/sse/task-status/{id}`) streaming live status updates to the UI.

### 4. 🌐 Practitioner Experience & PWA Capabilities
- **Voice Dictation (`useVoiceInput.js`)**: Hands-free voice-to-text dictation powered by the Web Speech API.
- **Multi-Language Support (i18n)**: Instant UI toggle between **English** and **Hindi (`hi`)**.
- **Offline Request Queueing (`OfflineIndicator.jsx`)**: Offline-first operation that queues registration and record creations locally, automatically replaying them when network restores.
- **Printable PDF Export (`pdf_generator.py`)**: Downloadable e-prescriptions and payment receipts complete with digital verification signatures.

---

## ⚡ Quick Start Guide

### Prerequisites
- **Node.js**: v18+
- **Python**: v3.10+
- **Docker & Docker Compose**: (for PostgreSQL & Redis)

### 1. Environment Configuration
Ensure `.env` exists in the project root:
```env
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/healthid
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your_super_secret_jwt_key
STORAGE_MODE=local
```

### 2. Launch Infrastructure Services
```bash
docker-compose up -d
```

### 3. Run Unified Startup Script
Start the FastAPI server, Celery worker, and Vite React frontend simultaneously:
```bash
./dev.sh
```

- **React Frontend**: `http://localhost:5173`
- **FastAPI API & Swagger Docs**: `http://localhost:8000/docs`
- **Health / Readiness Probes**: `http://localhost:8000/healthz` \| `http://localhost:8000/readyz`

---

## 🧪 Automated Testing

Run the backend test suite:
```bash
PYTHONPATH=app pytest app/tests/
```
- **Test Results**: `49 passed` in 7.8s (100% passing).
