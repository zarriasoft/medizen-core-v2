"""
Router publico (sin autenticacion) para el formulario de captacion externa.
Recibe los datos del test IEIM de un potencial paciente y los almacena.
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from ..database import SessionLocal, get_db
from ..models import Patient, IEIMRecord
from ..limiter import limiter

router = APIRouter(prefix="/public", tags=["public"])


class CaptureFormData(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    # Puntuaciones IEIM del test (1-10)
    pain_level: float
    sleep_quality: float
    energy_level: float
    stress_anxiety: float
    mobility: float
    inflammation: float


class CaptureFormResponse(BaseModel):
    message: str
    overall_score: float
    classification: str
    recommendation: str


def _calculate_ieim(data: CaptureFormData) -> float:
    """Calcula el score IEIM global (promedio de 6 variables)."""
    scores = [
        data.pain_level,
        data.sleep_quality,
        data.energy_level,
        data.stress_anxiety,
        data.mobility,
        data.inflammation,
    ]
    return round(sum(scores) / len(scores), 2)


def _classify_ieim(score: float) -> tuple[str, str]:
    """Retorna (clasificacion, recomendacion) segun el puntaje."""
    if score >= 8.0:
        return (
            "Equilibrio Optimo 🟢",
            "Tu indice de equilibrio es excelente. Te recomendamos sesiones de mantenimiento para sostenerte.",
        )
    elif score >= 6.0:
        return (
            "Equilibrio Moderado 🟡",
            "Hay areas de mejora. Un programa de 10 sesiones podria llevar tu bienestar al siguiente nivel.",
        )
    elif score >= 4.0:
        return (
            "Desequilibrio Leve 🟠",
            "Tu cuerpo necesita atencion. Te sugerimos comenzar con un programa intensivo de recuperacion.",
        )
    else:
        return (
            "Desequilibrio Critico 🔴",
            "Tu nivel de bienestar es critico. Te contactaremos a la brevedad para coordinar una evaluacion urgente.",
        )


@router.post("/capture", response_model=CaptureFormResponse)
@limiter.limit("3/minute")
def submit_capture_form(request: Request, form: CaptureFormData, db: Session = Depends(get_db)):
    """
    Endpoint publico que recibe el test IEIM de captacion.
    Crea al paciente si no existe, guarda el registro IEIM y devuelve su resultado.
    """
    overall_score = _calculate_ieim(form)
    classification, recommendation = _classify_ieim(overall_score)

    # Crear paciente si no existe aun (por email)
    patient = db.query(Patient).filter(Patient.email == form.email).first()
    if not patient:
        patient = Patient(
            first_name=form.first_name,
            last_name=form.last_name,
            email=form.email,
            phone=form.phone,
            address=form.address,
            created_at=datetime.utcnow(),
            is_active=True,
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)

    # Guardar el registro IEIM
    ieim_record = IEIMRecord(
        patient_id=patient.id,
        record_date=datetime.utcnow(),
        pain_level=form.pain_level,
        sleep_quality=form.sleep_quality,
        energy_level=form.energy_level,
        stress_anxiety=form.stress_anxiety,
        mobility=form.mobility,
        inflammation=form.inflammation,
        overall_score=overall_score,
    )
    db.add(ieim_record)
    db.commit()

    return CaptureFormResponse(
        message=f"Gracias {form.first_name}, hemos recibido tu evaluacion.",
        overall_score=overall_score,
        classification=classification,
        recommendation=recommendation,
    )


class EnrollRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[str] = None
    plan_name: str

class EnrollResponse(BaseModel):
    message: str

@router.post("/enroll", response_model=EnrollResponse)
def enroll_patient(form: EnrollRequest, db: Session = Depends(get_db)):
    from ..models import Membership
    from ..email import send_admin_notification, format_new_enrollment_email
    import logging

    parsed_dob = None
    if form.date_of_birth:
        try:
            # HTML5 date inputs send data in YYYY-MM-DD format
            parsed_dob = datetime.strptime(form.date_of_birth, "%Y-%m-%d").date()
        except ValueError:
            pass

    # Check if patient exists
    patient = db.query(Patient).filter(Patient.email == form.email).first()
    if not patient:
        from ..auth import get_password_hash
        patient = Patient(
            first_name=form.first_name,
            last_name=form.last_name,
            email=form.email,
            hashed_password=get_password_hash(form.password),
            phone=form.phone,
            address=form.address,
            date_of_birth=parsed_dob,
            created_at=datetime.utcnow(),
            is_active=True,
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
    else:
        # Update details if provided
        from ..auth import get_password_hash
        if not patient.hashed_password:
            patient.hashed_password = get_password_hash(form.password)
        if form.phone and not patient.phone:
            patient.phone = form.phone
        if form.address and not patient.address:
            patient.address = form.address
        if parsed_dob and not patient.date_of_birth:
            patient.date_of_birth = parsed_dob
        db.commit()

    from app import crud
    plan = crud.get_membership_plan_by_name(db, form.plan_name)
    sessions = plan.total_sessions if plan and plan.total_sessions else 1

    # Create membership record based on user requirement
    membership = Membership(
        patient_id=patient.id,
        membership_type=form.plan_name,
        start_date=datetime.utcnow(),
        end_date=None, # left blank intentionally
        total_sessions=sessions, # from the configured plan parameter
        used_sessions=0,
        is_active=False # inactive status (pending payment)
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)

    from ..models import Payment
    amount_str = plan.price.replace("$", "").replace(".", "").replace(",", "") if plan and plan.price else "0"
    try:
        amount = float(amount_str)
    except ValueError:
        amount = 0.0

    payment = Payment(
        patient_id=patient.id,
        membership_id=membership.id,
        amount=amount,
        status="pending"
    )
    db.add(payment)
    db.commit()

    # --- EMAIL NOTIFICATION INTEGRATION ---
    try:
        from ..email import send_patient_notification, format_welcome_email
        patient_data = {
            "first_name": form.first_name,
            "last_name": form.last_name,
            "email": form.email,
            "phone": form.phone or "No indicado"
        }

        # 1. Notify Admin
        email_html = format_new_enrollment_email(patient_data, form.plan_name)
        subject = f"🔔 Nueva Solicitud de Inscripción: {form.first_name} {form.last_name} ({form.plan_name})"
        send_admin_notification(db=db, subject=subject, html_body=email_html)

        # 2. Notify Patient
        patient_html = format_welcome_email(form.first_name, form.plan_name)
        patient_subject = "¡Bienvenido a MediZen! Confirmación de inscripción"
        send_patient_notification(db=db, to_email=form.email, subject=patient_subject, html_body=patient_html)

    except Exception as e:
        logging.error(f"Error al enviar la notificación por correo: {repr(e)}")
        # Proceed anyway as the patient data was saved successfully
    # --------------------------------------

    return EnrollResponse(
        message=f"Inscripción recibida. Nos pondremos en contacto a la brevedad."
    )
