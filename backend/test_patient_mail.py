from app.database import SessionLocal
from app.email import send_patient_notification, format_welcome_email

db = SessionLocal()
try:
    patient_html = format_welcome_email("Prueba Paciente", "Premium")
    send_patient_notification(db, to_email="zarria@gmail.com", subject="Test Envío a Paciente", html_body=patient_html)
    print("Test local script completado.")
finally:
    db.close()
