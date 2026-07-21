# HealthID AI - Medical Record Platform

An advanced, AI-powered medical record and identity platform. It provides seamless patient identity generation (ABHA-style Health IDs with QR codes), comprehensive role-based access control, and an integrated OpenAI Vision pipeline to automatically extract and structure data from uploaded medical documents (PDFs, X-Rays, MRIs).

## Project Structure

This is a Monorepo containing both the FastAPI Backend and the React Frontend.

```
ai-healthcare/
├── backend/               # FastAPI Backend Application
│   ├── ai_pipeline/       # GPT-4o Vision Document Extraction logic
│   ├── public/            # Stores generated QR codes and uploaded Reports
│   ├── routers/           # API Endpoints (Auth, Patients, Records, Master Data)
│   ├── main.py            # FastAPI App entrypoint
│   └── models.py          # SQLAlchemy Database Schemas
├── frontend/              # React (Vite) Frontend Application
│   ├── src/
│   │   ├── components/    # UI Components (Doctor Dashboard, Login, etc.)
│   │   ├── context/       # Global State (AuthContext)
│   │   ├── App.jsx        # Routing layer
│   │   └── index.css      # Premium Glassmorphism Design System
├── .env                   # Global Environment Variables
├── dev.sh                 # Unified Startup Script
└── plan.md                # Original Project Specifications
```

## Setup & Installation

### Prerequisites
*   Node.js (v18+)
*   Python (3.9+)

### 1. Environment Variables
Ensure you have the `.env` file at the root of the project. You must supply your `OPENAI_API_KEY` to enable the document extraction pipeline.

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

For development, use the unified startup script from the root directory:

```bash
./dev.sh
```

This script automatically launches:
*   The **FastAPI Server** on `http://localhost:8000` (Access the Swagger Docs at `http://localhost:8000/docs`)
*   The **React Frontend** on `http://localhost:5173`

## Features & Architecture

*   **Premium React UI**: Uses a sophisticated dark-mode glassmorphism theme, protected by role-based routing (React Router + Context API).
*   **Role-Based Access Control (RBAC)**: Backend APIs strictly check if the user is a `Super Admin`, `Hospital Admin`, `Doctor`, `Receptionist`, or `Lab Technician`.
*   **Medical Timeline**: A unified feed merging manual doctor prescriptions with AI-processed lab reports.
*   **OpenAI Vision Pipeline**: Upload a blood report PDF; the backend converts it to an image, sends it to `gpt-4o`, extracts the key metrics, categorizes it, and saves it to the SQLite database.
*   **QR Code Identities**: Automatically generates scannable QR codes representing 14-digit Patient Health IDs.
