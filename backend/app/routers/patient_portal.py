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

@router.put("/", response_model=schemas.Patient)
def update_current_patient_profile(
    patient_update: schemas.PatientUpdateMe,
    db: Session = Depends(get_db),
    current_patient: models.Patient = Depends(auth.get_current_patient)
):
    update_data = patient_update.dict(exclude_unset=True)
    full_update = schemas.PatientUpdate(**update_data)
    updated = crud.update_patient(db, patient_id=current_patient.id, patient_update=full_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Patient not found")
    return updated


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

    # Verificar que el horario exista en la disponibilidad real del día
    slots = crud.get_availability(db, appointment.appointment_date.date())
    target_time_str = appointment.appointment_date.strftime("%H:%M")
    slot_is_available = any(s["start_time"] == target_time_str and s["is_available"] for s in slots)

    if not slot_is_available:
        raise HTTPException(status_code=400, detail="El horario seleccionado no está disponible en la agenda del especialista.")

    # Acquire lock to serialize appointment creation
    crud.acquire_booking_lock(db)

    if crud.check_appointment_overlap(db, appointment.appointment_date):
        raise HTTPException(status_code=400, detail="Ya existe una cita programada para este horario.")

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
        if membership:
            membership_name = membership.membership_type

    # Notificar al administrador
    send_appointment_notification(db, current_patient, db_app.appointment_date, db_app.notes, membership_name)

    return db_app

@router.put("/appointments/{appointment_id}/cancel", response_model=schemas.Appointment)
def cancel_patient_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_patient: models.Patient = Depends(auth.get_current_patient)
):
    app = crud.get_appointment(db, appointment_id=appointment_id)
    if not app:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if app.patient_id != current_patient.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this appointment")
    if app.status != "Scheduled":
        raise HTTPException(status_code=400, detail="Only scheduled appointments can be cancelled")

    app_update = schemas.AppointmentUpdate(status="Cancelled")
    updated = crud.update_appointment(db, appointment_id=appointment_id, appointment_update=app_update)
    return updated
