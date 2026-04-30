import traceback
from app.database import SessionLocal
from app.routers.capture import EnrollRequest, enroll_patient

db = SessionLocal()
form = EnrollRequest(
    first_name="Test",
    last_name="User",
    email="test_crash@example.com",
    password="my_password",
    phone="123",
    date_of_birth=None,
    plan_name="Premium"
)
try:
    print(enroll_patient(form, db))
except Exception as e:
    traceback.print_exc()
db.close()
