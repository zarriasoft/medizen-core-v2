from app.database import SessionLocal
from app import auth, crud, schemas

def create_admin():
    db = SessionLocal()
    try:
        user = crud.get_user_by_username(db, "admin")
        if user:
            print("Admin user already exists!")
            return

        admin_data = schemas.UserCreate(
            username="admin",
            password="adminpassword",
            email="admin@medizen.com",
            full_name="Administrador Medizen",
            role="admin",
            is_active=True
        )
        hashed_password = auth.get_password_hash(admin_data.password)
        crud.create_user(db, admin_data, hashed_password)
        print("Admin user created successfully! (admin / adminpassword)")
    except Exception as e:
        print(f"Error creating admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
