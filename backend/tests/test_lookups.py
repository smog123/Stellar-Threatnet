"""Reputation lookup endpoint tests."""

from conftest import API_PREFIX

VALID_ADDRESS = "G" + "A" * 55
VALID_ISSUER = "G" + "B" * 55
VALID_TOKEN_ISSUER = "G" + "C" * 55


async def test_wallet_lookup_unknown_returns_404(client):
    resp = await client.get(f"{API_PREFIX}/lookup/wallet/{VALID_ADDRESS}")
    assert resp.status_code == 404


async def test_wallet_lookup_invalid_format_returns_400(client):
    resp = await client.get(f"{API_PREFIX}/lookup/wallet/not-an-address")
    assert resp.status_code == 400


async def test_domain_lookup_unknown_returns_404(client):
    resp = await client.get(f"{API_PREFIX}/lookup/domain/example.com")
    assert resp.status_code == 404


async def test_domain_lookup_invalid_format_returns_400(client):
    resp = await client.get(f"{API_PREFIX}/lookup/domain/not a domain!!")
    assert resp.status_code == 400


async def test_token_lookup_unknown_returns_404(client):
    resp = await client.get(f"{API_PREFIX}/lookup/token/FAKE/{VALID_ISSUER}")
    assert resp.status_code == 404


async def test_token_lookup_invalid_issuer_returns_400(client):
    resp = await client.get(f"{API_PREFIX}/lookup/token/FAKE/not-an-issuer")
    assert resp.status_code == 400


async def test_seeded_wallet_lookup_returns_reputation(client, session_factory):
    from app.models.entities import ThreatStatus, WalletReputation

    async with session_factory() as db:
        db.add(
            WalletReputation(
                address=VALID_ADDRESS,
                reputation_score=10,
                status=ThreatStatus.CONFIRMED_MALICIOUS,
                category="Malicious Drainer",
                reason="Confirmed drainer behavior across multiple accounts.",
                report_count=14,
            )
        )
        await db.commit()

    resp = await client.get(f"{API_PREFIX}/lookup/wallet/{VALID_ADDRESS}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["reputation_score"] == 10
    assert body["status"] == "confirmed_malicious"
    assert body["category"] == "Malicious Drainer"


async def test_seeded_domain_and_token_lookups(client, session_factory):
    from app.models.entities import DomainReputation, ThreatStatus, TokenReputation

    async with session_factory() as db:
        db.add(
            DomainReputation(
                domain_name="stellar-airdrop-claim.net",
                confidence_score=0.95,
                status=ThreatStatus.CONFIRMED_MALICIOUS,
                category="Fake Airdrop",
                reason="Cloned claim page harvesting secret keys.",
            )
        )
        db.add(
            TokenReputation(
                asset_identifier=f"USDC:{VALID_TOKEN_ISSUER}",
                asset_code="USDC",
                issuer_address=VALID_TOKEN_ISSUER,
                status=ThreatStatus.CONFIRMED_MALICIOUS,
                category="Impersonation Token",
                reason="Mimics Circle USDC with unauthorized issuer.",
            )
        )
        await db.commit()

    domain = await client.get(f"{API_PREFIX}/lookup/domain/stellar-airdrop-claim.net")
    assert domain.status_code == 200
    assert domain.json()["confidence_score"] == 0.95

    token = await client.get(f"{API_PREFIX}/lookup/token/USDC/{VALID_TOKEN_ISSUER}")
    assert token.status_code == 200
    assert token.json()["status"] == "confirmed_malicious"
