"""API key and audit log tests."""

from sqlalchemy import select

from app.models.entities import APIKey, UserRole
from conftest import API_PREFIX


async def test_api_key_lifecycle(client, reporter_headers):
    created = await client.post(
        f"{API_PREFIX}/api-keys", json={"name": "ci-pipeline"}, headers=reporter_headers
    )
    assert created.status_code == 201
    body = created.json()
    assert body["key"].startswith("tn_")
    key_id = body["id"]

    listing = await client.get(f"{API_PREFIX}/api-keys", headers=reporter_headers)
    assert len(listing.json()) == 1

    revoked = await client.delete(f"{API_PREFIX}/api-keys/{key_id}", headers=reporter_headers)
    assert revoked.status_code == 204
    after = await client.get(f"{API_PREFIX}/api-keys", headers=reporter_headers)
    assert after.json()[0]["is_active"] is False


async def test_api_key_authenticates_lookups(client, reporter_headers):
    created = (
        await client.post(f"{API_PREFIX}/api-keys", json={"name": "sdk"}, headers=reporter_headers)
    ).json()

    # Use the plaintext key as an alternative auth method on an authenticated endpoint.
    me = await client.get(f"{API_PREFIX}/auth/me", headers={"X-API-Key": created["key"]})
    assert me.status_code == 200
    assert me.json()["email"] == "reporter@example.com"

    bad = await client.get(f"{API_PREFIX}/auth/me", headers={"X-API-Key": "tn_invalid"})
    assert bad.status_code == 401


async def test_audit_logs_admin_only(client, reporter_headers, session_factory):
    from conftest import auth_headers, promote_user

    await client.post(f"{API_PREFIX}/api-keys", json={"name": "x"}, headers=reporter_headers)

    # Reporter cannot read audit logs.
    forbidden = await client.get(f"{API_PREFIX}/admin/audit-logs", headers=reporter_headers)
    assert forbidden.status_code == 403

    admin_headers = await auth_headers(client, "admin@example.com")
    await promote_user(session_factory, "admin@example.com", UserRole.ADMIN)
    logs = await client.get(f"{API_PREFIX}/admin/audit-logs", headers=admin_headers)
    assert logs.status_code == 200
    assert any(entry["action"] == "API_KEY_CREATED" for entry in logs.json())
