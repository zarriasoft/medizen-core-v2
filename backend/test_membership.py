import os
import datetime
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import User
from app.auth import get_password_hash

# Set up test client
client = TestClient(app)

def test_membership_tracking():
    print("Starting tests...")

    # Needs a token to access endpoints. We will create a fresh user and get connection token or override deps.
    # To keep it simple, we just override get_current_user

    from app.auth import get_current_user
    app.dependency_overrides[get_current_user] = lambda: {"username": "admin", "role": "admin"}

    # 2. Get first patient or create one
    import uuid
    unique_ext = str(uuid.uuid4())[:8]
    print("Creating a unique test patient")
    response = client.post("/patients", json={
        "first_name": "Test",
        "last_name": f"Patient_{unique_ext}",
        "email": f"test_{unique_ext}@example.com",
        "phone": "12345678"
    })
    patient_id = response.json()["id"]
    print(f"Using patient_id: {patient_id}")

    # 3. Create a membership for patient
    membership_data = {
        "patient_id": patient_id,
        "membership_type": "TEST_AUTO_TRACKING",
        "start_date": datetime.datetime.now().isoformat(),
        "total_sessions": 2,
        "used_sessions": 0,
        "is_active": True
    }
    response = client.post("/memberships", json=membership_data)
    membership = response.json()
    membership_id = membership["id"]
    print(f"Created membership {membership_id} with 0/2 used sessions")

    # 4. Schedule appointment 1
    appt_data = {
        "patient_id": patient_id,
        "appointment_date": (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat(),
        "notes": "Test Appt 1",
        "status": "Scheduled"
    }
    response = client.post("/appointments", json=appt_data)
    appt1 = response.json()

    from app.database import SessionLocal
    from app.models import Membership

    def get_membership_from_db(mem_id):
        db = SessionLocal()
        mem = db.query(Membership).filter(Membership.id == mem_id).first()
        db.close()
        return mem

    # Verify membership consumed NOTHING yet
    mem_check = get_membership_from_db(membership_id)
    print(f"After Schedule Appt 1 -> Used Sessions: {mem_check.used_sessions}, Active: {mem_check.is_active}")
    assert mem_check.used_sessions == 0
    assert mem_check.is_active == True

    # Complete appointment 1
    response = client.post(f"/appointments/{appt1['id']}/complete", params={"notes": "Done"})
    mem_check = get_membership_from_db(membership_id)
    print(f"After Complete Appt 1 -> Used Sessions: {mem_check.used_sessions}, Active: {mem_check.is_active}")
    assert mem_check.used_sessions == 1
    assert mem_check.is_active == True

    # 5. Schedule appointment 2
    appt_data["notes"] = "Test Appt 2"
    response = client.post("/appointments", json=appt_data)
    appt2 = response.json()

    # Complete appointment 2
    response = client.post(f"/appointments/{appt2['id']}/complete", params={"notes": "Done"})

    # Verify membership consumed 2 and deactivated
    mem_check = get_membership_from_db(membership_id)
    print(f"After Complete Appt 2 -> Used Sessions: {mem_check.used_sessions}, Active: {mem_check.is_active}")
    assert mem_check.used_sessions == 2
    assert mem_check.is_active == False

    # 6. Cancel appointment 1 (using update endpoint maybe? or just patch status)
    update_data = {"status": "Cancelled"}
    response = client.put(f"/appointments/{appt1['id']}", json=update_data)

    # Verify membership refunded 1 and activated
    mem_check = get_membership_from_db(membership_id)
    print(f"After Cancel Appt 1 -> Used Sessions: {mem_check.used_sessions}, Active: {mem_check.is_active}")
    assert mem_check.used_sessions == 1
    assert mem_check.is_active == True

    # 7. Delete appointment 2
    response = client.delete(f"/appointments/{appt2['id']}")

    # Verify membership refunded 1
    mem_check = get_membership_from_db(membership_id)
    print(f"After Delete Appt 2 -> Used Sessions: {mem_check.used_sessions}, Active: {mem_check.is_active}")
    assert mem_check.used_sessions == 0

    print("ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    test_membership_tracking()
