from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List

from .. import schemas, models, crud, auth
from ..database import get_db
from ..models import MembershipPlan

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

@router.get("/ieim-history")
def get_ieim_history(db: Session = Depends(get_db)):
    # Group by month/year in Python to support both SQLite and PostgreSQL
    records = db.query(models.IEIMRecord.record_date, models.IEIMRecord.overall_score).all()

    history_dict = {}
    for r in records:
        if r.record_date and r.overall_score is not None:
            month_str = r.record_date.strftime('%Y-%m')
            if month_str not in history_dict:
                history_dict[month_str] = []
            history_dict[month_str].append(r.overall_score)

    history = []
    for month_str in sorted(history_dict.keys()):
        scores = history_dict[month_str]
        avg_score = sum(scores) / len(scores) if scores else 0
        history.append({
            "name": month_str,
            "score": round(avg_score, 1)
        })

    return history


@router.get("/analytics")
def get_advanced_analytics(db: Session = Depends(get_db)):
    """Metricas avanzadas: retencion, tendencias, ingresos."""
    now = datetime.utcnow()

    # Pacientes activos por mes (ultimos 6 meses)
    monthly_patients = []
    for i in range(5, -1, -1):
        month_start = (now.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        count = db.query(models.Patient).filter(
            models.Patient.created_at < month_end,
            models.Patient.is_active == True
        ).count()
        monthly_patients.append({
            "month": month_start.strftime("%Y-%m"),
            "active_patients": count
        })

    # IEIM promedio por mes (ultimos 6 meses)
    ieim_trend = []
    for i in range(5, -1, -1):
        month_start = (now.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        records = db.query(models.IEIMRecord).filter(
            models.IEIMRecord.record_date >= month_start,
            models.IEIMRecord.record_date < month_end
        ).all()
        avg = round(sum(r.overall_score for r in records) / len(records), 1) if records else 0
        ieim_trend.append({"month": month_start.strftime("%Y-%m"), "avg_ieim": avg})

    # Ingresos estimados (membresias activas * precio del plan)
    active_memberships = db.query(models.Membership).filter(
        models.Membership.is_active == True
    ).all()
    estimated_revenue = 0
    membership_distribution = {}
    for m in active_memberships:
        plan = db.query(models.MembershipPlan).filter(
            models.MembershipPlan.name == m.membership_type
        ).first()
        if plan:
            try:
                price = float(plan.price.replace("$", "").replace(".", "").replace(",", ""))
            except (ValueError, AttributeError):
                price = 0
            estimated_revenue += price
            membership_distribution[plan.name] = membership_distribution.get(plan.name, 0) + 1

    # Tasa de retencion (pacientes con IEIM en ultimos 60 dias / total activos)
    sixty_days_ago = now - timedelta(days=60)
    active_patients = db.query(models.Patient).filter(models.Patient.is_active == True).count()
    active_with_recent_ieim = db.query(models.IEIMRecord.patient_id).filter(
        models.IEIMRecord.record_date >= sixty_days_ago
    ).distinct().count()
    retention_rate = round(active_with_recent_ieim / active_patients * 100, 1) if active_patients > 0 else 0

    return {
        "monthly_patients": monthly_patients,
        "ieim_trend": ieim_trend,
        "estimated_monthly_revenue": estimated_revenue,
        "membership_distribution": membership_distribution,
        "retention_rate": retention_rate,
        "total_appointments": db.query(models.Appointment).count(),
        "completed_appointments": db.query(models.Appointment).filter(
            models.Appointment.status == "Completed"
        ).count(),
        "total_payments": db.query(models.Payment).filter(
            models.Payment.status == "completed"
        ).count(),
        "pending_payments": db.query(models.Payment).filter(
            models.Payment.status == "pending"
        ).count(),
    }
