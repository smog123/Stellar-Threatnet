"""AI threat assistant endpoint tests."""

from conftest import API_PREFIX

VALID_ADDRESS = "G" + "A" * 55


async def test_ai_phishing_query_returns_disclaimer(client):
    resp = await client.post(
        f"{API_PREFIX}/ai/query", json={"query": "Explain the recent phishing campaign"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "phishing" in body["analysis"].lower()
    assert "certainty" in body["confidence_disclaimer"].lower()
    assert body["sources_referenced"]


async def test_ai_wallet_query_enriched_with_lookup(client, session_factory):
    from app.models.entities import ThreatStatus, WalletReputation

    async with session_factory() as db:
        db.add(
            WalletReputation(
                address=VALID_ADDRESS,
                reputation_score=10,
                status=ThreatStatus.CONFIRMED_MALICIOUS,
                category="Drainer",
                reason="Confirmed drainer behavior.",
            )
        )
        await db.commit()

    resp = await client.post(
        f"{API_PREFIX}/ai/query",
        json={"query": f"Is this wallet suspicious? {VALID_ADDRESS}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "10" in body["analysis"]
    assert "confirmed_malicious" in body["analysis"]
    assert "wallet telemetry" in " ".join(body["sources_referenced"]).lower()


async def test_ai_general_query(client):
    resp = await client.post(
        f"{API_PREFIX}/ai/query", json={"query": "What does Stellar ThreatNet monitor?"}
    )
    assert resp.status_code == 200
    assert resp.json()["analysis"]
