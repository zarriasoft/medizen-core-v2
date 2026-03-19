from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/programs",
    tags=["programs"],
    dependencies=[Depends(auth.get_current_user)]
)

@router.get("/", response_model=List[schemas.Program])
def read_programs(skip: int = 0, limit: int = 10000, db: Session = Depends(get_db)):
    return crud.get_programs(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.Program)
def create_program(program: schemas.ProgramCreate, db: Session = Depends(get_db)):
    return crud.create_program(db=db, program=program)

@router.put("/{program_id}", response_model=schemas.Program)
def update_program(program_id: int, program_update: schemas.ProgramUpdate, db: Session = Depends(get_db)):
    db_program = crud.update_program(db, program_id=program_id, program_update=program_update)
    if db_program is None:
        raise HTTPException(status_code=404, detail="Program not found")
    return db_program

@router.delete("/{program_id}")
def delete_program(program_id: int, db: Session = Depends(get_db)):
    db_program = crud.delete_program(db, program_id=program_id)
    if db_program is None:
        raise HTTPException(status_code=404, detail="Program not found")
    return {"detail": "Program deactivated successfully"}
