from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
    dependencies=[Depends(auth.get_current_user)]
)

@router.post("/", response_model=schemas.Appointment)
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    db_patient = crud.get_patient(db, patient_id=appointment.patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return crud.create_appointment(db=db, appointment=appointment)

@router.get("/", response_model=List[schemas.Appointment])
def read_all_appointments(skip: int = 0, limit: int = 10000, db: Session = Depends(get_db)):
    return crud.get_all_appointments(db, skip=skip, limit=limit)

@router.get("/patient/{patient_id}", response_model=List[schemas.Appointment])
def read_patient_appointments(patient_id: int, db: Session = Depends(get_db)):
    return crud.get_patient_appointments(db, patient_id=patient_id)

@router.put("/{appointment_id}", response_model=schemas.Appointment)
def update_appointment(appointment_id: int, appointment: schemas.AppointmentUpdate, db: Session = Depends(get_db)):
    db_appointment = crud.update_appointment(db, appointment_id=appointment_id, appointment_update=appointment)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment

@router.delete("/{appointment_id}", response_model=schemas.Appointment)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db_appointment = crud.delete_appointment(db, appointment_id=appointment_id)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment

@router.post("/{appointment_id}/complete", response_model=schemas.Appointment)
def complete_appointment(appointment_id: int, notes: str = "", db: Session = Depends(get_db)):
    db_appointment = crud.complete_appointment(db, appointment_id=appointment_id, notes=notes)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment
