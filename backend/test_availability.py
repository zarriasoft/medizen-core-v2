import sys
import os
from datetime import date

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app import crud

def test_avail():
    db = SessionLocal()
    try:
        # Test Friday, March 27, 2026
        target = date(2026, 3, 27)
        slots = crud.get_availability(db, target)
        print("Availability for", target)
        for s in slots:
            print(s)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_avail()
