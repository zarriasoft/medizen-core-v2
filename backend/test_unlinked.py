import os
import datetime
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import User, Appointment, Membership, Patient
from app.auth import get_password_hash

# Set up test client
client = TestClient(app)

def test_unlinked_completion():
    print("Starting unlinked completion test...")
    from app.auth import get_current_user
    app.dependency_overrides[get_current_user] = lambda: {"username": "admin", "role": "admin"}
    
    db = SessionLocal()
    
    # Create patient
    import uuid
    uid = str(uuid.uuid4())[:8]
    patient = Patient(first_name="Test", last_name=f"NoLink_{uid}", email=f"nolink_{uid}@test.com", phone="123")
    db.add(patient)
    db.commit()
    db.refresh(patient)
    
    # 1. Create appointment directly in DB so it bypasses create_appointment logic
    # This simulates a pre-existing old appointment
    appt = Appointment(
        patient_id=patient.id,
        appointment_date=datetime.datetime.now(),
        notes="Unlinked old appt",
        status="Scheduled"
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    
    # 2. Create membership directly in DB
    mem = Membership(
        patient_id=patient.id,
        membership_type="Basica",
        start_date=datetime.datetime.now(),
        total_sessions=1,
        used_sessions=0,
        is_active=True
    )
    db.add(mem)
    db.commit()
    db.refresh(mem)
    
    print(f"Created Patient {patient.id}, Appt {appt.id}, Mem {mem.id}")
    
    # 3. Call complete endpoint
    response = client.post(f"/appointments/{appt.id}/complete", params={"notes": "Finalized"})
    print("Complete Response:", response.status_code)
    
    # 4. Check DB
    db.refresh(appt)
    db.refresh(mem)
    
    print(f"Appt {appt.id}: Status={appt.status}, Membership_id={appt.membership_id}")
    print(f"Mem {mem.id}: Used={mem.used_sessions}, Active={mem.is_active}")
    
    if appt.membership_id == mem.id and mem.used_sessions == 1:
        print("TEST PASSED: Unlinked appointment successfully linked to active membership upon completion.")
    else:
        print("TEST FAILED: Did not link correctly.")

    db.close()

if __name__ == '__main__':
    test_unlinked_completion()
