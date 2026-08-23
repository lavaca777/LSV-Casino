from tests.conftest import register_user


def _register_and_login(client):
    resp = register_user(client)
    data = resp.json()
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    return data["user_id"], headers


def test_get_user(client):
    user_id, headers = _register_and_login(client)
    resp = client.get(f"/users/{user_id}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == user_id
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "password_hash" not in data
    assert "password" not in data


def test_get_other_user_forbidden(client):
    user_id, headers = _register_and_login(client)
    resp = register_user(client, email="other@example.com", username="otheruser")
    other_id = resp.json()["user_id"]
    resp = client.get(f"/users/{other_id}", headers=headers)
    assert resp.status_code == 403


def test_update_user(client):
    user_id, headers = _register_and_login(client)
    resp = client.put(
        f"/users/{user_id}",
        json={"username": "newusername", "email": "new@example.com"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "newusername"
    assert data["email"] == "new@example.com"


def test_update_user_duplicate_username(client):
    register_user(client, email="other@example.com", username="otheruser")
    user_id, headers = _register_and_login(client)
    resp = client.put(
        f"/users/{user_id}",
        json={"username": "otheruser"},
        headers=headers,
    )
    assert resp.status_code == 409


def test_change_password(client):
    user_id, headers = _register_and_login(client)
    resp = client.put(
        f"/users/{user_id}/password",
        json={"current_password": "password123", "new_password": "newpassword123"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json() == {"message": "Password updated"}

    # login con la nueva contraseña funciona
    resp = client.post(
        "/auth/login",
        json={"email_or_username": "test@example.com", "password": "newpassword123"},
    )
    assert resp.status_code == 200


def test_change_password_wrong_current(client):
    user_id, headers = _register_and_login(client)
    resp = client.put(
        f"/users/{user_id}/password",
        json={"current_password": "wrongpass", "new_password": "newpassword123"},
        headers=headers,
    )
    assert resp.status_code == 400
