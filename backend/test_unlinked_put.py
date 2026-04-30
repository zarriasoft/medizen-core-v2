import os
import datetime
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import User, Appointment, Membership, Patient
from app.auth import get_password_hash

client = TestClient(app)

def test_put_completion():
    print("Starting PUT completion test...")
    from app.auth import get_current_user
    app.dependency_overrides[get_current_user] = lambda: {"username": "admin", "role": "admin"}

    db = SessionLocal()

    import uuid
    uid = str(uuid.uuid4())[:8]
    patient = Patient(first_name="Test", last_name=f"NoLinkPUT_{uid}", email=f"nolinkput_{uid}@test.com", phone="123")
    db.add(patient)
    db.commit()
    db.refresh(patient)

    appt = Appointment(
        patient_id=patient.id,
        appointment_date=datetime.datetime.now(),
        notes="Unlinked old appt",
        status="Scheduled"
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)

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

    # CALL PUT ENDPOINT
    response = client.put(f"/appointments/{appt.id}", json={"status": "Completed"})
    print("PUT Response:", response.status_code)

    db.refresh(appt)
    db.refresh(mem)

    print(f"Appt {appt.id}: Status={appt.status}, Membership_id={appt.membership_id}")
    print(f"Mem {mem.id}: Used={mem.used_sessions}, Active={mem.is_active}")

    if appt.membership_id == mem.id and mem.used_sessions == 1:
        print("TEST PASSED!")
    else:
        print("TEST FAILED: Did not link correctly with PUT request.")

    db.close()

if __name__ == '__main__':
    test_put_completion()
