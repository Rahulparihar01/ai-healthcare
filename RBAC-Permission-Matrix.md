# HealthID AI — Role-Based Access Control (RBAC) Permission Matrix

This document defines exactly what each department/role can view, create, edit, or delete across the platform. Use this as the spec for implementing RBAC checks in the backend (JWT claim → role → permitted actions per module).

---

## 1. Roles Covered

| Role | Description |
|---|---|
| **Super Admin** | Platform-level owner. Manages multiple hospitals/organizations. |
| **Hospital Admin** | Manages one hospital/clinic — its staff, settings, and billing configuration. |
| **Doctor** | Clinical staff. Treats patients, writes prescriptions, orders tests, uses AI Copilot. |
| **Receptionist** | Front-desk staff. Handles registration, appointments, and billing — not clinical data. |
| **Lab Technician** | Handles lab test orders and uploads lab reports/results — not medicine prescriptions or billing. |
| **Patient** | End user. Views their own records and controls consent/access grants. |

---

## 2. Permission Legend

| Symbol | Meaning |
|---|---|
| ✅ Full | Create, View, Edit, Delete |
| 👁️ View Only | Can view, cannot create/edit/delete |
| 🔒 Scoped | Access limited to specific records (own patients / own org / own data) — see notes |
| ❌ None | No access at all |

---

## 3. Master Permission Matrix

| Module | Super Admin | Hospital Admin | Doctor | Receptionist | Lab Technician | Patient |
|---|---|---|---|---|---|---|
| Patient Registration (Health ID / QR) | ✅ Full | ✅ Full | 👁️ View | ✅ Full | ❌ None | 🔒 Own profile only |
| Patient Demographics & Profile | ✅ Full | ✅ Full | 👁️ View (assigned patients) | ✅ Full | ❌ None | 🔒 Own profile only |
| Appointment Scheduling | ✅ Full | ✅ Full | 👁️ View own schedule | ✅ Full | ❌ None | 🔒 Own appointments only |
| Medical Documents (Discharge summaries, general uploads) | ✅ Full | 👁️ View (org-wide) | 🔒 Full (assigned patients only) | ❌ None | ❌ None | 🔒 Own documents only |
| Radiology Reports (MRI/CT/X-Ray/ECG) | ✅ Full | 👁️ View (org-wide) | 🔒 Full (assigned patients only) | ❌ None | 👁️ View only (uploaded reports, not clinical interpretation edits) | 🔒 Own reports only |
| Lab Test Orders ("prescription" in lab context — the test/investigation request, NOT medicine) | ✅ Full | 👁️ View | ✅ Full — creates/edits test orders (assigned patients) | ❌ None | 👁️ View only (sees what tests were ordered, to know what to run) | 🔒 Own orders only |
| Lab Reports / Test Results | ✅ Full | 👁️ View (org-wide) | 👁️ View (assigned patients) | ❌ None | ✅ Full — uploads/edits results for ordered tests | 🔒 Own results only |
| Medicine Prescriptions (drug name, dosage, frequency) | ✅ Full | 👁️ View (org-wide) | ✅ Full (assigned patients) | ❌ None | ❌ None | 🔒 Own prescriptions only |
| Disease History / Diagnoses | ✅ Full | 👁️ View (org-wide) | ✅ Full (assigned patients) | ❌ None | ❌ None | 🔒 Own history only |
| Allergy Records | ✅ Full | 👁️ View (org-wide) | ✅ Full (assigned patients) | 👁️ View only *(emergency mode)* | ❌ None | 🔒 Own records only |
| AI Copilot — Summaries / Alerts / RAG Assistant | ✅ Full | 👁️ View (org-wide) | ✅ Full (assigned patients) | ❌ None | ❌ None | 🔒 Patient-facing assistant only, own data |
| Medical Timeline | ✅ Full | 👁️ View (org-wide) | ✅ Full (assigned patients) | ❌ None | ❌ None | 🔒 Own timeline only |
| Billing & Invoicing | ✅ Full | ✅ Full | ❌ None | ✅ Full | ❌ None | 🔒 Own invoices/payment history only |
| Consent & Access Management | ✅ Full (override, audited) | 🔒 Staff-assisted grants only, on patient's behalf | ❌ None (can request access, cannot grant it) | 🔒 Staff-assisted grants only, on patient's behalf | ❌ None | ✅ Full — grants/revokes provider access |
| Emergency Mode (blood group, allergies, conditions, emergency contacts only) | ✅ Full | ✅ Full | ✅ Full | ❌ None | ❌ None | N/A |
| Population Health Analytics | ✅ Full (cross-org) | 👁️ View (own org only) | ❌ None | ❌ None | ❌ None | ❌ None |
| Staff / User Management | ✅ Full (cross-org) | 🔒 Own hospital's staff only | ❌ None | ❌ None | ❌ None | ❌ None |
| Organization / Hospital Settings | ✅ Full | 🔒 Own hospital only | ❌ None | ❌ None | ❌ None | ❌ None |
| Audit Logs | ✅ Full (cross-org) | 👁️ View (own org only) | ❌ None | ❌ None | ❌ None | 👁️ View own access history only |

---

## 4. Per-Role Summary (plain-language, for your agent)

### 🧑‍💼 Receptionist
- **Has:** Full access to patient registration, appointment scheduling, and **billing/invoicing** — this is their core job.
- **Does not have:** Any access to clinical data — no medical documents, no lab reports, no prescriptions, no diagnoses, no AI Copilot. They should not even see a list of a patient's medicines or test results, only that a visit/invoice exists.
- **Exception:** Can view allergy info **only** in Emergency Mode context, not standard workflow — since that mode is designed for immediate front-desk/first-responder visibility, not general reception duties.

### 🩺 Doctor
- **Has:** Full clinical access for **their assigned patients only** — medical documents, radiology reports, disease history, medicine prescriptions, allergy records, AI Copilot, and the medical timeline.
- **Also creates lab test orders** (the "prescription" that tells the lab what to test — distinct from a medicine prescription).
- **Does not have:** Any billing/invoicing access. A doctor should never see what a patient was charged or their payment status — that's kept fully separate from clinical work.

### 🧪 Lab Technician
- **Has:** View access to **lab test orders** (what the doctor requested — this is the "prescription" in lab terms, i.e., the test/investigation request, not a medicine list) and full access to **upload/edit lab reports/results** for those ordered tests.
- **Does not have:** Access to medicine prescriptions, diagnoses, disease history, billing, or the AI Copilot. Their access is scoped strictly to the test-order → result-upload workflow.
- **Important distinction to build into the schema:** keep `LabTestOrder` (the request) and `MedicinePrescription` (the drug prescription) as separate models/tables from day one, so a permission check on one can never accidentally expose the other.

### 🏢 Hospital Admin
- **Has:** Full administrative control over their own hospital — staff accounts, billing configuration, org settings — plus **view-only** visibility into clinical data across their hospital (for oversight, not day-to-day clinical work) and org-scoped population analytics.
- **Does not have:** Ability to edit clinical records directly (they view, doctors edit), and no access to other hospitals' data (strict multi-tenant isolation).

### 🛡️ Super Admin
- **Has:** Full access across every hospital/org on the platform, including cross-org analytics, staff management, and an audited override for emergency/support situations.
- **Note:** Because this role is the highest-privilege one, every Super Admin action on clinical data should be logged with extra detail in the audit trail — this role is the biggest single risk if compromised.

### 🙋 Patient
- **Has:** Full view access to their own records (documents, prescriptions, lab results, timeline), plus the ability to **grant or revoke** provider access (or have staff do it on their behalf where the patient can't manage a smartphone/app themselves).
- **Does not have:** Any access to other patients' data, obviously, and cannot self-edit clinical data (e.g., can't edit their own diagnosis) — only view it and interact with the patient-facing AI Assistant.

---

## 5. Key Design Rules to Enforce in Code

1. **Billing and clinical data must never share a permission check.** A Receptionist role should be structurally incapable of querying clinical tables, not just hidden in the UI.
2. **"Prescription" is two different things — do not merge them.** `LabTestOrder` (what test to run) and `MedicinePrescription` (what drug to take) must be distinct models with distinct permissions, even though both might loosely be called "prescription" in conversation.
3. **Doctor access is scoped to assigned/treating patients, not the whole hospital.** Only Hospital Admin and Super Admin get org-wide clinical visibility, and even then it should default to view-only.
4. **Every non-patient access to a patient record should be consent-gated or logged**, including staff-assisted consent for patients who can't manage this themselves (e.g., rural/elderly patients).
5. **Emergency Mode is a narrow, separate permission set** — not a backdoor to full records. It should expose only blood group, allergies, existing conditions, and emergency contacts, and every use of it should be logged for later review.
