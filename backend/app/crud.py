from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

# --- USERS ---
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate, hashed_password: str = None):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        del update_data["password"]
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
        
    if hashed_password:
        db_user.hashed_password = hashed_password
        
    db.commit()
    db.refresh(db_user)
    return db_user

# --- PATIENTS ---
def get_patient(db: Session, patient_id: int):
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def get_patient_by_email(db: Session, email: str):
    return db.query(models.Patient).filter(models.Patient.email == email).first()

def get_patients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Patient).offset(skip).limit(limit).all()

def create_patient(db: Session, patient: schemas.PatientCreate):
    db_patient = models.Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def update_patient(db: Session, patient_id: int, patient_update: schemas.PatientUpdate):
    db_patient = get_patient(db, patient_id)
    if not db_patient:
        return None
    for key, value in patient_update.dict(exclude_unset=True).items():
        setattr(db_patient, key, value)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def delete_patient(db: Session, patient_id: int):
    db_patient = get_patient(db, patient_id)
    if not db_patient:
        return None
    db_patient.is_active = False
    db.commit()
    return db_patient

# --- IEIM RECORDS ---
def calculate_overall_score(record: schemas.IEIMRecordCreate) -> float:
    # Fórmula simple de ejemplo (esto se puede perfeccionar luego)
    # Se busca maximizar energía/sueño/movilidad y minimizar dolor/estres/inflamacion
    # Supongamos escala 1 a 10
    positive = record.energy_level + record.sleep_quality + record.mobility
    negative = record.pain_level + record.stress_anxiety + record.inflammation
    
    # max possible is 30 positive, 0 negative -> score 10
    score = ((positive - negative) + 30) / 6.0
    return round(max(1.0, min(10.0, score)), 2)

def create_ieim_record(db: Session, ieim_record: schemas.IEIMRecordCreate):
    overall_score = calculate_overall_score(ieim_record)
    
    db_ieim = models.IEIMRecord(**ieim_record.dict(), overall_score=overall_score)
    db.add(db_ieim)
    db.commit()
    db.refresh(db_ieim)
    return db_ieim

def get_patient_ieim_records(db: Session, patient_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.IEIMRecord)\
             .filter(models.IEIMRecord.patient_id == patient_id)\
             .order_by(models.IEIMRecord.record_date.desc())\
             .offset(skip).limit(limit).all()

# --- MEMBERSHIPS ---
def create_membership(db: Session, membership: schemas.MembershipCreate):
    db_membership = models.Membership(**membership.dict())
    db.add(db_membership)
    db.commit()
    db.refresh(db_membership)
    return db_membership

def get_membership(db: Session, membership_id: int):
    return db.query(models.Membership).filter(models.Membership.id == membership_id).first()

def get_patient_memberships(db: Session, patient_id: int):
    return db.query(models.Membership)\
             .filter(models.Membership.patient_id == patient_id, models.Membership.is_active == True)\
             .all()

def update_membership(db: Session, membership_id: int, membership_update: schemas.MembershipUpdate):
    db_membership = get_membership(db, membership_id)
    if not db_membership:
        return None
    for key, value in membership_update.dict(exclude_unset=True).items():
        setattr(db_membership, key, value)
    db.commit()
    db.refresh(db_membership)
    return db_membership

def delete_membership(db: Session, membership_id: int):
    db_membership = get_membership(db, membership_id)
    if not db_membership:
        return None
    db_membership.is_active = False
    db.commit()
    return db_membership

# --- APPOINTMENTS ---
def create_appointment(db: Session, appointment: schemas.AppointmentCreate):
    db_appointment = models.Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def get_patient_appointments(db: Session, patient_id: int):
    return db.query(models.Appointment)\
             .filter(models.Appointment.patient_id == patient_id)\
             .order_by(models.Appointment.appointment_date.desc())\
             .all()

def get_all_appointments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Appointment)\
             .order_by(models.Appointment.appointment_date.desc())\
             .offset(skip).limit(limit).all()

def get_appointment(db: Session, appointment_id: int):
    return db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()

def update_appointment(db: Session, appointment_id: int, appointment_update: schemas.AppointmentUpdate):
    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        return None
    for key, value in appointment_update.dict(exclude_unset=True).items():
        setattr(db_appointment, key, value)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def delete_appointment(db: Session, appointment_id: int):
    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        return None
    db.delete(db_appointment)
    db.commit()
def complete_appointment(db: Session, appointment_id: int, notes: str):
    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        return None
        
    db_appointment.status = "Completed"
    if notes:
        db_appointment.notes = notes
    
    # Check for active membership to deduct
    active_membership = db.query(models.Membership)\
                          .filter(models.Membership.patient_id == db_appointment.patient_id)\
                          .filter(models.Membership.is_active == True)\
                          .filter(models.Membership.used_sessions < models.Membership.total_sessions)\
                          .first()
                          
    if active_membership:
        active_membership.used_sessions += 1
        
    # Create Clinical History log
    hist_log = models.ClinicalHistory(
        patient_id=db_appointment.patient_id,
        appointment_id=db_appointment.id,
        notes=notes if notes else "Sesión Completada"
    )
    db.add(hist_log)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

# --- PROGRAMS ---
def get_program(db: Session, program_id: int):
    return db.query(models.Program).filter(models.Program.id == program_id).first()

def get_programs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Program).offset(skip).limit(limit).all()

def create_program(db: Session, program: schemas.ProgramCreate):
    db_program = models.Program(**program.dict())
    db.add(db_program)
    db.commit()
    db.refresh(db_program)
    return db_program

def update_program(db: Session, program_id: int, program_update: schemas.ProgramUpdate):
    db_program = get_program(db, program_id)
    if not db_program:
        return None
    for key, value in program_update.dict(exclude_unset=True).items():
        setattr(db_program, key, value)
    db.commit()
    db.refresh(db_program)
    return db_program

def delete_program(db: Session, program_id: int):
    db_program = get_program(db, program_id)
    if not db_program:
        return None
    db_program.is_active = False
    db.commit()
    return db_program
