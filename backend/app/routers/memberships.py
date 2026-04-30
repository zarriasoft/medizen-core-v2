from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/memberships",
    tags=["memberships"],
    dependencies=[Depends(auth.get_current_user)]
)

@router.post("/", response_model=schemas.Membership)
def create_membership_for_patient(
    membership: schemas.MembershipCreate, db: Session = Depends(get_db)
):
    # Check if patient exists
    db_patient = crud.get_patient(db, patient_id=membership.patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return crud.create_membership(db=db, membership=membership)

@router.get("/patient/{patient_id}", response_model=List[schemas.Membership])
def read_patient_memberships(patient_id: int, db: Session = Depends(get_db)):
    memberships = crud.get_patient_memberships(db, patient_id=patient_id)
    return memberships

@router.get("/", response_model=List[schemas.MembershipWithPatient])
def read_all_memberships(skip: int = 0, limit: int = 10000, db: Session = Depends(get_db)):
    memberships = crud.get_all_memberships(db, skip=skip, limit=limit)
    return memberships

@router.put("/{membership_id}", response_model=schemas.Membership)
def update_membership(membership_id: int, membership_update: schemas.MembershipUpdate, db: Session = Depends(get_db)):
    db_membership = crud.update_membership(db, membership_id=membership_id, membership_update=membership_update)
    if db_membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")
    return db_membership

@router.delete("/{membership_id}")
def delete_membership(membership_id: int, db: Session = Depends(get_db)):
    db_membership = crud.delete_membership(db, membership_id=membership_id)
    if db_membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")
    return {"detail": "Membership deactivated successfully"}
