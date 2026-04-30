from app.models import User, Patient, Membership, MembershipPlan, Payment, IEIMRecord, Appointment
from app.auth import get_password_hash
from datetime import datetime, timedelta


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


def test_analytics_empty(client, db_session):
    token = _get_admin_token(client, db_session)
    resp = client.get("/dashboard/analytics", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["estimated_monthly_revenue"] == 0
    assert data["retention_rate"] == 0
    assert data["total_appointments"] == 0


def test_analytics_with_data(client, db_session):
    token = _get_admin_token(client, db_session)

    patient = Patient(first_name="Ana", last_name="Garcia", email="ana@test.com", is_active=True)
    db_session.add(patient)
    db_session.commit()

    plan = MembershipPlan(name="Plan Basico", price="$45.000", frequency="mensual", features="IEIM", total_sessions=4)
    db_session.add(plan)
    db_session.commit()

    membership = Membership(patient_id=patient.id, membership_type="Plan Basico", total_sessions=4, is_active=True)
    db_session.add(membership)
    db_session.commit()

    ieim = IEIMRecord(patient_id=patient.id, record_date=datetime.utcnow(), pain_level=7, sleep_quality=6,
                      energy_level=5, stress_anxiety=4, mobility=8, inflammation=3, overall_score=5.5)
    db_session.add(ieim)
    db_session.commit()

    payment = Payment(patient_id=patient.id, membership_id=membership.id, amount=45000, status="completed")
    db_session.add(payment)
    db_session.commit()

    appt = Appointment(patient_id=patient.id, appointment_date=datetime.utcnow() + timedelta(days=1), status="Scheduled")
    db_session.add(appt)
    db_session.commit()

    resp = client.get("/dashboard/analytics", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()

    assert data["retention_rate"] == 100
    assert data["total_appointments"] == 1
    assert data["completed_appointments"] == 0
    assert data["total_payments"] == 1
    assert "Plan Basico" in data["membership_distribution"]
    assert len(data["monthly_patients"]) == 6
    assert len(data["ieim_trend"]) == 6


def test_payment_init_mock(client, db_session):
    token = _get_admin_token(client, db_session)

    patient = Patient(first_name="Test", last_name="Payment", email="pay@test.com", is_active=True)
    db_session.add(patient)
    db_session.commit()

    plan = MembershipPlan(name="Plan Test", price="$30.000", frequency="mensual", features="Test", total_sessions=4)
    db_session.add(plan)
    db_session.commit()

    membership = Membership(patient_id=patient.id, membership_type="Plan Test", total_sessions=4, is_active=False)
    db_session.add(membership)
    db_session.commit()

    resp = client.post("/payments/init", json={
        "membership_id": membership.id, "amount": 30000, "return_url": "http://localhost:5174/portal"
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert "redirect_url" in data
    assert "token" in data
    assert data["token"].startswith("mock_token_")


def test_payment_confirm_mock(client, db_session):
    token = _get_admin_token(client, db_session)

    patient = Patient(first_name="Test", last_name="Confirm", email="confirm@test.com", is_active=True)
    db_session.add(patient)
    db_session.commit()

    membership = Membership(patient_id=patient.id, membership_type="Plan Test", total_sessions=4, is_active=False)
    db_session.add(membership)
    db_session.commit()

    init_resp = client.post("/payments/init", json={
        "membership_id": membership.id, "amount": 30000, "return_url": "http://localhost:5174/portal"
    }, headers={"Authorization": f"Bearer {token}"})
    payment_token = init_resp.json()["token"]

    resp = client.post(f"/payments/confirm?token={payment_token}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"

    # Verificar que la membresia se activo
    db_session.refresh(membership)
    assert membership.is_active is True


def test_payments_require_auth(client):
    resp = client.post("/payments/init", json={"membership_id": 1, "amount": 30000})
    assert resp.status_code == 401
