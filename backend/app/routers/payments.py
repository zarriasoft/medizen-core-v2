"""
Router de pagos con estructura preparada para integracion WebPay/Transbank.
Modo mock para desarrollo; modo produccion requiere credenciales de Transbank.
"""
import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from .. import crud, models, auth
from ..database import get_db

router = APIRouter(prefix="/payments", tags=["payments"])

MOCK_MODE = os.getenv("TRANSBANK_ENV") != "production"


class PaymentInitRequest(BaseModel):
    membership_id: int
    amount: float
    return_url: str = ""


class PaymentInitResponse(BaseModel):
    payment_id: int
    redirect_url: str
    token: str


class WebhookPayload(BaseModel):
    token: str
    status: str
    transaction_id: Optional[str] = None


@router.post("/init", response_model=PaymentInitResponse, dependencies=[Depends(auth.get_current_user)])
def init_payment(data: PaymentInitRequest, db: Session = Depends(get_db)):
    """
    Inicia un flujo de pago via WebPay/Transbank.
    En modo mock devuelve una URL simulada.
    """
    membership = crud.get_membership(db, data.membership_id)
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")

    payment = models.Payment(
        patient_id=membership.patient_id,
        membership_id=data.membership_id,
        amount=data.amount,
        status="pending",
        transaction_id=str(uuid.uuid4()),
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    if MOCK_MODE:
        token = f"mock_token_{payment.id}"
        redirect_url = f"{data.return_url}?token_ws={token}"
    else:
        # TODO: Integrar con Transbank SDK
        # from transbank.webpay.webpay_plus.transaction import Transaction
        # resp = Transaction().create(
        #     buy_order=str(payment.id),
        #     session_id=str(membership.patient_id),
        #     amount=data.amount,
        #     return_url=data.return_url
        # )
        # token = resp['token']
        # redirect_url = resp['url'] + '?token_ws=' + token
        token = f"tbk_token_{payment.id}"
        redirect_url = f"{data.return_url}?token_ws={token}"

    payment.transaction_id = token
    db.commit()

    return PaymentInitResponse(
        payment_id=payment.id,
        redirect_url=redirect_url,
        token=token,
    )


@router.post("/confirm")
def confirm_payment(token: str, db: Session = Depends(get_db)):
    """
    Confirma el resultado de un pago (callback de Transbank o mock).
    Activa la membresia si el pago es exitoso.
    """
    payment = (
        db.query(models.Payment)
        .filter(models.Payment.transaction_id == token)
        .first()
    )
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if MOCK_MODE:
        payment.status = "completed"
        payment.completed_at = datetime.utcnow()
    else:
        # TODO: Confirmar con Transbank
        # from transbank.webpay.webpay_plus.transaction import Transaction
        # resp = Transaction().commit(token)
        # if resp['status'] == 'AUTHORIZED':
        #     payment.status = 'completed'
        # else:
        #     payment.status = 'failed'
        payment.status = "completed"
        payment.completed_at = datetime.utcnow()

    db.commit()

    if payment.status == "completed" and payment.membership_id:
        membership = crud.get_membership(db, payment.membership_id)
        if membership:
            membership.is_active = True
            db.commit()

    return {"status": payment.status, "payment_id": payment.id}


@router.get("/{payment_id}", dependencies=[Depends(auth.get_current_user)])
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {
        "id": payment.id,
        "patient_id": payment.patient_id,
        "membership_id": payment.membership_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "status": payment.status,
        "created_at": payment.created_at.isoformat() if payment.created_at else None,
        "completed_at": payment.completed_at.isoformat() if payment.completed_at else None,
    }


@router.get("/patient/{patient_id}", dependencies=[Depends(auth.get_current_user)])
def get_patient_payments(patient_id: int, db: Session = Depends(get_db)):
    payments = (
        db.query(models.Payment)
        .filter(models.Payment.patient_id == patient_id)
        .order_by(models.Payment.created_at.desc())
        .all()
    )
    return [
        {
            "id": p.id,
            "membership_id": p.membership_id,
            "amount": p.amount,
            "currency": p.currency,
            "status": p.status,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in payments
    ]
