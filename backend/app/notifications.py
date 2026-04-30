"""
Sistema de notificaciones en tiempo real (WebSocket) y recordatorios automaticos.
"""
import logging
import socketio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Patient, Appointment

logger = logging.getLogger("medizen.notifications")

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=False,
    engineio_logger=False,
)


def get_sio():
    return sio


async def notify_patient(patient_id: int, event: str, data: dict):
    """Envia notificacion a un paciente especifico via WebSocket."""
    room = f"patient_{patient_id}"
    await sio.emit(event, data, room=room)
    logger.info(f"Notificacion enviada a patient_{patient_id}: {event} -> {data}")


@sio.event
async def connect(sid, environ, auth):
    logger.info(f"WebSocket conectado: {sid}")


@sio.event
async def join_patient_room(sid, data):
    patient_id = data.get("patient_id")
    if patient_id:
        room = f"patient_{patient_id}"
        sio.enter_room(sid, room)
        logger.info(f"Cliente {sid} se unio a room patient_{patient_id}")
        await sio.emit("joined", {"room": room}, to=sid)


@sio.event
async def disconnect(sid):
    logger.info(f"WebSocket desconectado: {sid}")


# --- RECORDATORIOS DE CITAS ---


def check_upcoming_appointments():
    """
    Detecta citas programadas para las proximas 24 horas
    y envia recordatorios por email + WebSocket.
    """
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        in_24h = now + timedelta(hours=24)

        upcoming = (
            db.query(Appointment)
            .filter(
                Appointment.status == "Scheduled",
                Appointment.appointment_date >= now,
                Appointment.appointment_date <= in_24h,
            )
            .all()
        )

        for appointment in upcoming:
            patient = (
                db.query(Patient)
                .filter(Patient.id == appointment.patient_id)
                .first()
            )
            if not patient:
                continue

            date_str = appointment.appointment_date.strftime("%d/%m/%Y a las %H:%M")

            # Email recordatorio
            _send_appointment_reminder_email(patient, appointment, date_str)

            # WebSocket (se enviara si el paciente esta conectado)
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.ensure_future(
                        notify_patient(
                            patient.id,
                            "appointment_reminder",
                            {
                                "title": "Recordatorio de Cita",
                                "message": f"Tienes una cita manana {date_str}",
                                "appointment_id": appointment.id,
                                "date": appointment.appointment_date.isoformat(),
                            },
                        )
                    )
            except RuntimeError:
                pass

            logger.info(
                f"Recordatorio enviado: {patient.first_name} {patient.last_name} - Cita {date_str}"
            )

        logger.info(f"Recordatorios de citas: {len(upcoming)} cita(s) en las proximas 24h.")
    except Exception as e:
        logger.error(f"Error en check_upcoming_appointments: {e}")
    finally:
        db.close()


def _send_appointment_reminder_email(patient, appointment, date_str):
    """Envia email de recordatorio de cita usando el sistema SMTP existente."""
    try:
        from .email import send_patient_notification

        html_body = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px">
            <h2 style="color:#0d9488">Recordatorio de Cita - MediZen</h2>
            <p>Hola <strong>{patient.first_name}</strong>,</p>
            <p>Te recordamos que tienes una cita programada para:</p>
            <div style="background:#f0fdfa;border:1px solid #0d9488;border-radius:8px;padding:15px;margin:20px 0">
                <p style="font-size:18px;margin:0"><strong>Fecha:</strong> {date_str}</p>
            </div>
            <p>Si necesitas reagendar, contactanos o ingresa a tu portal.</p>
            <p style="color:#64748b;font-size:12px">MediZen - Bienestar Integral</p>
        </div>
        """

        send_patient_notification(
            db=None,
            to_email=patient.email,
            subject=f"Recordatorio de Cita - {date_str}",
            html_body=html_body,
        )
    except Exception as e:
        logger.warning(f"No se pudo enviar email de recordatorio a {patient.email}: {e}")
