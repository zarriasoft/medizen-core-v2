from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

import sys
sys.path.append('c:/Medizen/v2/backend')
from app.models import Patient
import app.models as models
from app.database import Base

engine = create_engine('sqlite:///C:/Medizen/v2/backend/medizen_core.db', connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    patient = Patient(
        first_name="Test",
        last_name="Test",
        email="test_dateofbirth@gmail.com",
        phone="123",
        date_of_birth="2026-02-24",
        created_at=datetime.utcnow(),
        is_active=True,
    )
    db.add(patient)
    db.commit()
    print("Success")
except Exception as e:
    print(f"Failed with exception: {type(e).__name__}: {e}")
finally:
    db.rollback()
    db.close()
