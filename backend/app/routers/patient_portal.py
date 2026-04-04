from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/me",
    tags=["patient portal"],
    dependencies=[Depends(auth.get_current_patient)]
)

@router.get("/", response_model=schemas.Patient)
def read_current_patient_profile(current_patient: models.Patient = Depends(auth.get_current_patient)):
    return current_patient

@router.get("/memberships", response_model=List[schemas.Membership])
def read_current_patient_memberships(db: Session = Depends(get_db), current_patient: models.Patient = Depends(auth.get_current_patient)):
    return crud.get_patient_memberships(db, patient_id=current_patient.id)

@router.get("/appointments", response_model=List[schemas.Appointment])
def read_current_patient_appointments(db: Session = Depends(get_db), current_patient: models.Patient = Depends(auth.get_current_patient)):
    return crud.get_patient_appointments(db, patient_id=current_patient.id)

from datetime import date
from ..email import send_appointment_notification

@router.get("/appointments/availability", response_model=List[schemas.TimeSlot])
def read_availability(target_date: date, db: Session = Depends(get_db)):
    return crud.get_availability(db, target_date)

@router.post("/appointments", response_model=schemas.Appointment)
def create_patient_appointment(appointment: schemas.AppointmentBase, db: Session = Depends(get_db), current_patient: models.Patient = Depends(auth.get_current_patient)):
    # Validate date is not in past
    from datetime import datetime
    if appointment.appointment_date < datetime.now():
        raise HTTPException(status_code=400, detail="Cannot book an appointment in the past")
        
    app_create = schemas.AppointmentCreate(
        patient_id=current_patient.id,
        appointment_date=appointment.appointment_date,
        membership_id=appointment.membership_id,
        notes=appointment.notes,
        status="Scheduled"
    )
    db_app = crud.create_appointment(db, app_create)
    
    # Obtener el nombre de la membresía para el correo
    membership_name = None
    if db_app.membership_id:
        membership = db.query(models.Membership).filter(models.Membership.id == db_app.membership_id).first()
        if membership and membership.plan:
            membership_name = membership.plan.name
            
    # Notificar al administrador
    send_appointment_notification(db, current_patient, db_app.appointment_date, db_app.notes, membership_name)
    
    return db_app
