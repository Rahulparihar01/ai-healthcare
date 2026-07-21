from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from database import Base
import enum
from datetime import datetime

class RoleEnum(str, enum.Enum):
    SUPER_ADMIN = "Super Admin"
    HOSPITAL_ADMIN = "Hospital Admin"
    DOCTOR = "Doctor"
    LAB_TECHNICIAN = "Lab Technician"
    PHARMACIST = "Pharmacist"
    RECEPTIONIST = "Receptionist"
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
    
    role = Column(String, default=RoleEnum.PATIENT.value)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)

    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    otps = relationship("OTPVerification", back_populates="user", cascade="all, delete-orphan")
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

# --- MASTER DATA MODELS ---

class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    settings = Column(JSON, default={}) # Flexible settings storage

    users = relationship("User", back_populates="hospital")

class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    department = Column(String)
    specialization = Column(String)
    license_number = Column(String)
    medical_council = Column(String)

    user = relationship("User", back_populates="doctor_profile")

class Laboratory(Base):
    __tablename__ = "laboratories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    license_number = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)

class Pharmacy(Base):
    __tablename__ = "pharmacies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    license_number = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)

class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    health_id = Column(String, unique=True, index=True)
    qr_code_path = Column(String, nullable=True)
    
    blood_group = Column(String, nullable=True)
    emergency_contact_name = Column(String, nullable=True)
    emergency_contact_phone = Column(String, nullable=True)
    
    allergies = Column(JSON, default=[])
    personal_details = Column(JSON, default={})
    medical_history = Column(JSON, default={})
    family_history = Column(JSON, default={})
    insurance_details = Column(JSON, default={})
    lifestyle = Column(JSON, default={})

    user = relationship("User")
