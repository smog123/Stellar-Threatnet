"""Live Horizon ingestor threat-detection tests.

Horizon is never contacted: we drive `HorizonIngestor._process_payment` directly
with sample payment records and assert the rows it upserts. The ingestor writes
through `AsyncSessionLocal`, so we repoint that at the in-memory test engine.
"""
import pytest

from app.services import ingestor as ingestor_module
from app.services.ingestor import HorizonIngestor
from app.models.entities import (
    ThreatStatus,
    TokenReputation,
    WalletReputation,
)

# A valid Stellar public key that is NOT the real Circle USDC issuer.
FAKE_ISSUER = "G" + "B" * 55
SENDER = "G" + "C" * 55
RECEIVER = "G" + "D" * 55


@pytest.fixture
def patched_ingestor(session_factory, monkeypatch):
    """An ingestor whose DB writes land in the test engine."""
    monkeypatch.setattr(ingestor_module, "AsyncSessionLocal", session_factory)
    return HorizonIngestor()


def _payment(**overrides):
    base = {
        "type": "payment",
        "from": SENDER,
        "to": RECEIVER,
        "amount": "100.0",
        "asset_type": "native",
        "transaction_hash": "abc123",
        "created_at": "2026-08-07T12:00:00Z",
        "paging_token": "1",
        "transaction": {"memo": None, "memo_type": "none"},
    }
    base.update(overrides)
    return base


async def test_impersonation_token_flagged(patched_ingestor, session_factory):
    await patched_ingestor._process_payment(
        _payment(
            asset_type="credit_alphanum4",
            asset_code="USDC",
            asset_issuer=FAKE_ISSUER,
        )
    )

    async with session_factory() as db:
        token = await db.get(TokenReputation, f"USDC:{FAKE_ISSUER}")

    assert token is not None
    assert token.status == ThreatStatus.SUSPICIOUS
    assert token.category == "Impersonation Token"


async def test_legit_issuer_not_flagged(patched_ingestor, session_factory):
    # USDC from its real Circle issuer must not be flagged.
    real_issuer = ingestor_module.KNOWN_ANCHORS["USDC"]
    await patched_ingestor._process_payment(
        _payment(
            asset_type="credit_alphanum4",
            asset_code="USDC",
            asset_issuer=real_issuer,
        )
    )

    async with session_factory() as db:
        token = await db.get(TokenReputation, f"USDC:{real_issuer}")

    assert token is None


async def test_memo_phishing_dust_flagged(patched_ingestor, session_factory):
    await patched_ingestor._process_payment(
        _payment(
            amount="0.0000100",  # dust, below DUST_AMOUNT_THRESHOLD
            transaction={"memo": "Claim your free XLM airdrop", "memo_type": "text"},
        )
    )

    async with session_factory() as db:
        wallet = await db.get(WalletReputation, SENDER)

    assert wallet is not None
    assert wallet.status == ThreatStatus.SUSPICIOUS
    assert wallet.category == "Memo Phishing Sender"


async def test_benign_payment_not_flagged(patched_ingestor, session_factory):
    # Normal-value native payment with no memo — nothing should be written.
    await patched_ingestor._process_payment(_payment())

    async with session_factory() as db:
        assert await db.get(WalletReputation, SENDER) is None
        assert await db.get(WalletReputation, RECEIVER) is None


async def test_large_payment_with_memo_not_dust(patched_ingestor, session_factory):
    # Suspicious memo text but a normal (non-dust) amount — not memo phishing.
    await patched_ingestor._process_payment(
        _payment(
            amount="500.0",
            transaction={"memo": "Claim your free XLM airdrop", "memo_type": "text"},
        )
    )

    async with session_factory() as db:
        assert await db.get(WalletReputation, SENDER) is None


async def test_missing_created_at_does_not_crash(patched_ingestor, session_factory):
    # A record without created_at must not raise (velocity bookkeeping is skipped).
    payment = _payment()
    payment.pop("created_at")
    await patched_ingestor._process_payment(payment)  # should simply return
