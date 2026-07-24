# Product Requirements Document (PRD)

## 1. Product Overview

### 1.1 Product Name
**HealthID AI - Medical Record Platform**

### 1.2 Vision & Purpose
HealthID AI is an advanced, multi-tenant AI-powered medical record and identity platform designed to digitize the entire patient journey and replace manual, paper-based healthcare handoffs. The product provides seamless patient identity generation (ABHA-style Health IDs with QR codes), comprehensive role-based access control (RBAC) with strict organizational isolation, and a highly sophisticated, fault-tolerant AI processing pipeline to automatically extract and structure clinical data from raw medical documents.

### 1.3 Target Audience
- **Patients**: Seeking to manage their health records, share digital medical histories seamlessly with doctors, and eliminate the need to carry physical files.
- **Doctors**: Needing quick, structured access to patient histories, diagnoses, lab results, and an easy way to write digital prescriptions or order labs.
- **Hospital Administrators & Super Admins**: Managing hospital branches, departments, and staff permissions, while requiring oversight through audit logs and dashboard analytics.
- **Receptionists**: Facilitating patient registration, identity generation (QR codes), and appointment scheduling.
- **Lab Technicians & Pharmacists**: Receiving digital lab/pharmacy orders, uploading test results, and closing the paperless loop for secondary healthcare actions.

## 2. Architecture & Tech Stack

### 2.1 Technology Stack
- **Backend**: Python (FastAPI) for high-performance REST APIs.
- **Frontend**: React (Vite) with a premium glassmorphism design system.
- **Database**: PostgreSQL (Relational schema with pgvector for embeddings).
- **Caching & Message Broker**: Redis.
- **Background Processing**: Celery Workers for asynchronous AI processing.
- **AI/ML Layer**: PyMuPDF / Tesseract for OCR, OpenAI GPT-4o-mini for document classification, GPT-4o for specialized JSON extraction.

### 2.2 Core Architectural Principles
- **Multi-Tenancy**: Built for organizations and hospitals; data is strictly bound to the `hospital_id`.
- **Fault Tolerance**: Background tasks are processed asynchronously without blocking user UI.
- **Security & Privacy**: RBAC-driven APIs actively verify JWT claims to authorize specific user roles. Audit trails log every PHI-related action.

## 3. Core Features & Requirements

### 3.1 Patient Identity Management
- **HealthID Generation**: Automatically generate 14-digit, unique Patient Health IDs.
- **QR Codes**: Generate scannable QR codes representing the patient's HealthID for rapid access at the reception or emergency scenarios.
- **Profile Data**: Store comprehensive demographic information, emergency contacts, known allergies, chronic diseases, and past medical history.

### 3.2 Role-Based Access Control (RBAC)
- Support for roles: Super Admin, Hospital Admin, Doctor, Lab Technician, Pharmacist, Receptionist, Nurse, Patient, and Emergency Doctor.
- Fine-grained permission model (`permissions` and `role_permissions` mapping).
- Strict endpoint protection and data filtering based on the currently authenticated user's role and associated hospital/department.
- **Consent & Emergency Access**: Time-bound or reason-bound emergency access logs to bypass strict privacy walls when life-threatening situations occur.

### 3.3 AI-Powered Document Extraction (Asynchronous Pipeline)
- **Document Ingestion**: Allow users to upload physical reports (images, PDFs).
- **OCR & Classification**: Extract raw text and automatically classify the document type from over 13 variants (e.g., CBC, Discharge Summary, MRI).
- **Intelligent Structuring**: Utilize GPT-4o to parse medical metrics, mapping varied units (e.g., `mg/dl` to `mg/dL`) into a standardized JSON format.
- **Clinical Validation**: Guard against AI hallucinations with an 80% confidence threshold and strict schema checks.
- **Manual Review Workflow**: Flag invalid or low-confidence AI parses for manual doctor/admin review in the UI.

### 3.4 Clinical Workflows & Management
- **Appointments & Visits**: Manage patient scheduling, check-ins, and visit lifecycle tracking.
- **Diagnoses & Prescriptions**: Allow doctors to record ICD-10 diagnoses and issue structured e-prescriptions natively.
- **Lab & Radiology Orders**: Close the loop between doctors and diagnostic departments. Allow Lab Techs to upload structured test results that automatically attach to the patient's history.
- **Smart Timeline**: A chronological timeline view in the frontend that aggregates visits, prescriptions, labs, and uploaded documents in one easily readable flow.
- **Clinical Alerts**: Automated system alerts for severe allergies, drug interactions, or critical lab results.

### 3.5 Security, Auditing & Compliance
- **Audit Trails**: Global middleware to log every interaction with Protected Health Information (PHI), detailing user, action, IP, and timestamp.
- **Authentication**: JWT-based auth, Refresh Tokens, and robust session management.

## 4. User Journeys

### 4.1 New Patient Onboarding & Visit
1. Patient arrives; Receptionist registers the patient on the platform.
2. System generates a unique HealthID and a QR code.
3. Receptionist books an appointment with a specific Doctor.
4. Doctor scans/searches the patient, reviews their timeline (which may include past uploaded paper records newly structured by AI).
5. Doctor records a diagnosis and orders a Lab Test.
6. Lab Technician sees the pending order, conducts the test, and uploads the PDF.
7. AI pipeline parses the Lab Report, structures the biomarkers, and alerts the Doctor.

## 5. Non-Functional Requirements (NFRs)

- **Performance**: Document processing should run in the background; the UI must actively poll or use webhooks to display real-time status.
- **Scalability**: Database queries involving large records must be heavily paginated to prevent memory exhaustion. N+1 queries must be optimized.
- **Availability**: System should support a Progressive Web App (PWA) fallback to allow limited offline interaction during network drops.
- **Compliance**: Adhere strictly to healthcare data standards. Ensure secure file handling (e.g., streaming files through RBAC proxy endpoints rather than static public mounts). No hardcoded secrets in the codebase.

## 6. Future Enhancements & Roadmap
- Integration with external pharmacy networks for direct E-Prescription fulfillment.
- Multi-language support and accessibility enhancements.
- Native mobile applications for iOS and Android platforms.
- Deep analytics dashboards for Hospital Admins to measure wait times and lab turnaround times.
