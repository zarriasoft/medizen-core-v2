from app.database import SessionLocal
from app.crud import get_availability
from datetime import datetime, timedelta

def test():
    db = SessionLocal()
    # Mañana
    target_date = (datetime.now() + timedelta(days=1)).date()
    print(f"Buscando horarios para mañana: {target_date} (Día de la semana: {target_date.weekday()})")

    slots = get_availability(db, target_date)
    print(f"Slots encontrados: {len(slots)}")
    for s in slots:
        print(s)

if __name__ == "__main__":
    test()
