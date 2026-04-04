import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app import auth
from app.models import Patient

def set_all_passwords():
    db = SessionLocal()
    try:
        patients = db.query(Patient).all()
        default_password = "medizen123"
        hashed = auth.get_password_hash(default_password)
        
        count = 0
        for p in patients:
            if not p.hashed_password:
                p.hashed_password = hashed
                count += 1
            
        db.commit()
        print(f"PASS_SET_SUCCESS: Se asigno contrasena a {count} paciente(s) sin credenciales.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    set_all_passwords()
