from app.database import SessionLocal
from app.models import Membership, Appointment

db = SessionLocal()

# Find the membership we just created
mem = db.query(Membership).filter(Membership.membership_type == "TEST_AUTO_TRACKING").order_by(Membership.id.desc()).first()
print("Membership:", mem.__dict__)

# Try the query as written in crud.py
active_membership = db.query(Membership)\
                        .filter(Membership.patient_id == mem.patient_id)\
                        .filter(Membership.is_active == True)\
                        .filter(Membership.used_sessions < Membership.total_sessions)\
                        .first()
print("Query result:", active_membership)

if active_membership:
    print("Found it!")
else:
    print("Didn't find it. Let's try piece by piece.")
    print("Patient ID match:", db.query(Membership).filter(Membership.patient_id == mem.patient_id).all())
    print("Active match:", db.query(Membership).filter(Membership.is_active == True).all())
    print("Sessions match:", db.query(Membership).filter(Membership.used_sessions < Membership.total_sessions).all())

db.close()
