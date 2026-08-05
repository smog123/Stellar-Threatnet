"""Statistics, search, latest-threats, and feed tests."""

from datetime import datetime

from conftest import API_PREFIX

W1 = "G" + "A" * 55
W2 = "G" + "B" * 55
W3 = "G" + "C" * 55

ADDR = {
    "w1": W1,
    "w2": W2,
    "w3": W3,
}


async def _seed(session_factory):
    from app.models.entities import (
        DomainReputation,
        Incident,
        IncidentStatus,
        ThreatStatus,
        TokenReputation,
        WalletReputation,
    )

    async with session_factory() as db:
        db.add_all(
            [
                WalletReputation(
                    address=W1, reputation_score=5, status=ThreatStatus.CONFIRMED_MALICIOUS,
                    category="Drainer", reason="drainer",
                ),
                WalletReputation(
                    address=W2, reputation_score=15, status=ThreatStatus.CONFIRMED_MALICIOUS,
                    category="Phishing Receiver", reason="phishing receiver",
                ),
                WalletReputation(
                    address=W3, reputation_score=90, status=ThreatStatus.TRUSTED,
                    category="Verified Anchor", reason="anchor",
                ),
                DomainReputation(
                    domain_name="stellar-fake-airdrop.com", confidence_score=0.98,
                    status=ThreatStatus.CONFIRMED_MALICIOUS, category="Fake Airdrop",
                    reason="cloned claim page",
                ),
                TokenReputation(
                    asset_identifier="USDC:FAKEISSUER123", asset_code="USDC",
                    issuer_address="FAKEISSUER123", status=ThreatStatus.CONFIRMED_MALICIOUS,
                    category="Impersonation", reason="impersonates USDC",
                ),
                Incident(
                    id="INC-0001", title="Phishing campaign A", description="desc",
                    affected_services="wallets", mitigations="block", status=IncidentStatus.OPEN,
                ),
                Incident(
                    id="INC-0002", title="Resolved issue", description="desc",
                    affected_services="exchanges", mitigations="patched", status=IncidentStatus.RESOLVED,
                ),
            ]
        )
        await db.commit()


async def test_stats_counts(client, session_factory):
    await _seed(session_factory)
    resp = await client.get(f"{API_PREFIX}/stats")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_malicious_wallets"] == 2
    assert body["total_phishing_domains"] == 1
    assert body["total_scam_tokens"] == 1
    assert body["total_incidents_recorded"] == 2
    assert body["active_campaigns_count"] == 1  # only OPEN
    assert body["total_indicators"] == 4


async def test_search_finds_across_entities(client, session_factory):
    await _seed(session_factory)
    resp = await client.get(f"{API_PREFIX}/search", params={"q": "airdrop"})
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert any(r["entity_type"] == "domain" and "airdrop" in r["identifier"] for r in results)

    by_address = await client.get(f"{API_PREFIX}/search", params={"q": W1[:20]})
    assert any(r["entity_type"] == "wallet" for r in by_address.json()["results"])

    typed = await client.get(f"{API_PREFIX}/search", params={"q": "phishing", "type": "incident"})
    assert all(r["entity_type"] == "incident" for r in typed.json()["results"])


async def test_latest_threats_excludes_trusted(client, session_factory):
    await _seed(session_factory)
    resp = await client.get(f"{API_PREFIX}/threats/latest", params={"limit": 10})
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 4
    assert all(i["status"] != "trusted" for i in items)


async def test_feed_csv_contains_rows(client, session_factory):
    await _seed(session_factory)
    resp = await client.get(f"{API_PREFIX}/feed")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    text = resp.text
    assert text.startswith("entity_type,identifier")
    assert "stellar-fake-airdrop.com" in text
    assert "USDC:FAKEISSUER123" in text
