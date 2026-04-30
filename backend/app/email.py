import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_admin_notification(db, subject: str, html_body: str):
    """
    Sends an email notification to the administrator making a real SMTP connection using DB settings.
    """
    from .models import SystemSettings
    import logging
    logger = logging.getLogger(__name__)

    settings = db.query(SystemSettings).first()

    # Defaults in case settings are entirely empty or missing
    smtp_host = settings.smtp_host if settings and settings.smtp_host else "smtp.gmail.com"
    try:
        smtp_port = int(settings.smtp_port) if settings and settings.smtp_port else 587
    except (ValueError, TypeError):
        smtp_port = 587

    smtp_user = settings.smtp_user if settings and settings.smtp_user else ""
    smtp_password = settings.smtp_password if settings and settings.smtp_password else ""
    admin_email = settings.admin_email if settings and settings.admin_email else ""

    if not smtp_user or not smtp_password or not admin_email:
        logger.warning(f"SKIPPING EMAIL: Missing SMTP credentials. User: {smtp_user}, AdminEmail: {admin_email}")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = admin_email

    msg.attach(MIMEText(html_body, "html"))

    try:
        logger.info(f"Attempting to send admin email via {smtp_host}:{smtp_port}...")
        if smtp_port == 465:
            from smtplib import SMTP_SSL
            with SMTP_SSL(smtp_host, smtp_port, timeout=15) as server:
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        logger.info(f"[OK] Email sent successfully to {admin_email}!")
        return True
    except Exception as e:
        logger.error(f"[ERROR] Failed to send admin email: {str(e)}")
        return False


def send_patient_notification(db, to_email: str, subject: str, html_body: str):
    """
    Sends an email notification to the patient making a real SMTP connection using DB settings.
    """
    from .models import SystemSettings
    import logging
    logger = logging.getLogger(__name__)

    settings = db.query(SystemSettings).first()

    # Defaults in case settings are entirely empty or missing
    smtp_host = settings.smtp_host if settings and settings.smtp_host else "smtp.gmail.com"
    try:
        smtp_port = int(settings.smtp_port) if settings and settings.smtp_port else 587
    except (ValueError, TypeError):
        smtp_port = 587

    smtp_user = settings.smtp_user if settings and settings.smtp_user else ""
    smtp_password = settings.smtp_password if settings and settings.smtp_password else ""

    if not smtp_user or not smtp_password or not to_email:
        logger.warning(f"SKIPPING PATIENT EMAIL: Missing SMTP credentials. To: {to_email}")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email

    msg.attach(MIMEText(html_body, "html"))

    try:
        logger.info(f"Attempting to send patient email via {smtp_host}:{smtp_port}...")
        if smtp_port == 465:
            from smtplib import SMTP_SSL
            with SMTP_SSL(smtp_host, smtp_port, timeout=15) as server:
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        logger.info(f"[OK] Email sent successfully to {to_email}!")
        return True
    except Exception as e:
        logger.error(f"[ERROR] Failed to send patient email: {str(e)}")
        return False


def format_welcome_email(patient_name: str, plan_name: str) -> str:
    """
    Genera el HTML para el correo de bienvenida al paciente tras su inscripción.
    """
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #0d9488;">¡Bienvenido a MediZen, {patient_name}!</h2>
        <p>Hemos recibido exitosamente tu solicitud de inscripción.</p>

        <p style="margin-top: 20px;">
          Has elegido el plan de membresía: <strong style="color: #d97706;">{plan_name}</strong>.
        </p>

        <p>
          Nuestro equipo se pondrá en contacto contigo a la brevedad para coordinar los detalles de pago y activación.
          <br><br>
          Una vez activada tu membresía, podrás acceder al <strong>Portal de Pacientes</strong> para agendar tus horas y revisar tu historial.
        </p>

        <p style="margin-top: 30px;">
          ¡Estamos felices de acompañarte en tu camino hacia el bienestar! <br><br>
          Atentamente,<br>
          <strong>El equipo de MediZen</strong>
        </p>
      </body>
    </html>
    """


def format_new_enrollment_email(patient_data: dict, plan_name: str) -> str:
    """
    Genera el HTML para el correo de notificación de nueva inscripción.
    """
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #0d9488;">¡Nueva Solicitud de Inscripción en MediZen!</h2>
        <p>Un nuevo paciente ha completado el formulario de membresía en el portal de pacientes.</p>

        <table style="border-collapse: collapse; width: 100%; max-width: 600px; margin-top: 20px;">
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8fafc; font-weight: bold; width: 30%;">Nombre:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8fafc; font-weight: bold;">Email:</td>
                <td style="padding: 10px; border: 1px solid #ddd;"><a href="mailto:{patient_data.get('email', '')}">{patient_data.get('email', '')}</a></td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8fafc; font-weight: bold;">Teléfono:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{patient_data.get('phone', 'No indicado')}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8fafc; font-weight: bold;">Plan Seleccionado:</td>
                <td style="padding: 10px; border: 1px solid #ddd; color: #d97706; font-weight: bold;">{plan_name}</td>
            </tr>
        </table>

        <p style="margin-top: 20px;">
          Por favor, ponte en contacto con el paciente a la brevedad para coordinar la firma y el pago de la membresía.<br>
          Recuerda activar su membresía manualmente en el portal Core una vez recibido el pago.
        </p>

        <p style="color: #64748b; font-size: 12px; margin-top: 40px;">
          Este es un correo automático generado por el Sistema Core de MediZen.
        </p>
      </body>
    </html>
    """

def format_new_appointment_email(patient_data: dict, appointment_date: str, notes: str, membership_name: str = None) -> str:
    """
    Genera el HTML para el correo de notificación de nueva cita agendada por el paciente.
    """
    membership_row = ""
    if membership_name:
        membership_row = f"""
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8fafc; font-weight: bold;">Membresía Elegida:</td>
                <td style="padding: 10px; border: 1px solid #ddd; color: #10b981; font-weight: bold;">{membership_name}</td>
            </tr>
        """

    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #0d9488;">¡Nueva Cita Agendada en MediZen!</h2>
        <p>Un paciente ha agendado una nueva sesión desde el portal de autogestión.</p>

        <table style="border-collapse: collapse; width: 100%; max-width: 600px; margin-top: 20px;">
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8fafc; font-weight: bold; width: 30%;">Paciente:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8fafc; font-weight: bold;">Fecha y Hora:</td>
                <td style="padding: 10px; border: 1px solid #ddd; color: #d97706; font-weight: bold;">{appointment_date}</td>
            </tr>
            {membership_row}
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8fafc; font-weight: bold;">Notas:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{notes or 'Sin notas adicionales'}</td>
            </tr>
        </table>

        <p style="margin-top: 20px;">
          Por favor, revisa el portal Core para más detalles.
        </p>
      </body>
    </html>
    """

def send_appointment_notification(db, patient, appointment_date, notes, membership_name: str = None):
    patient_data = {
        "first_name": patient.first_name,
        "last_name": patient.last_name,
    }
    date_str = appointment_date.strftime("%Y-%m-%d %H:%M")
    html_body = format_new_appointment_email(patient_data, date_str, notes, membership_name)
    subject = f"Nueva cita agendada: {patient.first_name} {patient.last_name} ({date_str})"
    return send_admin_notification(db, subject, html_body)
