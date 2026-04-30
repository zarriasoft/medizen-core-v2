import sys
import os

# Asegurar que los modulos de app se puedan importar
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Patient
from app.auth import get_password_hash

def reset_password(email="zarria@gmail.com", new_pass="123456"):
    db = SessionLocal()
    patient = db.query(Patient).filter(Patient.email == email).first()

    if not patient:
        print(f"[-] El usuario {email} NO existia en tu base de datos local.")
        print("[+] Creando la cuenta ahora mismo...")
        patient = Patient(email=email, first_name="Zarria", hashed_password=get_password_hash(new_pass))
        db.add(patient)
    else:
        patient.hashed_password = get_password_hash(new_pass)
        print(f"[+] Usuario encontrado. Clave de {email} reseteada exitosamente.")

    db.commit()
    print(f"==========================================")
    print(f"¡Listo! Ahora puedes entrar al portal.")
    print(f"Correo: {email}")
    print(f"Clave:  {new_pass}")
    print(f"==========================================")

if __name__ == "__main__":
    reset_password()
