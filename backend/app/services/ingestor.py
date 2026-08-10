"""Live Stellar Horizon ledger ingestor — detects threats in real time.

Streams payment operations from Horizon, identifies:
  - Memo phishing (dust drops with malicious URLs)
  - Wallet drainers (rapid sequential transfers to a sink)
  - Asset impersonation (fake USDC/BTC/etc. with wrong issuers)

Runs as a background asyncio task in production; disabled during tests.
"""
from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime
from typing import Any, Optional

import httpx

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.entities import (
    ThreatStatus,
    TokenReputation,
    WalletReputation,
)

# Patterns for memo phishing detection
SUSPICIOUS_MEMO_PATTERNS = [
    r"claim.*xlm",
    r"free.*xlm",
    r"airdrop.*stellar",
    r"reward.*stellar",
    r"https?://[a-z0-9-]+\.(com|org|net|xyz)",  # URLs in memos
]
MEMO_PATTERN = re.compile("|".join(SUSPICIOUS_MEMO_PATTERNS), re.IGNORECASE)

# Known legit issuers (production anchors) — tokens from other issuers are flagged
KNOWN_ANCHORS = {
    "USDC": "GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN",  # Circle
    "BTC": "GAUTUYY2THLF7SGITDFMXJVYH3LHDSMGEAKSBU267M2K7A3W543CKUEF",  # Ultra Stellar
    "AQUA": "GBNZILSTVQZ4R7IKQDGHYGY2QXL5QOFJYQMXPKWRRM5PAV7Y4M67AQUA",  # AquaNetwork
}

# Detection thresholds
DUST_AMOUNT_THRESHOLD = 0.001  # XLM — micro-payments likely spam
DRAINER_VELOCITY_WINDOW = 300  # seconds — track wallets that receive then drain quickly


class HorizonIngestor:
    """Streams Stellar Horizon operations and upserts detected threats."""

    def __init__(self):
        self.running = False
        self.last_cursor: Optional[str] = None
        # Track recent receivers for drainer velocity detection
        self.recent_receivers: dict[str, list[float]] = {}

    async def start(self):
        """Launch the background streaming task."""
        if self.running:
            return
        self.running = True
        print("[Ingestor] Starting Horizon ledger monitor...")
        asyncio.create_task(self._stream_loop())

    async def stop(self):
        """Graceful shutdown signal."""
        self.running = False
        print("[Ingestor] Stopping Horizon ledger monitor...")

    async def _stream_loop(self):
        """Main streaming loop — resilient to network errors."""
        while self.running:
            try:
                await self._stream_payments()
            except Exception as e:
                print(f"[Ingestor] Stream error: {e}. Reconnecting in 30s...")
                await asyncio.sleep(30)

    async def _stream_payments(self):
        """Stream live payment operations from Horizon via SSE.

        Horizon only streams when the client sends ``Accept: text/event-stream``;
        ``cursor=now`` tails live traffic (rather than replaying from genesis) and
        ``join=transactions`` embeds the parent transaction so memos are available.
        """
        base = settings.STELLAR_HORIZON_URL.rstrip("/")
        params = {
            "cursor": self.last_cursor or "now",
            "join": "transactions",
            "include_failed": "false",
            "limit": 200,
        }
        headers = {"Accept": "text/event-stream"}

        timeout = httpx.Timeout(120.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "GET", f"{base}/payments", params=params, headers=headers
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not self.running:
                        return
                    if not line.strip() or line.startswith(":"):
                        continue  # SSE keep-alive or comment
                    if line.startswith("data:"):
                        data_json = line[5:].strip()
                        if not data_json:
                            continue
                        try:
                            payment = json.loads(data_json)
                        except json.JSONDecodeError:
                            continue
                        # The stream opens with an `event: open` / `data: "hello"`
                        # handshake frame — skip anything that isn't a record.
                        if not isinstance(payment, dict):
                            continue
                        try:
                            await self._process_payment(payment)
                            self.last_cursor = payment.get("paging_token")
                        except Exception as e:
                            print(f"[Ingestor] Failed to process payment: {e}")

    async def _process_payment(self, payment: dict[str, Any]):
        """Analyze one payment for threat signals."""
        op_type = payment.get("type")
        if op_type != "payment":
            return  # Only care about payments for now

        source = payment.get("from")
        destination = payment.get("to")
        amount = float(payment.get("amount", "0"))
        asset_type = payment.get("asset_type", "native")
        asset_code = payment.get("asset_code")
        asset_issuer = payment.get("asset_issuer")
        transaction = payment.get("transaction") or {}
        memo = transaction.get("memo")
        memo_type = transaction.get("memo_type")
        tx_hash = payment.get("transaction_hash")
        created_at = payment.get("created_at")

        # Signal 1: Memo phishing (dust drops with suspicious text/URLs)
        if memo and memo_type in ("text", "MEMO_TEXT") and amount < DUST_AMOUNT_THRESHOLD:
            if MEMO_PATTERN.search(memo):
                await self._flag_memo_phishing(source, memo, tx_hash, created_at)

        # Signal 2: Asset impersonation (non-anchor issuers of major tokens)
        if asset_type != "native" and asset_code and asset_issuer:
            expected = KNOWN_ANCHORS.get(asset_code)
            if expected and asset_issuer != expected:
                await self._flag_impersonation_token(asset_code, asset_issuer, tx_hash, created_at)

        # Signal 3: Wallet drainer velocity (receivers that quickly forward out)
        # (Simplified: track receivers; a full implementation would correlate outbound ops)
        if destination and created_at:
            try:
                now = datetime.fromisoformat(created_at.replace("Z", "+00:00")).timestamp()
            except ValueError:
                return  # Unparseable timestamp — skip velocity bookkeeping
            receivers = self.recent_receivers.setdefault(destination, [])
            receivers.append(now)
            # Prune old entries outside the velocity window
            cutoff = now - DRAINER_VELOCITY_WINDOW
            receivers = [t for t in receivers if t > cutoff]
            if receivers:
                self.recent_receivers[destination] = receivers
            else:
                # Bound memory: forget wallets with no recent activity
                self.recent_receivers.pop(destination, None)
            # If >5 receives in the window, flag as suspicious
            if len(receivers) > 5:
                await self._flag_suspicious_wallet(destination, "High-velocity receiver", tx_hash, created_at)

    async def _flag_memo_phishing(self, source: str, memo: str, tx_hash: str, created_at: str):
        """Upsert a wallet flagged for memo phishing."""
        async with AsyncSessionLocal() as db:
            existing = await db.get(WalletReputation, source)
            if existing:
                return  # Already tracked
            wallet = WalletReputation(
                address=source,
                reputation_score=40,  # Suspicious range
                status=ThreatStatus.SUSPICIOUS,
                category="Memo Phishing Sender",
                reason=f"Sent dust payment with suspicious memo: '{memo[:80]}...'",
                is_verified=False,
                report_count=1,
                last_updated=datetime.utcnow(),
            )
            db.add(wallet)
            await db.commit()
            print(f"[Ingestor] Flagged memo phishing: {source} (memo: {memo[:40]}...)")

    async def _flag_impersonation_token(self, code: str, issuer: str, tx_hash: str, created_at: str):
        """Upsert a token flagged for impersonation."""
        identifier = f"{code}:{issuer}"
        async with AsyncSessionLocal() as db:
            existing = await db.get(TokenReputation, identifier)
            if existing:
                return
            token = TokenReputation(
                asset_identifier=identifier,
                asset_code=code,
                issuer_address=issuer,
                status=ThreatStatus.SUSPICIOUS,
                category="Impersonation Token",
                reason=f"Asset code '{code}' issued by unrecognized issuer (expected anchor: {KNOWN_ANCHORS.get(code)}).",
                is_verified=False,
                confidence_score=0.85,
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow(),
            )
            db.add(token)
            await db.commit()
            print(f"[Ingestor] Flagged impersonation token: {identifier}")

    async def _flag_suspicious_wallet(self, address: str, reason: str, tx_hash: str, created_at: str):
        """Upsert a wallet flagged for suspicious activity."""
        async with AsyncSessionLocal() as db:
            existing = await db.get(WalletReputation, address)
            if existing:
                return
            wallet = WalletReputation(
                address=address,
                reputation_score=50,
                status=ThreatStatus.UNDER_INVESTIGATION,
                category="Suspicious Activity",
                reason=reason,
                is_verified=False,
                report_count=1,
                last_updated=datetime.utcnow(),
            )
            db.add(wallet)
            await db.commit()
            print(f"[Ingestor] Flagged suspicious wallet: {address} ({reason})")


# Singleton instance
_ingestor: Optional[HorizonIngestor] = None


async def start_ingestor():
    """Start the global ingestor instance."""
    global _ingestor
    if _ingestor is None:
        _ingestor = HorizonIngestor()
    await _ingestor.start()


async def stop_ingestor():
    """Stop the global ingestor instance."""
    global _ingestor
    if _ingestor:
        await _ingestor.stop()
