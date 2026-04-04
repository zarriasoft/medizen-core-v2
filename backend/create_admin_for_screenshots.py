from app.database import SessionLocal
from app.crud import create_user
from app.schemas import UserCreate
from app.auth import get_password_hash

db = SessionLocal()
try:
    user_in = UserCreate(
        username="admin", 
        email="admin@medizen.com", 
        password="medicadmin", 
        full_name="Admin", 
        role="admin"
    )
    hashed = get_password_hash("medicadmin")
    # create_user will hash the password
    user = create_user(db, user_in, hashed)
    print("User created successfully")
except Exception as e:
    print("User might already exist or error:", e)
finally:
    db.close()
