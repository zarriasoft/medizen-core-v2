from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from .. import schemas, models, crud, auth
from ..database import get_db

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    dependencies=[Depends(auth.get_current_user)]
)

@router.get("/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    total_patients = db.query(models.Patient).filter(models.Patient.is_active == True).count()
    
    # Calcular promedio IEIM general basico
    records = db.query(models.IEIMRecord).all()
    avg_ieim = 0
    if records:
        avg_ieim = sum([r.overall_score for r in records]) / len(records)
        avg_ieim = round(avg_ieim, 1)

    # Sesiones hoy (Citas)
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    sessions_today = db.query(models.Appointment).filter(
        models.Appointment.appointment_date >= today_start,
        models.Appointment.appointment_date < today_end
    ).count()

    # Riesgo abandono (pacientes sin IEIM > 30 dias)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    risk_count = 0
    active_patients = db.query(models.Patient).filter(models.Patient.is_active == True).all()
    for p in active_patients:
        last = db.query(models.IEIMRecord).filter(models.IEIMRecord.patient_id == p.id).order_by(models.IEIMRecord.record_date.desc()).first()
        if not last or last.record_date < thirty_days_ago:
            risk_count += 1

    return {
        "active_patients": total_patients,
        "avg_ieim_score": avg_ieim,
        "sessions_today": sessions_today, 
        "abandonment_risk": risk_count
    }

@router.get("/alerts")
def get_dashboard_alerts(db: Session = Depends(get_db)):
    alerts = []
    
    # Riesgo Abandono
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_patients = db.query(models.Patient).filter(models.Patient.is_active == True).all()
    for p in active_patients:
        last = db.query(models.IEIMRecord).filter(models.IEIMRecord.patient_id == p.id).order_by(models.IEIMRecord.record_date.desc()).first()
        if not last:
            alerts.append({"type": "warning", "message": f"{p.first_name} {p.last_name} no tiene registros IEIM."})
        elif last.record_date < thirty_days_ago:
            alerts.append({"type": "warning", "message": f"{p.first_name} {p.last_name} sin evaluación IEIM desde {last.record_date.strftime('%Y-%m-%d')}."})

    # IEIM Critico
    recent_records = db.query(models.IEIMRecord).filter(models.IEIMRecord.overall_score < 4.0).all()
    for r in recent_records:
        p = db.query(models.Patient).filter(models.Patient.id == r.patient_id).first()
        if p:
            alerts.append({"type": "critical", "message": f"IEIM crítico ({r.overall_score}) reportado para {p.first_name} {p.last_name}."})

    # Membresias por expirar
    now = datetime.utcnow()
    seven_days = now + timedelta(days=7)
    expiring = db.query(models.Membership).filter(
        models.Membership.is_active == True,
        models.Membership.end_date != None,
        models.Membership.end_date <= seven_days,
        models.Membership.end_date >= now
    ).all()
    
    for m in expiring:
        p = db.query(models.Patient).filter(models.Patient.id == m.patient_id).first()
        if p:
            alerts.append({"type": "info", "message": f"Membresía de {p.first_name} {p.last_name} expira el {m.end_date.strftime('%Y-%m-%d')}."})

    return alerts
