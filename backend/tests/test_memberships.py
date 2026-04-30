from app.models import User, Patient, MembershipPlan
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


def _create_patient(client, token):
    resp = client.post(
        "/patients/",
        json={"first_name": "Maria", "last_name": "Lopez", "email": "maria@test.com"},
        headers={"Authorization": f"Bearer {token}"}
    )
    return resp.json()["id"]


def _create_membership_plan(db_session):
    plan = MembershipPlan(
        name="Plan Basico",
        description="Plan basico de bienestar",
        price="$30.000",
        frequency="mensual",
        features="Consulta mensual,IEIM",
        total_sessions=4
    )
    db_session.add(plan)
    db_session.commit()
    return plan.id


def test_create_membership(client, db_session):
    token = _get_admin_token(client, db_session)
    patient_id = _create_patient(client, token)
    _create_membership_plan(db_session)

    resp = client.post(
        "/memberships/",
        json={
            "patient_id": patient_id,
            "membership_type": "Plan Basico",
            "total_sessions": 4
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["patient_id"] == patient_id
    assert data["membership_type"] == "Plan Basico"
    assert data["total_sessions"] == 4
    assert data["used_sessions"] == 0
    assert data["is_active"] is True


def test_create_membership_nonexistent_patient(client, db_session):
    token = _get_admin_token(client, db_session)
    resp = client.post(
        "/memberships/",
        json={"patient_id": 9999, "membership_type": "Plan Basico", "total_sessions": 4},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 404
    assert "Patient not found" in resp.json()["detail"]


def test_get_patient_memberships(client, db_session):
    token = _get_admin_token(client, db_session)
    patient_id = _create_patient(client, token)

    client.post(
        "/memberships/",
        json={"patient_id": patient_id, "membership_type": "Plan Basico", "total_sessions": 4},
        headers={"Authorization": f"Bearer {token}"}
    )

    resp = client.get(
        f"/memberships/patient/{patient_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["patient_id"] == patient_id


def test_get_all_memberships(client, db_session):
    token = _get_admin_token(client, db_session)
    patient_id = _create_patient(client, token)

    client.post(
        "/memberships/",
        json={"patient_id": patient_id, "membership_type": "Plan Basico", "total_sessions": 4},
        headers={"Authorization": f"Bearer {token}"}
    )

    resp = client.get("/memberships/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_update_membership(client, db_session):
    token = _get_admin_token(client, db_session)
    patient_id = _create_patient(client, token)

    create_resp = client.post(
        "/memberships/",
        json={"patient_id": patient_id, "membership_type": "Plan Basico", "total_sessions": 4},
        headers={"Authorization": f"Bearer {token}"}
    )
    membership_id = create_resp.json()["id"]

    resp = client.put(
        f"/memberships/{membership_id}",
        json={"used_sessions": 2},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["used_sessions"] == 2


def test_delete_membership(client, db_session):
    token = _get_admin_token(client, db_session)
    patient_id = _create_patient(client, token)

    create_resp = client.post(
        "/memberships/",
        json={"patient_id": patient_id, "membership_type": "Plan Basico", "total_sessions": 4},
        headers={"Authorization": f"Bearer {token}"}
    )
    membership_id = create_resp.json()["id"]

    resp = client.delete(
        f"/memberships/{membership_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert "deactivated" in resp.json()["detail"]


def test_memberships_require_auth(client):
    resp = client.post("/memberships/", json={"patient_id": 1, "membership_type": "Test", "total_sessions": 1})
    assert resp.status_code == 401
