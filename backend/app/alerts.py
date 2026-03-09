import asyncio
import logging
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .database import SessionLocal
from .models import Patient, IEIMRecord, Membership

logger = logging.getLogger(__name__)

async def simulate_communication(patient: Patient, method: str, subject: str, body: str):
    """
    Simula el envío de un correo electrónico o SMS.
    """
    logger.info(f"--- INICIO DE SIMULACIÓN DE {method.upper()} ---")
    logger.info(f"Para: {patient.first_name} {patient.last_name} ({patient.email} / {patient.phone or 'Sin teléfono'})")
    logger.info(f"Asunto: {subject}")
    logger.info(f"Mensaje:\n{body}")
    logger.info(f"--- FIN DE SIMULACIÓN DE {method.upper()} ---")
    
    # Simular tiempo de red
    await asyncio.sleep(1)


async def run_alerts_check_job():
    """
    Tarea en segundo plano que se ejecuta cada X tiempo para buscar
    pacientes que requieran atencion (IEIM bajo, sin seguimiento, etc).
    """
    while True:
        try:
            logger.info("Ejecutando chequeo automatico de alertas...")
            check_abandonment_risk()
            check_critical_ieim_scores()
            check_expiring_memberships()
            logger.info("Chequeo de alertas finalizado.")
        except Exception as e:
            logger.error(f"Error en el chequeo de alertas: {e}")
        
        # Esperar 24 horas (o 1 minuto para desarrollo)
        # Para pruebas locales, vamos a ejecutarlo cada 60 segundos
        await asyncio.sleep(60)

def check_abandonment_risk():
    db = SessionLocal()
    try:
        # Pacientes activos que no han registrado IEIM en los ultimos 30 dias
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Esta es una consulta basica. En produccion podriamos guardar la alerta en DB.
        patients = db.query(Patient).filter(Patient.is_active == True).all()
        for p in patients:
            last_record = db.query(IEIMRecord).filter(IEIMRecord.patient_id == p.id).order_by(IEIMRecord.record_date.desc()).first()
            if not last_record or last_record.record_date < thirty_days_ago:
                logger.warning(f"ALERTA: Paciente {p.first_name} {p.last_name} (ID: {p.id}) en riesgo de abandono (Sin IEIM reciente).")
                # Simulamos envio de correo recordando llenar el IEIM
                asyncio.create_task(simulate_communication(
                    patient=p,
                    method="email",
                    subject="Recordatorio Importante: Tu Evaluación IEIM Medizen",
                    body=f"Hola {p.first_name}, hemos notado que no has completado tu evaluación IEIM recientemente. Es vital para tu seguimiento."
                ))
    finally:
        db.close()

def check_critical_ieim_scores():
    db = SessionLocal()
    try:
        # Buscar registros recientes con puntaje bajo (< 4.0)
        recent_records = db.query(IEIMRecord).filter(IEIMRecord.overall_score < 4.0).all()
        for record in recent_records:
            logger.warning(f"ALERTA CRITICA: IEIM muy bajo ({record.overall_score}) para paciente ID {record.patient_id}")
            # En vida real avisaríamos al doctor, o al paciente
            p = db.query(Patient).filter(Patient.id == record.patient_id).first()
            if p:
                asyncio.create_task(simulate_communication(
                    patient=p,
                    method="sms",
                    subject="Alerta Clínica: Medizen",
                    body=f"Hola {p.first_name}, tu último registro IEIM requiere atención. El Dr. Usuario se pondrá en contacto pronto."
                ))
    finally:
        db.close()

def check_expiring_memberships():
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        seven_days_from_now = now + timedelta(days=7)
        
        expiring = db.query(Membership).filter(
            Membership.is_active == True,
            Membership.end_date != None,
            Membership.end_date <= seven_days_from_now,
            Membership.end_date >= now
        ).all()
        
        for m in expiring:
            logger.warning(f"ALERTA COMERCIAL: Membresia del paciente ID {m.patient_id} expira el {m.end_date.strftime('%Y-%m-%d')}")
            p = db.query(Patient).filter(Patient.id == m.patient_id).first()
            if p:
                asyncio.create_task(simulate_communication(
                    patient=p,
                    method="whatsapp",
                    subject="Renueva tu Membresía Medizen",
                    body=f"Hola {p.first_name}! Tu membresía está por expirar el {m.end_date.strftime('%Y-%m-%d')}. ¡Aprovecha para renovarla hoy!"
                ))
    finally:
        db.close()
