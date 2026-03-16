from app.database import SessionLocal
from app.models import Appointment, Membership, Patient

db = SessionLocal()

juan = db.query(Patient).filter(Patient.first_name.like("%Juan%")).first()
if juan:
    print(f"Patient: {juan.first_name} {juan.last_name} (ID: {juan.id})")
    appts = db.query(Appointment).filter(Appointment.patient_id == juan.id).order_by(Appointment.id.desc()).limit(3).all()
    print("Appointments:")
    for a in appts:
        print(f"  - ID: {a.id}, Status: {a.status}, Date: {a.appointment_date}, Membership ID: {a.membership_id}")
    
    mems = db.query(Membership).filter(Membership.patient_id == juan.id).all()
    print("Memberships:")
    for m in mems:
        print(f"  - ID: {m.id}, Type: {m.membership_type}, Used: {m.used_sessions}/{m.total_sessions}, Active: {m.is_active}")
else:
    print("No patient named Juan found")

db.close()
