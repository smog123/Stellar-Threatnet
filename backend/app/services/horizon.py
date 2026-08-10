"""Live on-chain wallet profiling via Stellar Horizon.

Used as a fallback when a wallet has no entry in the threat database: instead of
returning a bare "unknown", we read the account's live on-chain footprint and
derive a soft, clearly-labelled heuristic. Account maturity is context, NOT a
safety guarantee — an aged account can still be malicious and a fresh one can be
perfectly legitimate (see docs/THREAT_MODEL.md).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.core.config import settings
from app.schemas.threats import OnChainProfile, WalletOnChainResponse

_NEW_ACCOUNT_DAYS = 30


class HorizonUnavailable(Exception):
    """Horizon could not be reached or returned an unexpected error."""


async def _fetch_raw(address: str) -> Optional[dict[str, Any]]:
    """Return {account, created_at} for a funded account, None if not found.

    Raises HorizonUnavailable on network/timeout/5xx errors so the caller can
    degrade gracefully instead of surfacing a 500.
    """
    base = settings.STELLAR_HORIZON_URL.rstrip("/")
    timeout = httpx.Timeout(settings.HORIZON_TIMEOUT_SECONDS)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            acct = await client.get(f"{base}/accounts/{address}")
            if acct.status_code == 404:
                return None
            acct.raise_for_status()
            account = acct.json()

            created_at: Optional[str] = None
            ops = await client.get(
                f"{base}/accounts/{address}/operations",
                params={"order": "asc", "limit": 1},
            )
            if ops.status_code == 200:
                records = ops.json().get("_embedded", {}).get("records", [])
                if records:
                    created_at = records[0].get("created_at")
    except (httpx.HTTPError, ValueError) as exc:
        raise HorizonUnavailable(str(exc)) from exc

    return {"account": account, "created_at": created_at}


def _age_days(created_at: Optional[str]) -> Optional[int]:
    if not created_at:
        return None
    try:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except ValueError:
        return None
    return max(0, (datetime.now(timezone.utc) - created).days)


def _derive(address: str, raw: Optional[dict[str, Any]]) -> WalletOnChainResponse:
    if raw is None:
        return WalletOnChainResponse(
            address=address,
            verdict="not_found",
            risk_level="neutral",
            summary=(
                "This address has never been funded on the Stellar public network, so it "
                "has no on-chain history to evaluate. It may exist only on testnet, or be a "
                "brand-new key that has never received funds."
            ),
            signals=["Account not found on Horizon (unfunded)"],
            profile=OnChainProfile(exists=False, funded=False),
        )

    account = raw["account"]
    balances = account.get("balances", [])
    native = next((b for b in balances if b.get("asset_type") == "native"), None)
    native_balance = native.get("balance") if native else "0"
    trustlines = [b for b in balances if b.get("asset_type") != "native"]
    signers = account.get("signers", [])
    home_domain = account.get("home_domain")
    thresholds = account.get("thresholds", {})
    age = _age_days(raw.get("created_at"))

    profile = OnChainProfile(
        exists=True,
        funded=True,
        native_balance=native_balance,
        account_age_days=age,
        num_subentries=account.get("subentry_count"),
        trustline_count=len(trustlines),
        signer_count=len(signers),
        thresholds_high=thresholds.get("high_threshold"),
        home_domain=home_domain,
        has_home_domain=bool(home_domain),
    )

    signals: list[str] = []
    if age is not None:
        signals.append(f"Account is ~{age} day(s) old")
    if home_domain:
        signals.append(f"Declares home_domain '{home_domain}' (SEP-0001)")
    if len(signers) > 1:
        signals.append(f"Multisig: {len(signers)} signers configured")
    if trustlines:
        signals.append(f"Holds {len(trustlines)} trustline(s)")

    is_new = age is not None and age < _NEW_ACCOUNT_DAYS
    if is_new:
        return WalletOnChainResponse(
            address=address,
            verdict="unknown_new",
            risk_level="caution",
            summary=(
                "No threat reports exist for this wallet, and on-chain it looks recently "
                "created with limited history. New accounts are common for drainer and "
                "airdrop-scam wallets — verify the counterparty independently before signing."
            ),
            signals=signals or ["Recently created account with minimal footprint"],
            profile=profile,
        )

    return WalletOnChainResponse(
        address=address,
        verdict="unknown_established",
        risk_level="info",
        summary=(
            "No threat reports exist for this wallet. On-chain it shows an established "
            "footprint (age and activity below). This is context, not a safety guarantee — "
            "an aged account can still be malicious, so continue to verify before transacting."
        ),
        signals=signals or ["Established account with on-chain history"],
        profile=profile,
    )


async def fetch_account_profile(address: str) -> WalletOnChainResponse:
    try:
        raw = await _fetch_raw(address)
    except HorizonUnavailable:
        return WalletOnChainResponse(
            address=address,
            verdict="unavailable",
            risk_level="neutral",
            summary=(
                "The Stellar Horizon network could not be reached to profile this address. "
                "No threat reports exist in ThreatNet either. Treat as unknown and verify "
                "independently."
            ),
            signals=["Live on-chain lookup temporarily unavailable"],
            profile=None,
        )
    return _derive(address, raw)
