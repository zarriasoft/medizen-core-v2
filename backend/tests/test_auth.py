from app.models import User, Patient
from app.auth import get_password_hash

def test_login_incorrect_credentials(client):
    response = client.post(
        "/auth/login",
        data={"username": "fake@admin.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_protected_route_without_token(client):
    # GET /settings/ is restricted to admins
    response = client.get("/settings/")
    assert response.status_code == 401

def test_admin_login_and_access(client, db_session):
    # Setup mock admin
    admin = User(
        username="admin@medizen.cl",
        email="admin@medizen.cl",
        hashed_password=get_password_hash("testpass"),
        role="admin"
    )
    db_session.add(admin)
    db_session.commit()

    # Login
    login_response = client.post(
        "/auth/login",
        data={"username": "admin@medizen.cl", "password": "testpass"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Access protected route
    settings_response = client.get(
        "/settings/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert settings_response.status_code == 200

def test_patient_login(client, db_session):
    # Create patient
    patient = Patient(
        first_name="Test",
        last_name="Patient",
        email="patient@test.com",
        hashed_password=get_password_hash("securepass")
    )
    db_session.add(patient)
    db_session.commit()

    # Login via patient endpoint
    login_response = client.post(
        "/auth/login/patient",
        data={"username": "patient@test.com", "password": "securepass"}
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
