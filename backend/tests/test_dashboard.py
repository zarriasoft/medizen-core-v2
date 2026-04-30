from app.models import User, Patient, IEIMRecord
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


def test_dashboard_metrics_empty(client, db_session):
    token = _get_admin_token(client, db_session)
    resp = client.get("/dashboard/metrics", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["active_patients"] == 0
    assert data["avg_ieim_score"] == 0
    assert data["sessions_today"] == 0
    assert data["abandonment_risk"] == 0


def test_dashboard_metrics_with_patient(client, db_session):
    token = _get_admin_token(client, db_session)
    patient = Patient(
        first_name="Ana", last_name="Garcia", email="ana@test.com", is_active=True
    )
    db_session.add(patient)
    db_session.commit()

    resp = client.get("/dashboard/metrics", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["active_patients"] == 1
    assert data["abandonment_risk"] == 1  # no IEIM records -> at risk


def test_dashboard_metrics_with_ieim(client, db_session):
    token = _get_admin_token(client, db_session)
    patient = Patient(
        first_name="Ana", last_name="Garcia", email="ana@test.com", is_active=True
    )
    db_session.add(patient)
    db_session.commit()

    record = IEIMRecord(
        patient_id=patient.id,
        record_date=__import__("datetime").datetime.utcnow(),
        pain_level=7, sleep_quality=6,
        energy_level=5, stress_anxiety=4,
        mobility=8, inflammation=3,
        overall_score=5.5
    )
    db_session.add(record)
    db_session.commit()

    resp = client.get("/dashboard/metrics", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["avg_ieim_score"] == 5.5
    assert data["abandonment_risk"] == 0  # has recent IEIM


def test_dashboard_alerts(client, db_session):
    token = _get_admin_token(client, db_session)
    patient = Patient(
        first_name="Carlos", last_name="Ruiz", email="carlos@test.com", is_active=True
    )
    db_session.add(patient)
    db_session.commit()

    record = IEIMRecord(
        patient_id=patient.id,
        record_date=__import__("datetime").datetime.utcnow(),
        pain_level=3, sleep_quality=2,
        energy_level=3, stress_anxiety=2,
        mobility=4, inflammation=1,
        overall_score=2.5  # critical
    )
    db_session.add(record)
    db_session.commit()

    resp = client.get("/dashboard/alerts", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert any("2.5" in alert["message"] for alert in data)


def test_dashboard_ieim_history(client, db_session):
    token = _get_admin_token(client, db_session)
    resp = client.get("/dashboard/ieim-history", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_dashboard_requires_auth(client):
    resp = client.get("/dashboard/metrics")
    assert resp.status_code == 401
