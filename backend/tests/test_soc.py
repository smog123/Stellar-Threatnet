"""SOC overview endpoint tests: network posture, landscape, feeds."""

from conftest import API_PREFIX

from app.models.entities import (
    CommunityReport,
    DomainReputation,
    Incident,
    IncidentStatus,
    ReportStatus,
    ThreatStatus,
    TokenReputation,
    WalletReputation,
)

W1 = "G" + "A" * 55
W2 = "G" + "B" * 55
W3 = "G" + "C" * 55
ISSUER = "G" + "D" * 55


async def _seed_soc(session_factory):
    async with session_factory() as db:
        db.add_all(
            [
                WalletReputation(address=W1, reputation_score=5, status=ThreatStatus.CONFIRMED_MALICIOUS, category="Drainer", reason="drainer"),
                WalletReputation(address=W2, reputation_score=30, status=ThreatStatus.SUSPICIOUS, category="Spammer", reason="spam"),
                WalletReputation(address=W3, reputation_score=90, status=ThreatStatus.TRUSTED, category="Anchor", reason="verified"),
                DomainReputation(domain_name="evil-claim.net", confidence_score=0.95, status=ThreatStatus.CONFIRMED_MALICIOUS, category="Fake Airdrop", reason="claim page"),
                TokenReputation(asset_identifier=f"FAKEUSDC:{ISSUER}", asset_code="FAKEUSDC", issuer_address=ISSUER, status=ThreatStatus.SUSPICIOUS, category="Impersonation", reason="impersonates USDC"),
                Incident(id="INC-SOC-01", title="Active campaign A", description="d", affected_services="wallets", mitigations="block", status=IncidentStatus.OPEN),
                Incident(id="INC-SOC-02", title="Active campaign B", description="d", affected_services="wallets", mitigations="warn", status=IncidentStatus.INVESTIGATING),
                Incident(id="INC-SOC-03", title="Resolved campaign", description="d", affected_services="wallets", mitigations="patched", status=IncidentStatus.RESOLVED),
                CommunityReport(id="REP-SOC-01", reporter_id="USR-REP1", target_type="wallet", target_value=W1, category="Drainer", description="drainer", status=ReportStatus.PENDING, upvotes=1, downvotes=0),
                CommunityReport(id="REP-SOC-02", reporter_id="USR-REP1", target_type="domain", target_value="old-claim.net", category="Fake Airdrop", description="old", status=ReportStatus.APPROVED),
            ]
        )
        await db.commit()


async def test_soc_overview_shape(client, session_factory):
    await _seed_soc(session_factory)
    resp = await client.get(f"{API_PREFIX}/stats/overview")
    assert resp.status_code == 200
    body = resp.json()

    assert body["generated_at"]
    assert body["network_status"]["level"] in ("normal", "elevated", "high")
    assert body["network_status"]["label"]
    assert body["network_status"]["summary"]

    assert body["landscape"]["wallets"]["confirmed_malicious"] == 1
    assert body["landscape"]["wallets"]["suspicious"] == 1
    assert body["landscape"]["wallets"]["trusted"] == 1
    assert body["landscape"]["domains"]["confirmed_malicious"] == 1
    assert body["landscape"]["tokens"]["suspicious"] == 1

    assert body["counts"]["total_malicious_wallets"] == 1
    assert body["counts"]["total_incidents_recorded"] == 3

    # modules are placeholder counters for later phases
    assert body["modules"] == {"anchors": 0, "soroban_scans": 0, "sep_validations": 0}


async def test_soc_overview_active_campaigns_excludes_resolved(client, session_factory):
    await _seed_soc(session_factory)
    body = (await client.get(f"{API_PREFIX}/stats/overview")).json()
    ids = [c["id"] for c in body["active_campaigns"]]
    assert "INC-SOC-01" in ids
    assert "INC-SOC-02" in ids
    assert "INC-SOC-03" not in ids


async def test_soc_overview_recent_reports_and_threats(client, session_factory):
    await _seed_soc(session_factory)
    body = (await client.get(f"{API_PREFIX}/stats/overview")).json()

    report_ids = [r["id"] for r in body["recent_reports"]]
    assert "REP-SOC-01" in report_ids and "REP-SOC-02" in report_ids

    # latest threats must exclude trusted entities
    assert all(t["status"] != "trusted" for t in body["latest_threats"])


async def test_soc_overview_empty_database(client):
    body = (await client.get(f"{API_PREFIX}/stats/overview")).json()
    assert body["network_status"]["level"] == "normal"
    assert body["landscape"]["wallets"]["confirmed_malicious"] == 0
    assert body["counts"]["total_indicators"] == 0
