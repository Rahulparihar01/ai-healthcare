# HealthID AI — Technical Architecture & Engineering Overview
### System Design · AI Pipeline · Technology Stack · Skills Demonstrated

---

## Table of Contents

1. [Overview](#1-overview)
2. [Project Structure](#2-project-structure)
3. [Setup & Installation](#3-setup--installation)
4. [System Architecture](#4-system-architecture)
5. [The AI Extraction Pipeline in Detail](#5-the-ai-extraction-pipeline-in-detail)
6. [Technology Stack](#6-technology-stack)
7. [Security, Privacy & Compliance](#7-security-privacy--compliance)
8. [Skills Demonstrated](#8-skills-demonstrated)

---

## 1. Overview

HealthID AI is an advanced, multi-tenant, AI-powered medical record and identity platform. It provides seamless patient identity generation (ABHA-style Health IDs with QR codes), comprehensive role-based access control with organizational isolation, and a fault-tolerant AI processing pipeline that automatically structures clinical data from uploaded medical documents.

## 2. Project Structure

The codebase is a monorepo containing the FastAPI backend and the React frontend:

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

## 3. Setup & Installation

### 3.1 Prerequisites
- Node.js (v18+)
- Python (3.9+)
- Docker & Docker Compose (required for PostgreSQL and Redis)

### 3.2 Environment Variables

An `.env` file at the project root must supply:
- `OPENAI_API_KEY` — enables the AI extraction pipeline.
- `DATABASE_URL` — defaults to `postgresql://postgres:postgres@localhost:5432/healthid`
- `CELERY_BROKER_URL` — defaults to `redis://localhost:6379/0`

### 3.3 Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 3.4 Running the Application

Start infrastructure services first, then launch the unified dev script:

```bash
docker-compose up -d
./dev.sh
```

This launches the FastAPI server on `http://localhost:8000` (Swagger docs at `/docs`), the React frontend on `http://localhost:5173`, and the Celery background worker for asynchronous AI document extraction.

## 4. System Architecture

### 4.1 Request & Processing Flow

A document upload moves through the following stages:

| Step | Component | Action |
|---|---|---|
| 1 | React Frontend | User (doctor/patient) uploads a document via the UI |
| 2 | FastAPI Server | Receives the API request |
| 3 | Local Storage + PostgreSQL | Saves the file and creates a record |
| 4 | Redis Broker | Task is enqueued for background processing |
| 5 | Celery Worker | Consumes the task asynchronously |
| 6 | OCR Service (PyMuPDF / Tesseract) | Extracts raw text from the document |
| 7 | Document Classifier (GPT-4o-mini) | Classifies document type from raw text |
| 8 | Specialized Extractor (GPT-4o) | Extracts structured JSON (schema v1.0) for that document type |
| 9 | Clinical Validator | Validates extracted data; routes to Completed or Needs Review |
| 10 | PostgreSQL | Final structured record is persisted |

### 4.2 Key Architectural Principles

- **Multi-Tenant Architecture** — strict organizational isolation. Super Admins manage multiple hospitals; Hospital Admins manage their internal staff and patients; every clinical record is strictly bound to its owning `hospital_id`.
- **Role-Based Access Control (RBAC)** — backend APIs verify JWT claims to authorize Super Admin, Hospital Admin, Doctor, Receptionist, and Lab Technician actions.
- **Asynchronous AI Pipeline (Celery + Redis)** — document uploads are processed in the background without blocking API responses; the frontend polls and renders live, granular processing statuses.
- **Two-Step Specialized Extraction** — fast OCR and classification, followed by a specialized, dynamically-prompted extraction pass (see Section 5).
- **Deep Clinical Validation** — protects the database from LLM hallucination.
- **Premium React UI** — glassmorphism design theme with a rich chronological timeline engine.
- **QR Code Identities** — automatically generated, scannable QR codes representing 14-digit Patient Health IDs.

## 5. The AI Extraction Pipeline in Detail

### 5.1 Step One — Fast OCR & Classification
- Raw text extraction via PyMuPDF / pytesseract.
- `gpt-4o-mini` classifies the document type from over 13 supported variants (e.g., CBC, Discharge Summary, MRI).

### 5.2 Step Two — Specialized Extraction
- `gpt-4o` runs with a dynamically injected prompt targeting the specific document type identified in Step One.
- Extracts structured, versioned JSON (schema v1.0) tailored to that document type.

### 5.3 Deep Clinical Validation
- Verifies required fields are present.
- Parses and normalizes numeric lab values and units (e.g., mapping `mg/dl` to `mg/dL`).
- Enforces consistent date formats.
- Requires an 80% confidence threshold before auto-acceptance.
- Failed documents are flagged in the UI for Manual Review rather than silently accepted.

## 6. Technology Stack

| Layer | Technologies |
|---|---|
| Backend Framework | FastAPI (Python), Node.js microservices where applicable |
| ORM / Data Access | SQLAlchemy |
| Relational Database | PostgreSQL (patient metadata, structured records) |
| Document Store | MongoDB (medical records) |
| Cache / Broker | Redis |
| Background Processing | Celery workers |
| AI / GenAI | GPT-4o / GPT-4o-mini, medical RAG pipeline, prompt engineering |
| Vector Database | Pinecone / Weaviate / Qdrant (semantic embeddings) |
| OCR | PyMuPDF, Tesseract (incl. handwritten text recognition) |
| Auth & Security | JWT, OAuth2, RBAC, encryption at rest & in transit |
| Object Storage | AWS S3 / Azure Blob Storage |
| Frontend (Web) | React.js, TailwindCSS, Vite |
| Frontend (Mobile) | React Native / Flutter (offline-first for rural use) |
| Healthcare Standards | ABDM / ABHA APIs, FHIR, HIP registration workflow |
| Deployment | Docker, Kubernetes, CI/CD pipelines |

## 7. Security, Privacy & Compliance

- JWT authentication and OAuth2 for identity and session management.
- Role-Based Access Control across Super Admin, Hospital Admin, Doctor, Receptionist, and Lab Technician roles.
- Strict multi-tenant data isolation — every record bound to its owning hospital/organization.
- Consent-based access control for patient records, with temporary doctor access grants.
- Encryption at rest and in transit.
- Secure file management and full audit logging.
- Alignment with ABDM / ABHA / FHIR standards for national interoperability.

## 8. Skills Demonstrated

### 8.1 System Architecture
- Large-scale healthcare system design.
- Multi-tenant SaaS architecture.
- Microservices and event-driven system design.
- REST API design and database architecture.
- Scalable backend development.

### 8.2 Backend Engineering
- FastAPI development, SQLAlchemy ORM.
- PostgreSQL, MongoDB, Redis.
- Celery background workers.
- API security, Docker & Kubernetes, CI/CD pipelines.

### 8.3 Authentication & Security
- JWT authentication, OAuth2, RBAC.
- Multi-tenant data isolation, consent-based access control.
- Encryption at rest & in transit, secure file management, audit logging.

### 8.4 AI & Generative AI
- LLM integration (GPT-4o / GPT-4o-mini), medical AI workflows.
- AI report summarization, comparison, and clinical reasoning.
- Retrieval-Augmented Generation (RAG), prompt engineering.
- Medical knowledge extraction and entity recognition.
- Structured JSON generation, AI confidence validation, hallucination prevention, clinical data validation.

### 8.5 OCR & Document Intelligence
- OCR processing, handwritten text recognition, PDF processing.
- Medical document classification and clinical document parsing.
- Structured medical data extraction, automatic report categorization.

### 8.6 Clinical Intelligence
- Disease detection & tracking, disease timeline generation.
- Prescription analysis, medication intelligence, drug interaction and duplicate detection.
- Allergy detection, laboratory trend analysis, radiology report analysis.
- Clinical alert generation; patient health scoring and predictive analytics (future).

### 8.7 Search & Knowledge Management
- Semantic search, vector embeddings, vector database integration.
- Patient knowledge graph, medical timeline engine.
- Context-aware information retrieval.

### 8.8 Healthcare Standards & Integration
- ABDM / ABHA integration, FHIR standards, HIP registration workflow.
- Healthcare interoperability and digital health infrastructure.

### 8.9 Frontend Development
- React.js, React Native / Flutter, TailwindCSS.
- Responsive, mobile-first, offline-first design.
- Real-time timeline UI and clinical dashboard development.

### 8.10 DevOps & Infrastructure
- Docker, Kubernetes, Redis, Celery.
- Object storage (AWS S3 / Azure Blob), background job processing.
- Monitoring, logging, and performance optimization.

### 8.11 Product & Business
- Healthcare product strategy and AI product development.
- Enterprise SaaS and rural healthcare digitization.
- Healthcare workflow automation, market validation, product positioning.
- Government digital health ecosystem integration.
