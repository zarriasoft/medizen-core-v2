from app.models import Patient, MembershipPlan, Membership, Appointment
from app.auth import get_password_hash
from datetime import datetime, timedelta

def setup_patient_and_login(client, db_session):
    # Create plan and patient
    plan = MembershipPlan(name="Plan Test", price="1000", total_sessions=5)
    db_session.add(plan)
    patient = Patient(
        first_name="Test", last_name="User",
        email="testapp@test.com", hashed_password=get_password_hash("pass")
    )
    db_session.add(patient)
    db_session.commit()

    # Create active membership
    membership = Membership(
        patient_id=patient.id, membership_type="Plan Test",
        total_sessions=5, used_sessions=0, is_active=True
    )
    db_session.add(membership)
    db_session.commit()

    # Login
    resp = client.post("/auth/login/patient", data={"username": "testapp@test.com", "password": "pass"})
    return patient.id, membership.id, resp.json()["access_token"]

def test_create_appointment(client, db_session):
    pid, mid, token = setup_patient_and_login(client, db_session)
    target_date = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)

    from app.models import SpecialistSchedule
    sched = SpecialistSchedule(day_of_week=target_date.weekday(), start_time="08:00", end_time="18:00", is_active=True)
    db_session.add(sched)
    db_session.commit()

    # Agendar cita
    response = client.post(
        "/me/appointments",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "appointment_date": target_date.isoformat(),
            "membership_id": mid
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Scheduled"

    # Verificar que NO se descontó una sesión (solo se descuenta al completar)
    membership = db_session.query(Membership).filter(Membership.id == mid).first()
    assert membership.used_sessions == 0

def test_prevent_double_booking(client, db_session):
    pid, mid, token = setup_patient_and_login(client, db_session)
    target_date = (datetime.now() + timedelta(days=1)).replace(hour=11, minute=0, second=0, microsecond=0)

    from app.models import SpecialistSchedule
    sched = SpecialistSchedule(day_of_week=target_date.weekday(), start_time="08:00", end_time="18:00", is_active=True)
    db_session.add(sched)
    db_session.commit()

    # Agendar primera cita
    res1 = client.post(
        "/me/appointments",
        headers={"Authorization": f"Bearer {token}"},
        json={"appointment_date": target_date.isoformat()}
    )
    assert res1.status_code == 200

    # Intentar agendar a la misma hora
    res2 = client.post(
        "/me/appointments",
        headers={"Authorization": f"Bearer {token}"},
        json={"appointment_date": target_date.isoformat()}
    )
    assert res2.status_code == 400
    assert "El horario seleccionado no está disponible" in res2.json()["detail"]

def test_cancel_appointment(client, db_session):
    pid, mid, token = setup_patient_and_login(client, db_session)
    target_date = (datetime.now() + timedelta(days=2)).replace(hour=14, minute=0, second=0, microsecond=0)

    from app.models import SpecialistSchedule
    sched = SpecialistSchedule(day_of_week=target_date.weekday(), start_time="08:00", end_time="18:00", is_active=True)
    db_session.add(sched)
    db_session.commit()

    # Crear cita vinculada a membresía
    res1 = client.post(
        "/me/appointments",
        headers={"Authorization": f"Bearer {token}"},
        json={"appointment_date": target_date.isoformat(), "membership_id": mid}
    )
    app_id = res1.json()["id"]

    # Cancelar cita
    res_cancel = client.put(
        f"/me/appointments/{app_id}/cancel",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res_cancel.status_code == 200
    assert res_cancel.json()["status"] == "Cancelled"

    # Verificar que la sesión se devolvió a la membresía
    membership = db_session.query(Membership).filter(Membership.id == mid).first()
    assert membership.used_sessions == 0
