
import sys
import os
from sqlalchemy.orm import Session

# Agregamos la ruta principal
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.database import SessionLocal
from app.email import send_admin_notification

def test_app_email():
    db = SessionLocal()
    try:
        print("Probando send_admin_notification desde el codigo de la app...")
        subject = "MediZen App Code Test Email"
        html_body = "<h1>Prueba exitosa</h1><p>Este correo fue enviado usando la funcion interna de la app.</p>"
        result = send_admin_notification(db, subject, html_body)
        if result:
            print("✅ La funcion devolvio True.")
        else:
            print("❌ La funcion devolvio False.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Asegurarse de usar la URL de Neon si queremos probar la nube
    # Pero si queremos probar el codigo local, usamos el default (SQLite)
    test_app_email()
