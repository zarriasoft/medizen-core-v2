from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(String, default="staff") # admin, staff, doctor
    is_active = Column(Boolean, default=True)

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    date_of_birth = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    ieim_records = relationship("IEIMRecord", back_populates="patient")
    memberships = relationship("Membership", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")

class IEIMRecord(Base):
    __tablename__ = "ieim_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    record_date = Column(DateTime, default=datetime.utcnow)
    
    # Las 6 variables del IEIM v2.0
    pain_level = Column(Float)
    sleep_quality = Column(Float)
    energy_level = Column(Float)
    stress_anxiety = Column(Float)
    mobility = Column(Float)
    inflammation = Column(Float)
    
    # Indice calculado general
    overall_score = Column(Float)

    patient = relationship("Patient", back_populates="ieim_records")

class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True) # Ej: Anti Estrés, Dolor Crónico
    description = Column(String)
    default_sessions = Column(Integer)
    is_active = Column(Boolean, default=True)

class MembershipPlan(Base):
    __tablename__ = "membership_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True) # Básica, Integrativa, Premium
    price = Column(String)
    frequency = Column(String) # mensual, anual
    features = Column(String) # Comma-separated or JSON
    color = Column(String, default="slate")
    is_popular = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)


class Membership(Base):
    __tablename__ = "memberships"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    membership_type = Column(String) # Pack 10, Mensual, VIP
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    total_sessions = Column(Integer, default=0)
    used_sessions = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    patient = relationship("Patient", back_populates="memberships")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    membership_id = Column(Integer, ForeignKey("memberships.id"), nullable=True) # ID of the membership session used
    appointment_date = Column(DateTime)
    notes = Column(String, nullable=True)
    status = Column(String, default="Scheduled") # Scheduled, Completed, Cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="appointments")
    membership = relationship("Membership")

class ClinicalHistory(Base):
    __tablename__ = "clinical_histories"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    date_recorded = Column(DateTime, default=datetime.utcnow)
    notes = Column(String)
    
    patient = relationship("Patient")
    appointment = relationship("Appointment")
