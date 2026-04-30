from app.models import Payment, Membership, Appointment, Patient
from datetime import datetime, timedelta

def test_complete_patient_journey(client, db_session):
    # --- PASO 1: Inscripción (Simulación Landing Page) ---
    enroll_data = {
        "first_name": "E2E",
        "last_name": "Tester",
        "email": "e2e@tester.com",
        "password": "supersecurepassword123",
        "plan_name": "Plan Test E2E"
    }

    # Fake a plan to avoid NoneType errors in price
    from app.models import MembershipPlan
    plan = MembershipPlan(name="Plan Test E2E", price="$45,000", total_sessions=4)
    db_session.add(plan)
    db_session.commit()

    resp_enroll = client.post("/public/enroll", json=enroll_data)
    assert resp_enroll.status_code == 200
    assert "Inscripción recibida" in resp_enroll.json()["message"]

    # Verificar Base de Datos (Membresía inactiva y Pago pendiente)
    patient = db_session.query(Patient).filter(Patient.email == "e2e@tester.com").first()
    assert patient is not None, "patient is None"

    membership = db_session.query(Membership).filter(Membership.patient_id == patient.id).first()
    assert membership is not None, "membership is None"
    assert membership.is_active is False

    payment = db_session.query(Payment).filter(Payment.patient_id == patient.id).first()
    assert payment is not None, "payment is None"
    assert payment.amount == 45000.0
    assert payment.status == "pending"

    # Simular Activación de Membresía (como si pagara por webpay)
    membership.is_active = True
    db_session.commit()

    # --- PASO 2: Login ---
    resp_login = client.post(
        "/auth/login/patient",
        data={"username": "e2e@tester.com", "password": "supersecurepassword123"}
    )
    assert resp_login.status_code == 200
    token = resp_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # --- PASO 3: Editar Perfil ---
    profile_update = {
        "first_name": "E2E",
        "last_name": "Tester Editado",
        "phone": "+56911223344",
        "address": "Av Test 123"
    }
    resp_profile = client.put("/me/", headers=headers, json=profile_update)
    assert resp_profile.status_code == 200
    assert resp_profile.json()["last_name"] == "Tester Editado"
    assert resp_profile.json()["phone"] == "+56911223344"

    # --- PASO 4: Agendar Cita ---
    target_date = (datetime.now() + timedelta(days=5)).replace(hour=15, minute=0, second=0, microsecond=0)

    from app.models import SpecialistSchedule
    sched = SpecialistSchedule(day_of_week=target_date.weekday(), start_time="08:00", end_time="18:00", is_active=True)
    db_session.add(sched)
    db_session.commit()

    resp_book = client.post(
        "/me/appointments",
        headers=headers,
        json={"appointment_date": target_date.isoformat(), "membership_id": membership.id}
    )
    assert resp_book.status_code == 200
    app_id = resp_book.json()["id"]
    assert resp_book.json()["status"] == "Scheduled"

    # Verificar que el cupo de la membresia NO se desconto (se descuenta al completar, no al agendar)
    db_session.refresh(membership)
    assert membership.used_sessions == 0

    # --- PASO 5: Prevención Doble Reserva ---
    resp_book_fail = client.post(
        "/me/appointments",
        headers=headers,
        json={"appointment_date": target_date.isoformat()}
    )
    assert resp_book_fail.status_code == 400
    assert "El horario seleccionado no está disponible" in resp_book_fail.json()["detail"]

    # --- PASO 6: Cancelar Cita ---
    resp_cancel = client.put(f"/me/appointments/{app_id}/cancel", headers=headers)
    assert resp_cancel.status_code == 200
    assert resp_cancel.json()["status"] == "Cancelled"

    db_session.refresh(membership)
    assert membership.used_sessions == 0

    # Final check: the DB reflects it
    appointment = db_session.query(Appointment).filter(Appointment.id == app_id).first()
    assert appointment.status == "Cancelled"
