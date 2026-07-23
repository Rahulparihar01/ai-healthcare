# HealthID AI RBAC Architecture Analysis & Implementation Report

**Version:** 1.0\
**Status:** Design Review\
**Purpose:** Analyze the current authorization architecture and compare
it against the proposed RBAC specification.

------------------------------------------------------------------------

# Executive Summary

The current HealthID AI backend already implements a solid **Role-Based
Access Control (RBAC)** foundation using JWT authentication, `RoleEnum`,
and hospital-scoped multi-tenancy. Dynamic departments are also
implemented correctly, allowing each hospital to maintain its own
organizational structure.

However, the authorization model is currently **role-driven**, where
access decisions are primarily based on user roles within application
logic. The proposed RBAC specification introduces a more mature
authorization model that combines **roles, permissions, patient
assignment, consent, emergency access, and auditing**.

Overall, the existing implementation provides approximately **80--85%**
of the required foundation. The remaining work focuses on introducing
fine-grained permissions and contextual authorization without replacing
the current architecture.

------------------------------------------------------------------------

# Current Codebase Analysis

## Authentication

Current implementation includes:

-   JWT Authentication
-   User Identity
-   RoleEnum
-   Hospital Association

**Assessment**

-   Production-ready authentication foundation.
-   No major architectural changes required.

------------------------------------------------------------------------

## Departments

Current implementation:

-   Departments are dynamically stored in the database.
-   Each department belongs to a hospital.
-   No hardcoded department list.

### Department Model

-   `hospital_id`
-   `name`
-   `description`
-   `is_active`

### Strengths

-   Supports unlimited hospitals.
-   Supports unlimited departments.
-   Easily configurable by Hospital Admins.

**Status:** Excellent (10/10)

------------------------------------------------------------------------

## Current Role System

Current roles available:

-   SUPER_ADMIN
-   HOSPITAL_ADMIN
-   DOCTOR
-   LAB_TECHNICIAN
-   PHARMACIST
-   RECEPTIONIST
-   NURSE
-   PATIENT
-   FAMILY_MEMBER
-   EMERGENCY_DOCTOR

Current authorization flow:

``` text
JWT
 ↓
Role
 ↓
Business Logic
 ↓
Access Decision
```

Typical implementation:

``` python
if user.role == RoleEnum.DOCTOR:
    allow()
```

### Assessment

Good for MVP.

However, permissions are implicitly embedded inside application logic
instead of being modeled explicitly.

------------------------------------------------------------------------

# Comparison with Proposed RBAC Specification

  Capability                       Current Codebase   Proposed RBAC
  -------------------------------- ------------------ ---------------
  JWT Authentication               ✅                 ✅
  Multi-Tenant Architecture        ✅                 ✅
  Dynamic Departments              ✅                 ✅
  Role-Based Access                ✅                 ✅
  Permission-Based Access          ❌                 ✅
  Patient Assignment               Partial            ✅
  Consent Enforcement              Partial            ✅
  Emergency Access                 Partial            ✅
  Billing vs Clinical Separation   Partial            ✅
  Resource-Level Authorization     ❌                 ✅
  Detailed Audit Controls          Partial            ✅

------------------------------------------------------------------------

# Architectural Gaps

## 1. Roles are acting as Permissions

Current implementation:

``` text
Doctor
    ↓
Everything a doctor can do
```

Problem:

Permissions are hidden inside business logic.

### Recommendation

Introduce explicit permissions.

Examples:

-   patient.read
-   patient.update
-   diagnosis.create
-   prescription.create
-   lab_order.create
-   lab_result.upload
-   appointment.manage
-   billing.view
-   ai.summary

Roles become collections of permissions rather than permissions
themselves.

------------------------------------------------------------------------

## 2. Missing Patient Resource Scoping

Current:

Doctor role grants general clinical access.

Required:

Doctors should only access assigned patients.

### Recommended Model

``` text
Doctor
    ↓
Permission
    ↓
Patient Assignment
    ↓
Access Granted
```

Suggested table:

-   doctor_id
-   patient_id
-   status
-   assigned_at
-   ended_at

------------------------------------------------------------------------

## 3. Consent Not Fully Integrated

Current implementation contains consent concepts but authorization does
not consistently evaluate them.

Recommended authorization sequence:

``` text
Role
 ↓
Permission
 ↓
Patient Assignment
 ↓
Consent Validation
 ↓
Access
```

Suggested Consent Model:

-   patient_id
-   provider_id
-   hospital_id
-   scope
-   expires_at
-   status

------------------------------------------------------------------------

## 4. Emergency Access

Current implementation uses a dedicated `EMERGENCY_DOCTOR` role.

Recommendation:

Replace permanent elevated access with temporary emergency sessions.

Suggested model:

-   requested_by
-   approved_by
-   reason
-   start_time
-   end_time
-   audit_reference

Every emergency access should be logged.

------------------------------------------------------------------------

## 5. Hospital Isolation

Hospital association already exists.

Recommendation:

Every repository query should automatically filter by:

``` sql
WHERE hospital_id = current_user.hospital_id
```

before evaluating permissions.

------------------------------------------------------------------------

# Recommended Permission Groups

## Administrative

-   staff.create
-   staff.update
-   staff.delete
-   department.manage
-   hospital.manage

## Patient

-   patient.create
-   patient.read
-   patient.update

## Appointment

-   appointment.create
-   appointment.read
-   appointment.update

## Clinical

-   diagnosis.create

-   diagnosis.read

-   diagnosis.update

-   prescription.create

-   prescription.read

-   allergy.update

## Laboratory

-   lab_order.create

-   lab_order.read

-   lab_result.upload

-   lab_result.edit

-   lab_result.view

## Radiology

-   radiology.upload
-   radiology.view

## Billing

-   invoice.create
-   invoice.read
-   invoice.update

## AI

-   ai.summary
-   ai.chat
-   ai.alert
-   ai.search

## Consent

-   consent.grant
-   consent.revoke
-   consent.override

## Audit

-   audit.read
-   audit.export

------------------------------------------------------------------------

# Recommended Authorization Flow

Current:

``` text
JWT
 ↓
Role
 ↓
Access
```

Recommended:

``` text
JWT
 ↓
Authentication
 ↓
Hospital Validation
 ↓
Role Validation
 ↓
Permission Validation
 ↓
Patient Assignment
 ↓
Consent Validation
 ↓
Emergency Override
 ↓
Audit Logging
 ↓
Access Granted
```

------------------------------------------------------------------------

# Recommended Database Enhancements

## permissions

-   id
-   name
-   resource
-   action
-   description

## role_permissions

-   role_id
-   permission_id

## patient_assignments

-   doctor_id
-   patient_id
-   status
-   assigned_at
-   ended_at

## patient_consents

-   patient_id
-   provider_id
-   hospital_id
-   scope
-   expires_at

## emergency_access

-   patient_id
-   provider_id
-   reason
-   approved_by
-   expires_at

------------------------------------------------------------------------

# Security Recommendations

-   Default Deny Policy
-   Least Privilege Principle
-   Hospital Isolation
-   Patient Scoped Authorization
-   Consent Validation
-   Immutable Audit Logs
-   Time-Limited Emergency Access

------------------------------------------------------------------------

# Migration Strategy

## Phase 1

-   Retain current RoleEnum.
-   Introduce permission middleware.

## Phase 2

Add:

-   permissions
-   role_permissions

without affecting existing users.

## Phase 3

Implement:

-   Patient Assignment
-   Consent Validation
-   Emergency Access

## Phase 4

Replace hardcoded role checks such as:

``` python
if role == DOCTOR:
```

with centralized authorization:

``` python
authorize(
    user=user,
    permission="diagnosis.create",
    patient=patient_id
)
```

------------------------------------------------------------------------

# Overall Assessment

  Area                         Score
  ------------------------- --------
  Authentication               10/10
  Multi-Tenant Design          10/10
  Dynamic Departments          10/10
  Current RBAC Foundation     8.5/10
  Permission Granularity        4/10
  Resource Scoping              5/10
  Consent Integration           5/10
  Emergency Controls            6/10
  Auditability                  8/10
  Production Readiness        8.5/10

------------------------------------------------------------------------

# Final Conclusion

The current HealthID AI authorization architecture provides a strong
RBAC foundation suitable for an MVP. The use of JWT authentication,
dynamic departments, hospital-scoped resources, and role-based
authorization establishes a solid base for future growth.

To achieve an enterprise-grade healthcare authorization model, the
platform should evolve beyond role-only authorization by introducing
explicit permissions, patient-scoped access, consent-aware
authorization, emergency override workflows, and comprehensive auditing.

Rather than replacing the current architecture, the recommended approach
is to extend the existing `RoleEnum` model with a permission layer and
contextual authorization. This minimizes disruption while significantly
improving security, scalability, and maintainability.

**Estimated alignment with the proposed RBAC specification:**
**80--85%**.
