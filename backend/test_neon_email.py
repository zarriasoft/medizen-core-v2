
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy import create_engine, text

NEON_URL = os.environ.get("DATABASE_URL")
if not NEON_URL:
    print("ERROR: DATABASE_URL no configurada.")
    sys.exit(1)
engine = create_engine(NEON_URL)

def test_neon_email():
    try:
        with engine.connect() as conn:
            row = conn.execute(text("SELECT smtp_host, smtp_port, smtp_user, smtp_password, admin_email FROM system_settings LIMIT 1")).mappings().first()

        if not row:
            print("❌ No hay settings en la base de datos Neon.")
            return

        print(f"Probando conexion SMTP para: {row['smtp_user']}")
        print(f"Host: {row['smtp_host']}:{row['smtp_port']}")

        msg = MIMEMultipart()
        msg['From'] = row['smtp_user']
        msg['To'] = row['admin_email']
        msg['Subject'] = "MediZen Test Email"
        msg.attach(MIMEText("Este es un correo de prueba de MediZen.", 'plain'))

        if row['smtp_port'] == 465:
            server = smtplib.SMTP_SSL(row['smtp_host'], row['smtp_port'], timeout=15)
        else:
            server = smtplib.SMTP(row['smtp_host'], row['smtp_port'], timeout=15)
            server.set_debuglevel(1)
            server.starttls()

        server.login(row['smtp_user'], row['smtp_password'])
        server.send_message(msg)
        server.quit()
        print("✅ ¡Correo de prueba enviado exitosamente!")

    except Exception as e:
        print(f"❌ Error al enviar correo: {e}")

if __name__ == "__main__":
    test_neon_email()
