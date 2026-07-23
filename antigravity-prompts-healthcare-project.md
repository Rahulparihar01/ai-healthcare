# Antigravity (Gemini) Prompts — Healthcare Paperless System Analysis

Two ready-to-paste prompts for use inside Google Antigravity's agent (Gemini model). Run **Prompt 1** first to get the analysis report, then feed its output (or just run in the same session) into **Prompt 2** for the gap analysis.

Before running, fill in the `[bracketed]` placeholders with your actual repo/module names if you want tighter scoping — otherwise leave them and let the agent explore the whole repo.

---

## PROMPT 1 — Full Codebase Analysis & Report

```
You are acting as a senior full-stack + healthcare-software auditor. You have access to this repository's file system — explore it directly instead of asking me to paste code.

PROJECT CONTEXT:
This is a paperless healthcare management system. Instead of patients carrying paper files to a doctor, the system digitizes the entire patient journey. Core actors/roles include:
- Patient
- Doctor
- Reception / Front-desk staff
- Lab Assistant
- Admin / other staff roles

Tech stack: Python (backend/API) + React (frontend).

YOUR TASK:
Explore the entire repository (backend and frontend folders, config files, requirements.txt/package.json, migrations, tests, docs) and produce a structured ANALYSIS REPORT covering:

1. PROJECT STRUCTURE OVERVIEW
   - Folder/module map with a one-line purpose for each major directory
   - How frontend and backend communicate (REST/GraphQL/WebSocket, base URLs, API versioning)

2. BACKEND (Python) ANALYSIS
   - Framework used (Django/FastAPI/Flask/etc.) and version
   - App/module breakdown (auth, patients, doctors, reception, lab, appointments, reports, etc.)
   - Database models/schema summary and relationships
   - Authentication & role-based access control (how doctor/reception/lab-assistant/admin roles are enforced)
   - API endpoints inventory (method, path, purpose, auth required)
   - Error handling, logging, and validation patterns used
   - Background jobs / async tasks (if any)
   - Dependency list with any outdated or vulnerable packages flagged

3. FRONTEND (React) ANALYSIS
   - State management approach (Redux/Context/Zustand/etc.)
   - Routing structure and role-based route protection
   - Component structure and reusability (list any duplicated logic)
   - API integration layer (axios/fetch wrapper, error handling, token refresh)
   - Form handling & validation library used
   - UI library/design system in use

4. DATA FLOW FOR KEY PATIENT JOURNEYS
   - Trace the full flow for: patient registration → appointment booking → doctor consultation → lab request → lab result upload → report delivery
   - Note where paper-like manual steps still exist (if any) versus fully digital steps

5. CODE QUALITY & MAINTAINABILITY
   - Naming/consistency issues
   - Duplicate or dead code
   - Missing or weak input validation (especially for medical data fields)
   - Test coverage (unit/integration/e2e) — what exists, what's missing
   - Presence/absence of CI config, linting, formatting rules

6. SECURITY & COMPLIANCE FLAGS
   - Handling of sensitive patient data (PII/PHI) at rest and in transit
   - Password/token storage, session handling
   - Role/permission leaks (e.g., can a lab assistant see billing data they shouldn't?)
   - Any hardcoded secrets/keys found in the repo

OUTPUT FORMAT:
Return the report as a single structured Markdown document with the sections above as headings, using tables where useful (e.g., API endpoint inventory, dependency list). Be specific — cite actual file paths and line numbers/function names as evidence for every finding, not generic statements. End with a short "Summary of Findings" table (Category | Status: Good/Warning/Critical | Key Issue).

Do not propose fixes yet — this prompt is for analysis and reporting only.
```

---

## PROMPT 2 — Gap Analysis & Prioritized Roadmap

```
You are continuing as the same auditor. You now have the analysis report from the previous step (or, if this is a fresh session, re-explore the repository the same way as before) for a paperless healthcare management system built in Python (backend) + React (frontend), covering roles: Patient, Doctor, Reception, Lab Assistant, Admin/other staff.

YOUR TASK:
Perform a GAP ANALYSIS comparing the CURRENT implementation against what a production-grade, fully paperless healthcare workflow requires. Structure your answer as follows:

1. FUNCTIONAL GAPS (by role)
   For each role — Patient, Doctor, Reception, Lab Assistant, Admin — list:
   - What the system currently supports (with file/module evidence)
   - What's missing or incomplete for that role's real-world workflow
   - Any workflow step that still implicitly assumes paper/manual handoff

2. CROSS-CUTTING GAPS
   - Notifications (SMS/email/push for appointments, lab results, reminders)
   - Audit trail / activity logs (who accessed/changed what patient record, when)
   - Multi-location/branch support (if relevant)
   - Offline handling / poor-connectivity resilience (relevant for reception/lab desks)
   - Reporting & analytics (admin dashboards, doctor's patient history view, lab turnaround metrics)
   - File/document handling (scanned reports, prescriptions as PDF, image uploads for lab results)
   - Multi-language / accessibility support

3. SECURITY & COMPLIANCE GAPS
   - Gaps against standard healthcare data-protection expectations (access control granularity, encryption at rest/in transit, consent management, data retention/deletion policy)
   - Session/token expiry and re-authentication gaps
   - Any role able to access data outside its intended scope

4. TECHNICAL / ARCHITECTURE GAPS
   - Scalability concerns (DB indexing, N+1 queries, pagination on large patient lists)
   - Testing gaps (list specific untested critical paths, e.g. lab result upload, prescription generation)
   - Missing CI/CD, environment config management, or deployment documentation
   - API design inconsistencies between frontend expectations and backend implementation

5. PRIORITIZED GAP TABLE
   Produce a table with columns: Gap | Affected Role(s) | Impact (High/Medium/Low) | Effort to Fix (High/Medium/Low) | Recommended Priority (P0/P1/P2)
   Sort by priority, P0 first.

6. SUGGESTED NEXT STEPS
   A short numbered action plan (5-10 items) for the next development sprint, ordered by priority, each tied back to a specific gap above.

OUTPUT FORMAT:
Structured Markdown with headings and tables as specified. Every gap must reference concrete evidence from the codebase (file/function/route), not generic industry assumptions. Where you are inferring a gap rather than confirming it from code (e.g., "no notification system found"), explicitly say so as "Not found in codebase" rather than assuming intent.
```

---

### How to use these
1. Open your project in Antigravity, start a new agent session with Gemini.
2. Paste **Prompt 1** as-is (it works best when the agent has full repo access rather than pasted snippets).
3. Once you have the report, either continue in the same chat or start fresh and paste **Prompt 2**.
4. If your repo is large, you can scope either prompt by adding a line like: `Limit exploration to: backend/apps/patients, backend/apps/lab, frontend/src/pages/reception` — this keeps the agent focused and avoids partial/truncated exploration on big codebases.
