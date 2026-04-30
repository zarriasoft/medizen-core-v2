from app.models import Patient, IEIMRecord


def test_capture_creates_patient_and_ieim(client, db_session):
    resp = client.post("/public/capture", json={
        "first_name": "Pedro",
        "last_name": "Gomez",
        "email": "pedro@test.com",
        "pain_level": 8,
        "sleep_quality": 7,
        "energy_level": 6,
        "stress_anxiety": 5,
        "mobility": 4,
        "inflammation": 3
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "Gracias Pedro" in data["message"]
    assert data["overall_score"] == 5.5  # (8+7+6+5+4+3)/6 = 5.5
    assert data["classification"] is not None
    assert data["recommendation"] is not None

    patient = db_session.query(Patient).filter(Patient.email == "pedro@test.com").first()
    assert patient is not None
    assert patient.first_name == "Pedro"

    records = db_session.query(IEIMRecord).filter(IEIMRecord.patient_id == patient.id).all()
    assert len(records) == 1
    assert records[0].overall_score == 5.5


def test_capture_reuses_existing_patient(client, db_session):
    patient = Patient(
        first_name="Pedro", last_name="Gomez",
        email="pedro@test.com", is_active=True
    )
    db_session.add(patient)
    db_session.commit()

    resp = client.post("/public/capture", json={
        "first_name": "Pedro",
        "last_name": "Gomez",
        "email": "pedro@test.com",
        "pain_level": 4, "sleep_quality": 4,
        "energy_level": 4, "stress_anxiety": 4,
        "mobility": 4, "inflammation": 4
    })
    assert resp.status_code == 200
    assert resp.json()["overall_score"] == 4.0

    patients = db_session.query(Patient).filter(Patient.email == "pedro@test.com").all()
    assert len(patients) == 1


def test_capture_classification_optimo(client):
    resp = client.post("/public/capture", json={
        "first_name": "A", "last_name": "B",
        "email": "a@test.com",
        "pain_level": 9, "sleep_quality": 9,
        "energy_level": 9, "stress_anxiety": 9,
        "mobility": 9, "inflammation": 8
    })
    assert resp.status_code == 200
    assert "Equilibrio Optimo" in resp.json()["classification"]


def test_capture_classification_critico(client):
    resp = client.post("/public/capture", json={
        "first_name": "B", "last_name": "C",
        "email": "b@test.com",
        "pain_level": 2, "sleep_quality": 1,
        "energy_level": 2, "stress_anxiety": 1,
        "mobility": 3, "inflammation": 1
    })
    assert resp.status_code == 200
    assert "Desequilibrio Critico" in resp.json()["classification"]


def test_capture_no_auth_required(client):
    resp = client.post("/public/capture", json={
        "first_name": "C", "last_name": "D",
        "email": "c@test.com",
        "pain_level": 5, "sleep_quality": 5,
        "energy_level": 5, "stress_anxiety": 5,
        "mobility": 5, "inflammation": 5
    })
    assert resp.status_code == 200
