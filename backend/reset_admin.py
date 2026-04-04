import sys
import os

# Agregamos la ruta principal para que encuentre el modulo app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app import auth, crud

def reset_admin():
    db = SessionLocal()
    try:
        user = crud.get_user_by_username(db, "admin")
        if not user:
            print("El usuario admin no existe en la base de datos.")
            return

        user.hashed_password = auth.get_password_hash("adminpassword")
        db.commit()
        print("PASS_RESET_SUCCESS")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin()
