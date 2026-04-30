import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import SpecialistSchedule

def seed_schedules():
    db = SessionLocal()
    try:
        # Check if there are any schedules already
        existing = db.query(SpecialistSchedule).count()
        if existing > 0:
            print("Schedules already exist. Skipping seed.")
            return

        # Create Mon-Fri (0-4) from 09:00 to 18:00
        for day in range(5):
            sched = SpecialistSchedule(
                day_of_week=day,
                start_time="09:00",
                end_time="18:00",
                is_active=True
            )
            db.add(sched)

        db.commit()
        print("Successfully seeded Monday-Friday 09:00 to 18:00 schedules.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_schedules()
