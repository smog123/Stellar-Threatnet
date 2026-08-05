"""Incident endpoint and RBAC tests."""

from conftest import API_PREFIX

INCIDENT_PAYLOAD = {
    "title": "Freighter Phishing Extension Campaign",
    "description": "Malicious extension spoofing Freighter branding extracting secret seeds.",
    "affected_services": "Freighter Users, Web Wallets",
    "mitigations": "Revoke permissions; update to official store release.",
    "references": "https://github.com/stellar-threatnet/incidents/0801",
    "severity": "high",
}


async def test_list_incidents_empty(client):
    resp = await client.get(f"{API_PREFIX}/incidents")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 0
    assert body["items"] == []


async def test_list_incidents_invalid_severity_returns_422(client):
    resp = await client.get(f"{API_PREFIX}/incidents", params={"severity": "bogus"})
    assert resp.status_code == 422


async def test_reporter_cannot_create_incident(client, reporter_headers):
    resp = await client.post(
        f"{API_PREFIX}/incidents", json=INCIDENT_PAYLOAD, headers=reporter_headers
    )
    assert resp.status_code == 403


async def test_analyst_creates_incident_and_listing_works(client, analyst_headers):
    created = await client.post(
        f"{API_PREFIX}/incidents", json=INCIDENT_PAYLOAD, headers=analyst_headers
    )
    assert created.status_code == 201, created.text
    incident = created.json()
    assert incident["title"] == INCIDENT_PAYLOAD["title"]
    assert incident["status"] == "open"
    assert incident["severity"] == "high"

    listing = await client.get(f"{API_PREFIX}/incidents")
    assert listing.json()["total"] == 1

    fetched = await client.get(f"{API_PREFIX}/incidents/{incident['id']}")
    assert fetched.status_code == 200


async def test_moderator_updates_incident_status(client, analyst_headers, moderator_headers):
    created = (
        await client.post(f"{API_PREFIX}/incidents", json=INCIDENT_PAYLOAD, headers=analyst_headers)
    ).json()

    # A reporter cannot update.
    forbidden = await client.patch(
        f"{API_PREFIX}/incidents/{created['id']}",
        json={"status": "resolved"},
        headers=await _headers(client),
    )
    assert forbidden.status_code in (401, 403)

    updated = await client.patch(
        f"{API_PREFIX}/incidents/{created['id']}",
        json={"status": "resolved"},
        headers=moderator_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "resolved"


async def test_update_missing_incident_404(client, moderator_headers):
    resp = await client.patch(
        f"{API_PREFIX}/incidents/INC-NOPE", json={"status": "resolved"}, headers=moderator_headers
    )
    assert resp.status_code == 404


async def _headers(client):
    from conftest import auth_headers

    return await auth_headers(client, "peon@example.com")
