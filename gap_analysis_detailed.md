# HealthID AI - Workflow & Architecture Gap Analysis

This analysis compares the current HealthID AI implementation against a production-grade, fully paperless healthcare workflow.

## 1. FUNCTIONAL GAPS (by role)

### Patient
*   **Currently Supports**: Profile creation, basic medical history viewing (via timeline), and uploading documents (`app/routers/patient.py`, `frontend/src/components/PatientDashboard.jsx`).
*   **Missing/Incomplete**: 
    *   **Appointment Booking**: Patients cannot book or manage appointments directly.
    *   **Consent Management**: While the `PatientConsent` DB model exists (`models.py`), there is no API or frontend UI for patients to dynamically grant/revoke access to specific doctors.
    *   **Paper Handoffs**: Patients still have to physically walk into the hospital to book an appointment or pay bills (no digital payment integration).

### Doctor
*   **Currently Supports**: Creating visits, diagnoses, and basic prescriptions (`app/routers/records.py`).
*   **Missing/Incomplete**: 
    *   **E-Prescription Standards**: Prescriptions are saved as raw JSON (`records.py:117`). There is no cryptographic signing or integration with an external pharmacy network (e-prescribing).
    *   **Lab Orders**: Doctors cannot digitally order a lab test that routes directly to the lab technician's queue.
    *   **Paper Handoffs**: Because lab ordering isn't integrated, doctors likely have to print a lab slip for the patient to take to the lab.

### Receptionist / Front Desk
*   **Currently Supports**: The frontend `ReceptionistDashboard.jsx` has a mock "Appointments" tab.
*   **Missing/Incomplete**: 
    *   **Scheduling System**: There are no backend APIs for scheduling, calendar management, or slot booking. 
    *   **Billing/Invoicing**: `auth_middleware.py` lists permissions like `"invoice.create"`, but there are no actual billing routers, models, or UI components. 
    *   **Paper Handoffs**: Check-in processes and payments are entirely manual and paper-based.

### Lab Assistant / Technician
*   **Currently Supports**: A backend API for uploading lab results (`POST /records/upload` in `records.py`).
*   **Missing/Incomplete**: 
    *   **Dedicated UI**: There is no `LabTechnicianDashboard.jsx` in the frontend.
    *   **Queue Management**: No system to view pending lab orders from doctors.
    *   **Paper Handoffs**: Technicians must rely on physical paper orders to know what tests to run, then manually match the result PDF to a patient ID.

### Admin / Staff
*   **Currently Supports**: Basic analytics and onboarding of doctors/hospitals (`app/routers/analytics.py`, `app/routers/hospital.py`).
*   **Missing/Incomplete**: 
    *   **Audit Trail Viewing**: `models.py` has an `AuditLog` table, but there is no frontend UI for admins to review who accessed what patient record.
    *   **Staff Roster Management**: No shift scheduling or availability toggles for doctors.

## 2. CROSS-CUTTING GAPS

*   **Notifications**: *Not found in codebase*. Only email OTPs for authentication exist (`app/routers/identity/verification.py`). There are no SMS/email reminders for appointments, lab results, or follow-ups.
*   **Audit Trail**: The `AuditLog` model exists, but there is no middleware automatically logging every PHI read/write event across all endpoints.
*   **Multi-location Support**: The `Hospital` model exists, but APIs like `GET /records/list` do not filter by branch/location.
*   **Offline Handling**: *Not found in codebase*. No Service Workers, `manifest.json`, or local caching strategies in the React Vite app (`vite.config.js` uses basic plugins). 
*   **Reporting & Analytics**: Admin dashboards show basic aggregates, but lack deep operational metrics (e.g., lab turnaround times, doctor utilization rates).
*   **File/Document Handling**: Documents are uploaded as static PDFs/Images to a local folder (`/public/uploads/`). There is no OCR verification step before saving, and no centralized object storage (like AWS S3) configuration.
*   **Multi-language / Accessibility**: *Not found in codebase*. No i18n libraries configured in `package.json`.

## 3. SECURITY & COMPLIANCE GAPS

*   **Access Control Granularity (IDOR)**: As noted previously, endpoints like `GET /records/list` in `records.py` accept any `health_id` without verifying if the requesting doctor/patient has authorized access to that specific ID.
*   **Data at Rest / In Transit**: Uploaded PHI (lab reports) are stored unencrypted in a public static directory (`app/main.py:54`). 
*   **Session Management**: JWTs are used (`app/auth.py`), but there is no server-side token revocation list (blacklist) upon logout. `DELETE /sessions/all` exists but relies on DB sessions rather than invalidating the actual JWT signature.
*   **Consent Management**: No mechanism enforces the `PatientConsent` model before returning data from the database.

## 4. TECHNICAL / ARCHITECTURE GAPS

*   **Scalability Concerns**: 
    *   **Missing Pagination**: The primary timeline endpoint (`GET /records/list` in `records.py:262`) uses `.all()` without `skip`/`limit` parameters. This will crash the browser for patients with extensive medical histories.
*   **Testing Gaps**: 
    *   Backend tests (`app/tests/`) only cover the AI pipeline (e.g., `test_copilot_engine.py`). Zero integration tests exist for the FastAPI routers.
    *   Frontend tests (`frontend/src/tests/components/`) directory is completely empty.
*   **CI/CD**: *Not found in codebase*. No GitHub Actions, GitLab CI, or Docker deployment manifests beyond a basic `docker-compose.yml`.

## 5. PRIORITIZED GAP TABLE

| Gap | Affected Role(s) | Impact | Effort to Fix | Recommended Priority |
|---|---|---|---|---|
| **IDOR & Static PHI Exposure** | All | High | Medium | **P0** |
| **Missing Pagination on Records API** | Patient, Doctor | High | Low | **P0** |
| **No Global Audit Trail Middleware** | Admin, Compliance | High | Medium | **P1** |
| **Missing Scheduling/Appointment APIs** | Patient, Reception | High | High | **P1** |
| **No Backend Integration Tests** | Developers | High | Medium | **P1** |
| **Missing Lab Technician Dashboard** | Lab Assistant | Medium | Medium | **P2** |
| **No Notification System (SMS/Email)** | Patient, Doctor | Medium | Medium | **P2** |
| **Missing E-Prescription Signing** | Doctor, Pharmacy | Medium | High | **P2** |
| **No Offline Mode (PWA)** | Reception, Lab | Low | High | **P3** |
