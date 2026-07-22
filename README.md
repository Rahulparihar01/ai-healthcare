# HealthID AI - Medical Record Platform

An advanced, multi-tenant AI-powered medical record and identity platform. It provides seamless patient identity generation (ABHA-style Health IDs with QR codes), comprehensive role-based access control with organizational isolation, and a highly sophisticated, fault-tolerant AI processing pipeline to automatically structure clinical data from medical documents.

## Project Structure

This is a Monorepo containing the FastAPI Backend and the React Frontend.

```
ai-healthcare/
├── backend/               # FastAPI Backend Application
│   ├── ai_pipeline/       # Two-Step AI Document Extraction & Validation
│   ├── public/            # Stores generated QR codes and uploaded Reports
│   ├── routers/           # API Endpoints (Auth, Patients, Records, Orgs)
│   ├── main.py            # FastAPI App entrypoint
│   ├── models.py          # SQLAlchemy Database Schemas
│   └── celery_app.py      # Celery Task Queue configuration
├── frontend/              # React (Vite) Frontend Application
│   ├── src/
│   │   ├── components/    # UI Components (Timeline, Dashboard, etc.)
│   │   ├── App.jsx        # Routing layer
│   │   └── index.css      # Premium Glassmorphism Design System
├── docker-compose.yml     # Infrastructure (PostgreSQL & Redis)
├── dev.sh                 # Unified Startup Script
└── plan.md                # Original Project Specifications
```

## Setup & Installation

### Prerequisites
*   Node.js (v18+)
*   Python (3.9+)
*   Docker & Docker Compose (required for PostgreSQL and Redis)

### 1. Environment Variables
Ensure you have the `.env` file at the root of the project. You must supply:
* `OPENAI_API_KEY` to enable the AI extraction pipeline.
* `DATABASE_URL` (Defaults to `postgresql://postgres:postgres@localhost:5432/healthid`)
* `CELERY_BROKER_URL` (Defaults to `redis://localhost:6379/0`)

### 2. Install Dependencies
**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

## Running the Application

For local development, start the required infrastructure services first:

```bash
docker-compose up -d
```

Then, use the unified startup script from the root directory:

```bash
./dev.sh
```

This script automatically launches:
*   The **FastAPI Server** on `http://localhost:8000` (Access the Swagger Docs at `http://localhost:8000/docs`)
*   The **React Frontend** on `http://localhost:5173`
*   The **Celery Background Worker** to process asynchronous AI document extraction.

## Core Features & Architecture

### System Architecture
```mermaid
graph TD
    User([Doctor / Patient]) -->|Uploads Document| UI[React Frontend]
    UI -->|API Request| API[FastAPI Server]
    
    API -->|Save File| FileSystem[(Local Storage)]
    API -->|Create Record| DB[(PostgreSQL)]
    API -->|Enqueue Task| Redis[(Redis Broker)]
    
    Redis -->|Consume Task| Worker[Celery Worker]
    
    subgraph "AI Processing Pipeline"
        Worker --> OCR[OCR Service <br> PyMuPDF / Tesseract]
        OCR -->|Raw Text| Classifier[Document Classifier <br> GPT-4o-mini]
        Classifier -->|Document Type| Extractor[Specialized Extractor <br> GPT-4o]
        Extractor -->|JSON Schema v1.0| Validator[Clinical Validator]
        Validator -->|Valid| Complete((Completed))
        Validator -->|Invalid| Review((Needs Review))
    end
    
    Complete --> DB
    Review --> DB
```

*   **Multi-Tenant Architecture**: Strict organizational isolation. Super Admins manage multiple Hospitals. Hospital Admins manage their internal staff and patients. Every clinical record is strictly bound to its owning `hospital_id`.
*   **Role-Based Access Control (RBAC)**: Backend APIs actively verify JWT claims to authorize `Super Admin`, `Hospital Admin`, `Doctor`, `Receptionist`, and `Lab Technician` actions.
*   **Asynchronous AI Pipeline (Celery + Redis)**: Document uploads are processed instantly in the background without blocking API responses. The frontend actively polls and renders live, granular processing statuses.
*   **Two-Step Specialized Extraction**:
    1.  **Fast OCR & Classification**: Rips raw text via PyMuPDF/pytesseract, then uses `gpt-4o-mini` to classify the document type from over 13 variants (e.g., CBC, Discharge Summary, MRI).
    2.  **Specialized Extraction**: Uses `gpt-4o` with a dynamically injected prompt targeting that specific document type to extract structured, versioned JSON.
*   **Deep Clinical Validation**: Actively protects the database from LLM hallucinations by verifying required fields, parsing and normalizing numeric lab values and units (e.g., mapping `mg/dl` to `mg/dL`), enforcing date formats, and requiring an 80% confidence threshold. Failed documents are actively flagged in the UI for **Manual Review**.
*   **Premium React UI**: Designed with a sophisticated glassmorphism theme, smooth animations, and a rich chronological timeline engine.
*   **QR Code Identities**: Automatically generates scannable QR codes representing 14-digit Patient Health IDs.
