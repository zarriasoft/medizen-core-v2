import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Patient

def list_patients():
    db = SessionLocal()
    try:
        patients = db.query(Patient).all()
        print("Total pacientes:", len(patients))
        for p in patients:
            print(f"- {p.email}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_patients()
