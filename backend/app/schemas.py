from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import List, Optional

# --- USER SCHEMAS ---
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "staff"
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserUpdateMe(BaseModel):
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class User(UserBase):
    id: int

    class Config:
        orm_mode = True

# --- TOKEN SCHEMAS ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

# --- PATIENT SCHEMAS ---

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    is_active: Optional[bool] = None

class PatientUpdateMe(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None

class Patient(PatientBase):
    id: int
    created_at: datetime
    is_active: bool
    ieim_records: List['IEIMRecord'] = []

    class Config:
        orm_mode = True

# --- IEIM RECORD SCHEMAS ---
class IEIMRecordBase(BaseModel):
    pain_level: float
    sleep_quality: float
    energy_level: float
    stress_anxiety: float
    mobility: float
    inflammation: float

class IEIMRecordCreate(IEIMRecordBase):
    patient_id: int

class IEIMRecord(IEIMRecordBase):
    id: int
    patient_id: int
    record_date: datetime
    overall_score: float

    class Config:
        orm_mode = True

# --- PROGRAM SCHEMAS ---
class ProgramBase(BaseModel):
    name: str
    description: Optional[str] = None
    default_sessions: int

class ProgramCreate(ProgramBase):
    pass

class ProgramUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    default_sessions: Optional[int] = None
    is_active: Optional[bool] = None

class Program(ProgramBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

# --- MEMBERSHIP PLAN SCHEMAS ---
class MembershipPlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: str
    frequency: str
    features: str
    color: Optional[str] = "slate"
    is_popular: Optional[bool] = False
    total_sessions: Optional[int] = 1

class MembershipPlanCreate(MembershipPlanBase):
    pass

class MembershipPlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None
    frequency: Optional[str] = None
    features: Optional[str] = None
    color: Optional[str] = None
    is_popular: Optional[bool] = None
    total_sessions: Optional[int] = None
    is_active: Optional[bool] = None

class MembershipPlan(MembershipPlanBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


# --- MEMBERSHIP SCHEMAS ---
class MembershipBase(BaseModel):
    membership_type: str
    total_sessions: int

class MembershipCreate(MembershipBase):
    patient_id: int
    end_date: Optional[datetime] = None

class MembershipUpdate(BaseModel):
    end_date: Optional[datetime] = None
    used_sessions: Optional[int] = None
    is_active: Optional[bool] = None

class Membership(MembershipBase):
    id: int
    patient_id: int
    start_date: datetime
    end_date: Optional[datetime] = None
    used_sessions: int
    is_active: bool

    class Config:
        orm_mode = True

class MembershipWithPatient(Membership):
    patient_name: Optional[str] = None
    patient_last_name: Optional[str] = None

    class Config:
        from_attributes = True

# --- APPOINTMENT SCHEMAS ---
class AppointmentBase(BaseModel):
    appointment_date: datetime
    membership_id: Optional[int] = None
    notes: Optional[str] = None
    status: Optional[str] = "Scheduled"

class AppointmentCreate(AppointmentBase):
    patient_id: int

class AppointmentUpdate(BaseModel):
    appointment_date: Optional[datetime] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class Appointment(AppointmentBase):
    id: int
    patient_id: int
    membership_id: Optional[int] = None
    created_at: datetime

    class Config:
        orm_mode = True

# --- CLINICAL HISTORY SCHEMAS ---
class ClinicalHistoryBase(BaseModel):
    notes: str

class ClinicalHistoryCreate(ClinicalHistoryBase):
    patient_id: int
    appointment_id: Optional[int] = None

class ClinicalHistory(ClinicalHistoryBase):
    id: int
    patient_id: int
    appointment_id: Optional[int] = None
    date_recorded: datetime

    class Config:
        orm_mode = True

# --- SYSTEM SETTINGS SCHEMAS ---
class SystemSettingsBase(BaseModel):
    smtp_host: Optional[str] = "smtp.gmail.com"
    smtp_port: Optional[int] = 587
    smtp_user: Optional[str] = ""
    smtp_password: Optional[str] = ""
    admin_email: Optional[str] = ""

class SystemSettingsUpdate(SystemSettingsBase):
    pass

class SystemSettings(SystemSettingsBase):
    id: int
    updated_at: datetime

    class Config:
        orm_mode = True

class SystemSettingsOut(BaseModel):
    id: int
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    admin_email: Optional[str] = None
    updated_at: datetime

    class Config:
        orm_mode = True

class SystemSettingsPublic(BaseModel):
    admin_email: Optional[str] = ""

    class Config:
        orm_mode = True


# --- SPECIALIST AVAILABILITY SCHEMAS ---
class SpecialistScheduleBase(BaseModel):
    day_of_week: int
    start_time: str
    end_time: str
    is_active: Optional[bool] = True

class SpecialistScheduleCreate(SpecialistScheduleBase):
    pass

class SpecialistSchedule(SpecialistScheduleBase):
    id: int

    class Config:
        orm_mode = True

class ScheduleOverrideBase(BaseModel):
    override_date: date
    is_day_off: Optional[bool] = True
    start_time: Optional[str] = None
    end_time: Optional[str] = None

class ScheduleOverrideCreate(ScheduleOverrideBase):
    pass

class ScheduleOverride(ScheduleOverrideBase):
    id: int

    class Config:
        orm_mode = True

class TimeSlot(BaseModel):
    start_time: str
    end_time: str
    is_available: bool

Patient.model_rebuild() if hasattr(Patient, 'model_rebuild') else Patient.update_forward_refs()
