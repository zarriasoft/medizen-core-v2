from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/membership-plans",
    tags=["membership-plans"]
)

@router.get("/", response_model=List[schemas.MembershipPlan])
def read_membership_plans(skip: int = 0, limit: int = 10000, db: Session = Depends(get_db)):
    plans = crud.get_membership_plans(db, skip=skip, limit=limit)
    return plans

@router.post("/", response_model=schemas.MembershipPlan, dependencies=[Depends(auth.get_current_user)])
def create_membership_plan(plan: schemas.MembershipPlanCreate, db: Session = Depends(get_db)):
    return crud.create_membership_plan(db=db, plan=plan)

@router.put("/{plan_id}", response_model=schemas.MembershipPlan, dependencies=[Depends(auth.get_current_user)])
def update_membership_plan(plan_id: int, plan_update: schemas.MembershipPlanUpdate, db: Session = Depends(get_db)):
    db_plan = crud.update_membership_plan(db, plan_id=plan_id, plan_update=plan_update)
    if db_plan is None:
        raise HTTPException(status_code=404, detail="Membership plan not found")
    return db_plan

@router.delete("/{plan_id}", dependencies=[Depends(auth.get_current_user)])
def delete_membership_plan(plan_id: int, db: Session = Depends(get_db)):
    db_plan = crud.delete_membership_plan(db, plan_id=plan_id)
    if db_plan is None:
        raise HTTPException(status_code=404, detail="Membership plan not found")
    if isinstance(db_plan, dict) and "error" in db_plan:
        raise HTTPException(status_code=400, detail=db_plan["error"])
    return {"detail": "Membership plan deactivated successfully"}
