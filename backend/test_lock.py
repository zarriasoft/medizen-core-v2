from app.database import SessionLocal
from app.crud import acquire_booking_lock
import traceback

def test():
    db = SessionLocal()
    try:
        print("Intentando acquire_booking_lock...")
        lock = acquire_booking_lock(db)
        print(f"Lock obtenido: {lock}")
    except Exception as e:
        print("ERROR CRASH:")
        traceback.print_exc()

if __name__ == "__main__":
    test()
