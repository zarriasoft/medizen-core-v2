import logging
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .database import SessionLocal
from .models import Patient, IEIMRecord, Membership

logger = logging.getLogger(__name__)


def _simulate_communication(patient: Patient, method: str, subject: str, body: str):
    """
    Simula el envio de una comunicacion al paciente (email, SMS, WhatsApp).
    En produccion, aqui se integra Twilio, SendGrid, etc.
    """
    logger.info(f"--- [{method.upper()}] Para: {patient.first_name} {patient.last_name} | {patient.email} ---")
    logger.info(f"  Asunto: {subject}")
    logger.info(f"  Mensaje: {body}")


def check_abandonment_risk():
    """Detecta pacientes sin registro IEIM en los ultimos 30 dias."""
    db: Session = SessionLocal()
    try:
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        patients = db.query(Patient).filter(Patient.is_active == True).all()
        count = 0
        for p in patients:
            last_record = (
                db.query(IEIMRecord)
                .filter(IEIMRecord.patient_id == p.id)
                .order_by(IEIMRecord.record_date.desc())
                .first()
            )
            if not last_record or last_record.record_date < thirty_days_ago:
                count += 1
                logger.warning(
                    f"RIESGO ABANDONO: {p.first_name} {p.last_name} (ID: {p.id}) - Sin IEIM reciente."
                )
                _simulate_communication(
                    patient=p,
                    method="email",
                    subject="Recordatorio: Tu Evaluacion IEIM Medizen",
                    body=(
                        f"Hola {p.first_name}, hace mas de 30 dias que no completas tu evaluacion IEIM. "
                        "Es vital para tu seguimiento de salud. Ingresa a tu portal Medizen."
                    ),
                )
        logger.info(f"Chequeo abandono: {count} paciente(s) en riesgo.")
    except Exception as e:
        logger.error(f"Error en check_abandonment_risk: {e}")
    finally:
        db.close()


def check_critical_ieim_scores():
    """Detecta registros IEIM con puntaje critico (< 4.0)."""
    db: Session = SessionLocal()
    try:
        # Solo registros de los ultimos 7 dias para no re-alertar constantemente
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        critical_records = (
            db.query(IEIMRecord)
            .filter(
                IEIMRecord.overall_score < 4.0,
                IEIMRecord.record_date >= seven_days_ago,
            )
            .all()
        )
        for record in critical_records:
            logger.warning(
                f"IEIM CRITICO: Puntaje {record.overall_score:.1f} para paciente ID {record.patient_id}"
            )
            p = db.query(Patient).filter(Patient.id == record.patient_id).first()
            if p:
                _simulate_communication(
                    patient=p,
                    method="sms",
                    subject="Alerta Clinica Medizen",
                    body=(
                        f"Hola {p.first_name}, tu ultimo registro IEIM ({record.overall_score:.1f}/10) "
                        "indica que necesitas atencion. Tu especialista revisara tu caso pronto."
                    ),
                )
        logger.info(f"Chequeo IEIM critico: {len(critical_records)} registro(s) critico(s).")
    except Exception as e:
        logger.error(f"Error en check_critical_ieim_scores: {e}")
    finally:
        db.close()


def check_expiring_memberships():
    """Detecta membresias que vencen en los proximos 7 dias."""
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        seven_days_from_now = now + timedelta(days=7)

        expiring = (
            db.query(Membership)
            .filter(
                Membership.is_active == True,
                Membership.end_date != None,
                Membership.end_date <= seven_days_from_now,
                Membership.end_date >= now,
            )
            .all()
        )

        for m in expiring:
            logger.warning(
                f"MEMBRESIA POR VENCER: Paciente ID {m.patient_id} - Vence {m.end_date.strftime('%Y-%m-%d')}"
            )
            p = db.query(Patient).filter(Patient.id == m.patient_id).first()
            if p:
                _simulate_communication(
                    patient=p,
                    method="whatsapp",
                    subject="Tu Membresia Medizen esta por vencer",
                    body=(
                        f"Hola {p.first_name}! Tu membresia vence el {m.end_date.strftime('%d/%m/%Y')}. "
                        "Comunicate con nosotros para renovarla y seguir disfrutando tus beneficios."
                    ),
                )
        logger.info(f"Chequeo membresias: {len(expiring)} membresia(s) por vencer.")
    except Exception as e:
        logger.error(f"Error en check_expiring_memberships: {e}")
    finally:
        db.close()


def run_daily_alerts():
    """
    Funcion principal del scheduler. Ejecuta todos los chequeos diarios.
    Llamada por APScheduler cada 24 horas.
    """
    logger.info("=" * 50)
    logger.info("INICIANDO CHEQUEO DIARIO DE ALERTAS MEDIZEN")
    logger.info("=" * 50)
    check_abandonment_risk()
    check_critical_ieim_scores()
    check_expiring_memberships()
    logger.info("CHEQUEO DIARIO FINALIZADO.")
