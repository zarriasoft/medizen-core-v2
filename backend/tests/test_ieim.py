from app.models import User, Patient
from app.auth import get_password_hash


def _get_admin_token(client, db_session):
    admin = User(
        username="admin@medizen.cl",
        email="admin@medizen.cl",
        hashed_password=get_password_hash("testpass"),
        role="admin"
    )
    db_session.add(admin)
    db_session.commit()
    resp = client.post("/auth/login", data={"username": "admin@medizen.cl", "password": "testpass"})
    return resp.json()["access_token"]


def _create_patient(client, db_session, token):
    resp = client.post(
        "/patients/",
        json={"first_name": "Juan", "last_name": "Perez", "email": "juan@test.com"},
        headers={"Authorization": f"Bearer {token}"}
    )
    return resp.json()["id"]


def test_create_ieim_record(client, db_session):
    token = _get_admin_token(client, db_session)
    patient_id = _create_patient(client, db_session, token)

    resp = client.post(
        f"/patients/{patient_id}/ieim/",
        json={
            "patient_id": patient_id,
            "pain_level": 7,
            "sleep_quality": 5,
            "energy_level": 6,
            "stress_anxiety": 4,
            "mobility": 8,
            "inflammation": 3
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["patient_id"] == patient_id
    assert data["pain_level"] == 7
    assert data["overall_score"] is not None


def test_ieim_patient_id_mismatch(client, db_session):
    token = _get_admin_token(client, db_session)
    patient_id = _create_patient(client, db_session, token)

    resp = client.post(
        f"/patients/{patient_id}/ieim/",
        json={
            "patient_id": patient_id + 999,
            "pain_level": 5, "sleep_quality": 5,
            "energy_level": 5, "stress_anxiety": 5,
            "mobility": 5, "inflammation": 5
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 400
    assert "Patient ID mismatch" in resp.json()["detail"]


def test_ieim_nonexistent_patient(client, db_session):
    token = _get_admin_token(client, db_session)
    resp = client.post(
        "/patients/9999/ieim/",
        json={
            "patient_id": 9999,
            "pain_level": 5, "sleep_quality": 5,
            "energy_level": 5, "stress_anxiety": 5,
            "mobility": 5, "inflammation": 5
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 404


def test_read_ieim_records(client, db_session):
    token = _get_admin_token(client, db_session)
    patient_id = _create_patient(client, db_session, token)

    client.post(
        f"/patients/{patient_id}/ieim/",
        json={
            "patient_id": patient_id,
            "pain_level": 8, "sleep_quality": 7,
            "energy_level": 6, "stress_anxiety": 5,
            "mobility": 4, "inflammation": 3
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    resp = client.get(
        f"/patients/{patient_id}/ieim/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["patient_id"] == patient_id


def test_ieim_requires_auth(client):
    resp = client.post(
        "/patients/1/ieim/",
        json={
            "patient_id": 1,
            "pain_level": 5, "sleep_quality": 5,
            "energy_level": 5, "stress_anxiety": 5,
            "mobility": 5, "inflammation": 5
        }
    )
    assert resp.status_code == 401
