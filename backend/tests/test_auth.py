"""Authentication and authorization tests."""

from conftest import API_PREFIX


async def test_register_creates_reporter(client):
    resp = await client.post(
        f"{API_PREFIX}/auth/register",
        json={"email": "alice@example.com", "password": "correct-horse-battery", "full_name": "Alice"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == "alice@example.com"
    assert body["user"]["role"] == "reporter"


async def test_register_duplicate_email_rejected(client):
    payload = {"email": "bob@example.com", "password": "correct-horse-battery"}
    first = await client.post(f"{API_PREFIX}/auth/register", json=payload)
    assert first.status_code == 201
    second = await client.post(f"{API_PREFIX}/auth/register", json=payload)
    assert second.status_code == 409


async def test_login_success_and_me(client):
    await client.post(
        f"{API_PREFIX}/auth/register",
        json={"email": "carol@example.com", "password": "correct-horse-battery"},
    )
    login = await client.post(
        f"{API_PREFIX}/auth/token",
        data={"username": "carol@example.com", "password": "correct-horse-battery"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = await client.get(f"{API_PREFIX}/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "carol@example.com"


async def test_login_wrong_password_rejected(client):
    await client.post(
        f"{API_PREFIX}/auth/register",
        json={"email": "dave@example.com", "password": "correct-horse-battery"},
    )
    login = await client.post(
        f"{API_PREFIX}/auth/token",
        data={"username": "dave@example.com", "password": "wrong-password"},
    )
    assert login.status_code == 401


async def test_me_requires_auth(client):
    resp = await client.get(f"{API_PREFIX}/auth/me")
    assert resp.status_code == 401
