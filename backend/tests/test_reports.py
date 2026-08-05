"""Community report workflow tests: submit -> vote -> moderate -> score update."""

from sqlalchemy import func, select

from app.models.entities import AuditLog, Evidence, ThreatStatus, WalletReputation
from conftest import API_PREFIX

VALID_ADDRESS = "G" + "A" * 55

REPORT_PAYLOAD = {
    "target_type": "wallet",
    "target_value": VALID_ADDRESS,
    "category": "Malicious Drainer",
    "description": "Address receives funds from multiple confirmed phishing domains.",
    "evidence_url": "https://stellar.expert/tx/abc123",
}


async def test_submit_report_requires_auth(client):
    resp = await client.post(f"{API_PREFIX}/reports", json=REPORT_PAYLOAD)
    assert resp.status_code in (401, 403)


async def test_submit_report_queues_for_moderation(client, reporter_headers):
    resp = await client.post(f"{API_PREFIX}/reports", json=REPORT_PAYLOAD, headers=reporter_headers)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["status"] == "pending"
    assert body["target_value"] == VALID_ADDRESS


async def test_vote_on_report(client, reporter_headers, moderator_headers):
    report = (
        await client.post(f"{API_PREFIX}/reports", json=REPORT_PAYLOAD, headers=reporter_headers)
    ).json()

    voted = await client.post(
        f"{API_PREFIX}/reports/{report['id']}/vote", json={"vote": "up"}, headers=moderator_headers
    )
    assert voted.status_code == 200
    assert voted.json()["upvotes"] == 1


async def test_vote_is_unique_per_user(client, reporter_headers, moderator_headers):
    report = (
        await client.post(f"{API_PREFIX}/reports", json=REPORT_PAYLOAD, headers=reporter_headers)
    ).json()
    report_id = report["id"]

    first = await client.post(
        f"{API_PREFIX}/reports/{report_id}/vote", json={"vote": "up"}, headers=moderator_headers
    )
    assert first.status_code == 200
    assert first.json()["upvotes"] == 1

    # A second vote by the same moderator must be rejected — no inflation.
    second = await client.post(
        f"{API_PREFIX}/reports/{report_id}/vote", json={"vote": "up"}, headers=moderator_headers
    )
    assert second.status_code == 409

    fresh = await client.get(f"{API_PREFIX}/reports/{report_id}")
    if fresh.status_code == 200:
        assert fresh.json()["upvotes"] == 1


async def test_reporter_cannot_moderate(client, reporter_headers):
    report = (
        await client.post(f"{API_PREFIX}/reports", json=REPORT_PAYLOAD, headers=reporter_headers)
    ).json()
    resp = await client.post(
        f"{API_PREFIX}/reports/{report['id']}/moderate",
        json={"action": "approve"},
        headers=reporter_headers,
    )
    assert resp.status_code == 403


async def test_approve_report_creates_entity_and_recomputes_score(
    client, reporter_headers, moderator_headers, session_factory
):
    report = (
        await client.post(f"{API_PREFIX}/reports", json=REPORT_PAYLOAD, headers=reporter_headers)
    ).json()

    # Wallet must not be tracked before approval.
    before = await client.get(f"{API_PREFIX}/lookup/wallet/{VALID_ADDRESS}")
    assert before.status_code == 404

    approved = await client.post(
        f"{API_PREFIX}/reports/{report['id']}/moderate",
        json={"action": "approve", "proof_type": "tx_hash", "confidence": 1.0},
        headers=moderator_headers,
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    # Evidence + audit log persisted.
    async with session_factory() as db:
        evidence_count = (
            await db.execute(select(func.count(Evidence.id)))
        ).scalar_one()
        audit_count = (
            await db.execute(select(func.count(AuditLog.id)))
        ).scalar_one()
        wallet = await db.get(WalletReputation, VALID_ADDRESS)
    assert evidence_count == 1
    assert audit_count >= 2  # submit + approve
    assert wallet is not None
    assert wallet.status == ThreatStatus.SUSPICIOUS  # 80 - 30*1.0 = 50 -> suspicious
    assert wallet.reputation_score == 50

    # Lookup now resolves.
    after = await client.get(f"{API_PREFIX}/lookup/wallet/{VALID_ADDRESS}")
    assert after.status_code == 200
    assert after.json()["reputation_score"] == 50


async def test_reject_report_creates_no_entity(client, reporter_headers, moderator_headers, session_factory):
    report = (
        await client.post(f"{API_PREFIX}/reports", json=REPORT_PAYLOAD, headers=reporter_headers)
    ).json()
    rejected = await client.post(
        f"{API_PREFIX}/reports/{report['id']}/moderate",
        json={"action": "reject", "moderation_note": "Duplicate of existing report"},
        headers=moderator_headers,
    )
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "rejected"

    async with session_factory() as db:
        evidence_count = (await db.execute(select(func.count(Evidence.id)))).scalar_one()
        wallet = await db.get(WalletReputation, VALID_ADDRESS)
    assert evidence_count == 0
    assert wallet is None


async def test_moderation_queue_lists_pending(client, reporter_headers, moderator_headers):
    await client.post(f"{API_PREFIX}/reports", json=REPORT_PAYLOAD, headers=reporter_headers)
    queue = await client.get(f"{API_PREFIX}/reports/queue", headers=moderator_headers)
    assert queue.status_code == 200
    assert len(queue.json()) == 1


async def test_moderating_twice_returns_404(client, reporter_headers, moderator_headers):
    report = (
        await client.post(f"{API_PREFIX}/reports", json=REPORT_PAYLOAD, headers=reporter_headers)
    ).json()
    await client.post(
        f"{API_PREFIX}/reports/{report['id']}/moderate",
        json={"action": "reject"},
        headers=moderator_headers,
    )
    again = await client.post(
        f"{API_PREFIX}/reports/{report['id']}/moderate",
        json={"action": "approve"},
        headers=moderator_headers,
    )
    assert again.status_code == 404
