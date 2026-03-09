from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/patients",
    tags=["patients"],
    dependencies=[Depends(auth.get_current_user)]
)

@router.post("/", response_model=schemas.Patient)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    db_patient = crud.get_patient_by_email(db, email=patient.email)
    if db_patient:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_patient(db=db, patient=patient)

@router.get("/", response_model=List[schemas.Patient])
def read_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_patients(db, skip=skip, limit=limit)

@router.get("/{patient_id}", response_model=schemas.Patient)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@router.post("/{patient_id}/ieim/", response_model=schemas.IEIMRecord)
def create_record_for_patient(
    patient_id: int, ieim_record: schemas.IEIMRecordCreate, db: Session = Depends(get_db)
):
    if ieim_record.patient_id != patient_id:
        raise HTTPException(status_code=400, detail="Patient ID mismatch")
    
    # Check if patient exists
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    return crud.create_ieim_record(db=db, ieim_record=ieim_record)

@router.get("/{patient_id}/ieim/", response_model=List[schemas.IEIMRecord])
def read_ieim_records(patient_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    records = crud.get_patient_ieim_records(db, patient_id=patient_id, skip=skip, limit=limit)
    return records

@router.put("/{patient_id}", response_model=schemas.Patient)
def update_patient(patient_id: int, patient_update: schemas.PatientUpdate, db: Session = Depends(get_db)):
    db_patient = crud.update_patient(db, patient_id=patient_id, patient_update=patient_update)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@router.delete("/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud.delete_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"detail": "Patient deactivated successfully"}
