"""
Router publico (sin autenticacion) para el formulario de captacion externa.
Recibe los datos del test IEIM de un potencial paciente y los almacena.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from ..database import SessionLocal
from ..models import Patient, IEIMRecord

router = APIRouter(prefix="/public", tags=["public"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CaptureFormData(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
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
def submit_capture_form(form: CaptureFormData, db: Session = Depends(get_db)):
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
