from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON, Index
from sqlalchemy.orm import relationship, declared_attr
from database import Base
import enum
from datetime import datetime
from pgvector.sqlalchemy import Vector

class AuditableMixin:
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.utcnow)
        
    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
    @declared_attr
    def created_by(cls):
        return Column(Integer, nullable=True)
        
    @declared_attr
    def updated_by(cls):
        return Column(Integer, nullable=True)

class RoleEnum(str, enum.Enum):
    SUPER_ADMIN = "Super Admin"
    HOSPITAL_ADMIN = "Hospital Admin"
    DOCTOR = "Doctor"
    LAB_TECHNICIAN = "Lab Technician"
    PHARMACIST = "Pharmacist"
    RECEPTIONIST = "Receptionist"
    NURSE = "Nurse"
    PATIENT = "Patient"
    FAMILY_MEMBER = "Family Member"
    EMERGENCY_DOCTOR = "Emergency Doctor"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone_number = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String)
    
    is_email_verified = Column(Boolean, default=False)
    is_phone_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    recovery_email = Column(String, nullable=True)
    recovery_phone = Column(String, nullable=True)

    role = Column(String, default=RoleEnum.PATIENT.value)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)

    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    otps = relationship("OTPVerification", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    devices = relationship("UserDevice", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    recovery_codes = relationship("RecoveryCode", back_populates="user", cascade="all, delete-orphan")
    
    doctor_profile = relationship("DoctorProfile", back_populates="user", uselist=False)
    hospital = relationship("Hospital", back_populates="users")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime)
    is_revoked = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="refresh_tokens")

class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    id = Column(Integer, primary_key=True, index=True)
    otp_code = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)
    expires_at = Column(DateTime)
    is_used = Column(Boolean, default=False)

    user = relationship("User", back_populates="otps")

class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_token = Column(String, unique=True, index=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    device_id = Column(String, nullable=True) # References UserDevice.device_id optionally
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="sessions")

class UserDevice(Base):
    __tablename__ = "user_devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(String, unique=True, index=True) # Unique identifier for device (UUID)
    device_name = Column(String, nullable=True)
    device_type = Column(String, nullable=True) # e.g., Windows, Android, Mac, iPhone, Linux
    is_trusted = Column(Boolean, default=False)
    last_login_ip = Column(String, nullable=True)
    last_login_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="devices")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("idx_audit_user_time", "user_id", "timestamp"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String) # LOGIN, LOGOUT, PASSWORD_CHANGE, UNKNOWN_DEVICE_LOGIN, etc.
    ip_address = Column(String, nullable=True)
    status = Column(String) # SUCCESS, FAILED
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON, default={})

    user = relationship("User", back_populates="audit_logs")

class RecoveryCode(Base):
    __tablename__ = "recovery_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    code_hash = Column(String) # Hashed just like passwords
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    used_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="recovery_codes")


# --- MASTER DATA MODELS ---

class Organization(Base, AuditableMixin):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    contact_email = Column(String)
    contact_phone = Column(String)
    is_active = Column(Boolean, default=True)

    hospitals = relationship("Hospital", back_populates="organization", cascade="all, delete-orphan")

class Hospital(Base, AuditableMixin):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    name = Column(String, index=True)
    address = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    settings = Column(JSON, default={}) # Flexible settings storage

    organization = relationship("Organization", back_populates="hospitals")
    users = relationship("User", back_populates="hospital")
    departments = relationship("Department", back_populates="hospital", cascade="all, delete-orphan")

class Department(Base, AuditableMixin):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    name = Column(String, index=True) # e.g. Cardiology, Neurology
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    hospital = relationship("Hospital", back_populates="departments")
    doctors = relationship("DoctorProfile", back_populates="department")

class DoctorProfile(Base, AuditableMixin):
    __tablename__ = "doctor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))
    
    license_number = Column(String, nullable=True)
    experience = Column(Integer, nullable=True) # Years of experience
    qualification = Column(String, nullable=True)
    consultation_fee = Column(Integer, nullable=True)
    availability = Column(JSON, default={})
    status = Column(String, default="Active")

    user = relationship("User", back_populates="doctor_profile")
    department = relationship("Department", back_populates="doctors")

class Laboratory(Base, AuditableMixin):
    __tablename__ = "laboratories"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)
    name = Column(String, index=True)
    address = Column(String)
    license_number = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)

class Pharmacy(Base, AuditableMixin):
    __tablename__ = "pharmacies"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)
    name = Column(String, index=True)
    address = Column(String)
    license_number = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)

class PatientProfile(Base, AuditableMixin):
    __tablename__ = "patient_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)
    health_id = Column(String, unique=True, index=True)
    qr_code_path = Column(String, nullable=True)
    
    # Basic Info
    full_name = Column(String, nullable=True)
    dob = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    blood_group = Column(String, nullable=True)
    address = Column(String, nullable=True)
    profile_photo = Column(String, nullable=True)
    
    # Emergency Info
    emergency_contact_name = Column(String, nullable=True)
    emergency_contact_phone = Column(String, nullable=True)
    emergency_contact_relation = Column(String, nullable=True)
    organ_donor = Column(Boolean, default=False)
    
    # Medical Info
    known_allergies = Column(JSON, default=[])
    chronic_diseases = Column(JSON, default=[])
    current_medications = Column(JSON, default=[])
    past_surgeries = Column(JSON, default=[])

    # AI Cache
    cached_case_history = Column(String, nullable=True)
    case_history_updated_at = Column(DateTime, nullable=True)
    insurance_details = Column(JSON, default={})
    
    # Status & Consent
    status = Column(String, default="Active") # Active, Inactive, Deceased, Merged
    allow_doctor_access = Column(Boolean, default=True)
    allow_hospital_access = Column(Boolean, default=True)
    emergency_access = Column(Boolean, default=True)

    user = relationship("User")
    
    # Knowledge Graph Relationships
    diseases = relationship("Disease", back_populates="patient", cascade="all, delete-orphan")
    medications = relationship("Medication", back_populates="patient", cascade="all, delete-orphan")
    allergies = relationship("Allergy", back_populates="patient", cascade="all, delete-orphan")
    lab_results = relationship("LabResult", back_populates="patient", cascade="all, delete-orphan")

class FileRecord(Base, AuditableMixin):
    __tablename__ = "file_records"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_path = Column(String)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"), nullable=True)
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id"), nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)

# --- PHASE 5: MEDICAL RECORDS MODELS ---

class Appointment(Base, AuditableMixin):
    __tablename__ = "appointments"
    __table_args__ = (
        Index("idx_appointment_doctor_time", "doctor_id", "start_time"),
    )

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id"))
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)
    
    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime, nullable=True)
    status = Column(String, default="Scheduled") # Scheduled, Completed, Cancelled, No-Show
    notes = Column(String, nullable=True)

    patient = relationship("PatientProfile")
    doctor = relationship("DoctorProfile")
    hospital = relationship("Hospital")

class Visit(Base, AuditableMixin):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id"), nullable=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)
    
    visit_date = Column(DateTime, default=datetime.utcnow)
    chief_complaint = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    status = Column(String, default="Completed") # Scheduled, In Progress, Completed
    
    patient = relationship("PatientProfile")
    doctor = relationship("DoctorProfile")
    hospital = relationship("Hospital")

class Diagnosis(Base, AuditableMixin):
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id"), nullable=True)
    
    condition_name = Column(String)
    icd10_code = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    clinical_notes = Column(String, nullable=True)

    visit = relationship("Visit")
    patient = relationship("PatientProfile")
    doctor = relationship("DoctorProfile")

class Prescription(Base, AuditableMixin):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id"), nullable=True)
    
    medications = Column(JSON, default=[]) # e.g. [{"name": "Aspirin", "dosage": "100mg", "frequency": "1/day"}]
    instructions = Column(String, nullable=True)

    visit = relationship("Visit")
    patient = relationship("PatientProfile")
    doctor = relationship("DoctorProfile")

class LabReport(Base, AuditableMixin):
    __tablename__ = "lab_reports"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)
    
    test_name = Column(String)
    results = Column(JSON, default={})
    file_url = Column(String, nullable=True)
    status = Column(String, default="Pending")
    processing_status = Column(String, default="Pending")

    visit = relationship("Visit")
    patient = relationship("PatientProfile")
    hospital = relationship("Hospital")

class Radiology(Base, AuditableMixin):
    __tablename__ = "radiology_reports"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)
    
    scan_type = Column(String) # X-Ray, MRI, CT Scan
    body_part = Column(String, nullable=True)
    file_url = Column(String, nullable=True)
    ai_analysis = Column(JSON, default={})
    processing_status = Column(String, default="Pending")

    visit = relationship("Visit")
    patient = relationship("PatientProfile")
    hospital = relationship("Hospital")

class MedicalDocument(Base, AuditableMixin):
    __tablename__ = "medical_documents"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    uploader_id = Column(Integer, ForeignKey("users.id"))
    
    document_type = Column(String)
    file_url = Column(String)
    extracted_data = Column(JSON, default={})
    processing_status = Column(String, default="Pending")
    embeddings = Column(JSON, default=[])

    patient = relationship("PatientProfile")
    uploader = relationship("User")

class TimelineEvent(Base, AuditableMixin):
    __tablename__ = "timeline_events"
    __table_args__ = (
        Index("idx_timeline_patient_date", "patient_id", "event_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    
    event_type = Column(String) # Visit, Diagnosis, Prescription, LabReport, Radiology, Document
    reference_id = Column(Integer) # ID of the corresponding record
    
    event_date = Column(DateTime, default=datetime.utcnow)
    title = Column(String)
    summary = Column(String, nullable=True)
    
    embedding = Column(Vector(1536), nullable=True)

    patient = relationship("PatientProfile")


class Disease(Base, AuditableMixin):
    __tablename__ = "diseases"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    
    disease_name = Column(String, index=True)
    status = Column(String, nullable=True) # e.g., Chronic, Acute
    severity = Column(String, nullable=True)
    diagnosis_date = Column(DateTime, nullable=True)

    patient = relationship("PatientProfile", back_populates="diseases")

class Medication(Base, AuditableMixin):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    
    medicine_name = Column(String, index=True)
    dosage = Column(String, nullable=True)
    frequency = Column(String, nullable=True)
    status = Column(String, nullable=True) # e.g., Active, Discontinued

    patient = relationship("PatientProfile", back_populates="medications")

class Allergy(Base, AuditableMixin):
    __tablename__ = "allergies"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    
    allergen = Column(String, index=True)
    severity = Column(String, nullable=True)
    reaction = Column(String, nullable=True)

    patient = relationship("PatientProfile", back_populates="allergies")

class LabResult(Base, AuditableMixin):
    __tablename__ = "lab_results_structured" # renamed to avoid conflict with `lab_results` JSON in LabReport if any, though distinct table

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    lab_report_id = Column(Integer, ForeignKey("lab_reports.id"), nullable=True)
    
    biomarker_name = Column(String, index=True)
    value = Column(String)
    unit = Column(String, nullable=True)
    reference_range = Column(String, nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("PatientProfile", back_populates="lab_results")
    lab_report = relationship("LabReport")

class Alert(Base, AuditableMixin):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id"), nullable=True)
    
    alert_type = Column(String, index=True) # e.g., INTERACTION, ALLERGY, CRITICAL_LAB, REMINDER
    severity = Column(String) # HIGH, MEDIUM, LOW
    message = Column(String)
    is_read = Column(Boolean, default=False)
    reference_id = Column(String, nullable=True) # Links to specific lab or medication
    
    patient = relationship("PatientProfile")
    doctor = relationship("DoctorProfile")

class AIAuditLog(Base, AuditableMixin):
    __tablename__ = "ai_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    feature_name = Column(String, index=True)
    input_prompt = Column(String)
    ai_output = Column(String)
    reasoning = Column(String, nullable=True)
    model_used = Column(String, default="gpt-4o-mini")
    confidence_score = Column(Integer, nullable=True)
    
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"), nullable=True)
    patient = relationship("PatientProfile")

# --- PHASE 6: RBAC & SCOPED ACCESS MODELS ---

class Permission(Base, AuditableMixin):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # e.g., "diagnosis.create"
    resource = Column(String) # e.g., "diagnosis"
    action = Column(String) # e.g., "create"
    description = Column(String, nullable=True)

class RolePermission(Base, AuditableMixin):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, index=True) # References RoleEnum value e.g. "Doctor"
    permission_id = Column(Integer, ForeignKey("permissions.id"))
    
    permission = relationship("Permission")

class LabTestOrder(Base, AuditableMixin):
    __tablename__ = "lab_test_orders"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id"), nullable=True)
    
    tests = Column(JSON, default=[]) # e.g. [{"name": "CBC", "priority": "High"}]
    clinical_notes = Column(String, nullable=True)
    status = Column(String, default="Pending") # Pending, Completed, Cancelled

    visit = relationship("Visit")
    patient = relationship("PatientProfile")
    doctor = relationship("DoctorProfile")

class PatientAssignment(Base, AuditableMixin):
    __tablename__ = "patient_assignments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id"))
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    
    status = Column(String, default="Active") # Active, Ended
    assigned_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    doctor = relationship("DoctorProfile")
    patient = relationship("PatientProfile")

class PatientConsent(Base, AuditableMixin):
    __tablename__ = "patient_consents"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    provider_id = Column(Integer, ForeignKey("users.id"))
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)
    
    scope = Column(String) # e.g. "Full", "Read-Only"
    status = Column(String, default="Active") # Active, Revoked, Expired
    expires_at = Column(DateTime, nullable=True)

    patient = relationship("PatientProfile")
    provider = relationship("User")
    hospital = relationship("Hospital")

class EmergencyAccess(Base, AuditableMixin):
    __tablename__ = "emergency_access_logs"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    provider_id = Column(Integer, ForeignKey("users.id"))
    
    reason = Column(String)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True) # If staff assisted
    status = Column(String, default="Active")
    expires_at = Column(DateTime)
    audit_reference = Column(String, nullable=True)

    patient = relationship("PatientProfile")
    provider = relationship("User", foreign_keys=[provider_id])
    approver = relationship("User", foreign_keys=[approved_by])


# --- PHASE 7: BILLING & PAYMENT MODELS ---

class Invoice(Base, AuditableMixin):
    __tablename__ = "invoices"
    __table_args__ = (
        Index("idx_invoice_patient_status", "patient_id", "status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id"), nullable=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=True)
    
    amount = Column(Integer) # Amount in cents / smallest currency unit
    currency = Column(String, default="USD")
    status = Column(String, default="Unpaid") # Unpaid, Paid, Refunded, Cancelled
    
    description = Column(String, nullable=True)
    line_items = Column(JSON, default=[])
    
    due_date = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    payment_method = Column(String, nullable=True) # Stripe, Razorpay, Cash, Card
    receipt_signature = Column(String, nullable=True)

    patient = relationship("PatientProfile")
    hospital = relationship("Hospital")
    doctor = relationship("DoctorProfile")
    visit = relationship("Visit")
    transactions = relationship("PaymentTransaction", back_populates="invoice", cascade="all, delete-orphan")

class PaymentTransaction(Base, AuditableMixin):
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    gateway = Column(String, default="Stripe")
    gateway_transaction_id = Column(String, nullable=True, index=True)
    payment_intent_id = Column(String, nullable=True)
    
    amount = Column(Integer)
    currency = Column(String, default="USD")
    status = Column(String, default="Pending") # Pending, Success, Failed, Refunded
    gateway_response = Column(JSON, default={})

    invoice = relationship("Invoice", back_populates="transactions")


 

# --- PHASE 9: RECORD REVISIONS ---

class RecordRevision(Base):
    __tablename__ = "record_revisions"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("medical_documents.id"))
    changed_by_user_id = Column(Integer, ForeignKey("users.id"))
    previous_data = Column(JSON)
    new_data = Column(JSON)
    change_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    record = relationship("MedicalDocument")
    changed_by = relationship("User")



