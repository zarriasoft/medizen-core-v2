from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime
from sqlalchemy.sql import func

# --- USERS ---
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(func.lower(models.User.email) == email.lower()).first()

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
    return db.query(models.Patient).filter(func.lower(models.Patient.email) == email.lower()).first()

def get_patients(db: Session, skip: int = 0, limit: int = 10000):
    return db.query(models.Patient).order_by(models.Patient.first_name.asc(), models.Patient.last_name.asc()).offset(skip).limit(limit).all()

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
             .filter(models.Membership.patient_id == patient_id)\
             .all()

def get_all_memberships(db: Session, skip: int = 0, limit: int = 10000):
    memberships = db.query(
        models.Membership, 
        models.Patient.first_name.label('patient_name'), 
        models.Patient.last_name.label('patient_last_name')
    )\
    .join(models.Patient, models.Membership.patient_id == models.Patient.id)\
    .order_by(models.Membership.start_date.desc())\
    .offset(skip).limit(limit).all()
    
    # Map to schema
    result = []
    for mem, p_name, p_lname in memberships:
        # Create schema object from membership model
        mem_schema = schemas.MembershipWithPatient.from_orm(mem)
        mem_schema.patient_name = p_name
        mem_schema.patient_last_name = p_lname
        result.append(mem_schema)
        
    return result

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

# --- MEMBERSHIP PLANS ---
def get_membership_plans(db: Session, skip: int = 0, limit: int = 1000):
    return db.query(models.MembershipPlan).order_by(models.MembershipPlan.id.asc()).offset(skip).limit(limit).all()

def get_membership_plan(db: Session, plan_id: int):
    return db.query(models.MembershipPlan).filter(models.MembershipPlan.id == plan_id).first()

def get_membership_plan_by_name(db: Session, plan_name: str):
    return db.query(models.MembershipPlan).filter(models.MembershipPlan.name == plan_name).first()

def create_membership_plan(db: Session, plan: schemas.MembershipPlanCreate):
    db_plan = models.MembershipPlan(**plan.dict())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def update_membership_plan(db: Session, plan_id: int, plan_update: schemas.MembershipPlanUpdate):
    db_plan = get_membership_plan(db, plan_id)
    if not db_plan:
        return None
    for key, value in plan_update.dict(exclude_unset=True).items():
        setattr(db_plan, key, value)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def delete_membership_plan(db: Session, plan_id: int):
    db_plan = get_membership_plan(db, plan_id)
    if not db_plan:
        return None
        
    # Check if there are active memberships using this plan name
    # We match by plan.name since Membership currently uses membership_type
    active_memberships = db.query(models.Membership)\
        .filter(models.Membership.membership_type == db_plan.name)\
        .filter(models.Membership.is_active == True)\
        .first()
        
    if active_memberships:
        return {"error": f"Cannot delete plan '{db_plan.name}' because there are active memberships using it."}
        
    db_plan.is_active = False
    db.commit()
    return db_plan

# --- APPOINTMENTS ---
def create_appointment(db: Session, appointment: schemas.AppointmentCreate):
    db_appointment = models.Appointment(**appointment.dict())
    
    # Just link the membership if active, DO NOT deduct yet (deduct on completion)
    # Only assign automatically if the frontend didn't already send one
    if not db_appointment.membership_id:
        active_membership = db.query(models.Membership)\
                              .filter(models.Membership.patient_id == appointment.patient_id)\
                              .filter(models.Membership.is_active == True)\
                              .filter(models.Membership.used_sessions < models.Membership.total_sessions)\
                              .first()
                              
        if active_membership:
            db_appointment.membership_id = active_membership.id
            
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def get_patient_appointments(db: Session, patient_id: int):
    return db.query(models.Appointment)\
             .filter(models.Appointment.patient_id == patient_id)\
             .order_by(models.Appointment.appointment_date.desc())\
             .all()

def get_all_appointments(db: Session, skip: int = 0, limit: int = 10000):
    return db.query(models.Appointment)\
             .order_by(models.Appointment.appointment_date.desc())\
             .offset(skip).limit(limit).all()

def get_appointment(db: Session, appointment_id: int):
    return db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()

def update_appointment(db: Session, appointment_id: int, appointment_update: schemas.AppointmentUpdate):
    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        return None
        
    old_status = db_appointment.status
    
    for key, value in appointment_update.dict(exclude_unset=True).items():
        setattr(db_appointment, key, value)
        
    # If the status is moved FROM "Completed" to something else, we must REFUND the session
    if old_status == "Completed" and db_appointment.status != "Completed" and db_appointment.membership_id:
        membership = get_membership(db, db_appointment.membership_id)
        if membership:
            membership.used_sessions -= 1
            if membership.used_sessions < membership.total_sessions:
                membership.is_active = True
                
    # If the status is moved TO "Completed" from something else, we must DEDUCT the session
    elif old_status != "Completed" and db_appointment.status == "Completed":
        # First try to re-use the linked membership if it has space
        linked_membership = get_membership(db, db_appointment.membership_id) if db_appointment.membership_id else None
        
        if linked_membership and linked_membership.used_sessions < linked_membership.total_sessions:
            linked_membership.used_sessions += 1
            if linked_membership.used_sessions >= linked_membership.total_sessions:
                linked_membership.is_active = False
        else:
            # If not possible, try to find a new active one
            active_membership = db.query(models.Membership)\
                                  .filter(models.Membership.patient_id == db_appointment.patient_id)\
                                  .filter(models.Membership.is_active == True)\
                                  .filter(models.Membership.used_sessions < models.Membership.total_sessions)\
                                  .first()
            if active_membership:
                active_membership.used_sessions += 1
                db_appointment.membership_id = active_membership.id
                if active_membership.used_sessions >= active_membership.total_sessions:
                    active_membership.is_active = False
            else:
                db_appointment.membership_id = None # Clear it if we couldn't get a session
                
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def delete_appointment(db: Session, appointment_id: int):
    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        return None
        
    # Only refund if it was Completed!
    if db_appointment.status == "Completed" and db_appointment.membership_id:
        membership = get_membership(db, db_appointment.membership_id)
        if membership:
            membership.used_sessions -= 1
            if membership.used_sessions < membership.total_sessions:
                membership.is_active = True
                
    db.delete(db_appointment)
    db.commit()
    return db_appointment
def complete_appointment(db: Session, appointment_id: int, notes: str):
    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        return None
        
    old_status = db_appointment.status
    db_appointment.status = "Completed"
    
    if notes:
        db_appointment.notes = notes
        
    # Deduct membership session here IF it wasn't already completed
    if old_status != "Completed":
        linked_membership = get_membership(db, db_appointment.membership_id) if db_appointment.membership_id else None
        
        if linked_membership and linked_membership.used_sessions < linked_membership.total_sessions:
            linked_membership.used_sessions += 1
            if linked_membership.used_sessions >= linked_membership.total_sessions:
                linked_membership.is_active = False
        else:
            # Try to find a new active one
            active_membership = db.query(models.Membership)\
                                  .filter(models.Membership.patient_id == db_appointment.patient_id)\
                                  .filter(models.Membership.is_active == True)\
                                  .filter(models.Membership.used_sessions < models.Membership.total_sessions)\
                                  .first()
            if active_membership:
                active_membership.used_sessions += 1
                db_appointment.membership_id = active_membership.id
                if active_membership.used_sessions >= active_membership.total_sessions:
                    active_membership.is_active = False
            else:
                db_appointment.membership_id = None

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
    db_program.is_active = False
    db.commit()
    return db_program

# --- AVAILABILITY ---
def get_availability(db: Session, target_date: datetime.date):
    """
    Calculates the availability for a specific date based on normal schedules, overrides, and existing appointments.
    Assumes slots of 60 minutes for simplicity.
    """
    # Check overrides
    override = db.query(models.ScheduleOverride).filter(models.ScheduleOverride.override_date == target_date).first()
    
    start_time_str = None
    end_time_str = None
    
    if override:
        if override.is_day_off:
            return []
        start_time_str = override.start_time
        end_time_str = override.end_time
    else:
        # Check regular schedule (0 = Monday, 6 = Sunday)
        day_of_week = target_date.weekday()
        schedules = db.query(models.SpecialistSchedule).filter(
            models.SpecialistSchedule.day_of_week == day_of_week,
            models.SpecialistSchedule.is_active == True
        ).all()
        
        if not schedules:
            return []
            
        # For simplicity, if multiple schedules exist for a day, we just take the first or union them.
        # Here we just take the first one or we can iterate. 
        # Assume one general block per day for Medizen currently.
        sched = schedules[0]
        start_time_str = sched.start_time
        end_time_str = sched.end_time
        
    if not start_time_str or not end_time_str:
        return []

    # Parse times
    start_time_obj = datetime.strptime(start_time_str, "%H:%M").time()
    end_time_obj = datetime.strptime(end_time_str, "%H:%M").time()
    
    # Generate 60-min slots
    from datetime import datetime as dt, timedelta
    
    slots = []
    current = dt.combine(target_date, start_time_obj)
    end = dt.combine(target_date, end_time_obj)
    
    # Fetch existing appointments for the day
    from datetime import time
    start_of_day = dt.combine(target_date, time.min)
    end_of_day = dt.combine(target_date, time.max)
    
    appointments = db.query(models.Appointment).filter(
        models.Appointment.appointment_date >= start_of_day,
        models.Appointment.appointment_date <= end_of_day,
        models.Appointment.status != "Cancelled"
    ).all()
    
    booked_times = [app.appointment_date for app in appointments]
    now = dt.now()

    while current + timedelta(hours=1) <= end:
        slot_start_time = current
        slot_end_time = current + timedelta(hours=1)
        
        # Check if booked
        # Simple match if there's an appointment EXACTLY at this start time
        # Better: if any appointment falls in [slot_start, slot_end)
        is_booked = any(
            slot_start_time <= b_time < slot_end_time for b_time in booked_times
        )
        
        # Check if in past
        is_past = slot_start_time <= now
        
        slots.append({
            "start_time": slot_start_time.strftime("%H:%M"),
            "end_time": slot_end_time.strftime("%H:%M"),
            "is_available": not is_booked and not is_past
        })
        
        current += timedelta(hours=1)
        
    return slots
