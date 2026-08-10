"""Live on-chain wallet profiling endpoint tests.

Horizon is never actually contacted: we monkeypatch the module-level
`_fetch_raw` so the heuristic derivation is exercised deterministically.
"""
from datetime import datetime, timedelta, timezone

import pytest

from app.services import horizon
from conftest import API_PREFIX

VALID_ADDRESS = "G" + "A" * 55


def _iso(days_ago: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()


def _account(**overrides):
    base = {
        "balances": [{"asset_type": "native", "balance": "100.0000000"}],
        "signers": [{"key": VALID_ADDRESS, "weight": 1}],
        "subentry_count": 0,
        "thresholds": {"high_threshold": 0},
        "home_domain": None,
    }
    base.update(overrides)
    return base


async def test_onchain_invalid_address_returns_400(client):
    resp = await client.get(f"{API_PREFIX}/lookup/wallet/not-an-address/onchain")
    assert resp.status_code == 400


async def test_onchain_established_account(client, monkeypatch):
    async def fake_fetch(address):
        return {
            "account": _account(
                home_domain="lobstr.co",
                balances=[
                    {"asset_type": "native", "balance": "5000.0"},
                    {"asset_type": "credit_alphanum4", "balance": "10.0"},
                ],
            ),
            "created_at": _iso(400),
        }

    monkeypatch.setattr(horizon, "_fetch_raw", fake_fetch)

    resp = await client.get(f"{API_PREFIX}/lookup/wallet/{VALID_ADDRESS}/onchain")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["verdict"] == "unknown_established"
    assert body["risk_level"] == "info"
    assert body["profile"]["account_age_days"] >= 365
    assert body["profile"]["trustline_count"] == 1
    assert body["profile"]["has_home_domain"] is True


async def test_onchain_new_account_flags_caution(client, monkeypatch):
    async def fake_fetch(address):
        return {"account": _account(), "created_at": _iso(3)}

    monkeypatch.setattr(horizon, "_fetch_raw", fake_fetch)

    resp = await client.get(f"{API_PREFIX}/lookup/wallet/{VALID_ADDRESS}/onchain")
    assert resp.status_code == 200
    body = resp.json()
    assert body["verdict"] == "unknown_new"
    assert body["risk_level"] == "caution"


async def test_onchain_not_found_when_unfunded(client, monkeypatch):
    async def fake_fetch(address):
        return None

    monkeypatch.setattr(horizon, "_fetch_raw", fake_fetch)

    resp = await client.get(f"{API_PREFIX}/lookup/wallet/{VALID_ADDRESS}/onchain")
    assert resp.status_code == 200
    body = resp.json()
    assert body["verdict"] == "not_found"
    assert body["profile"]["funded"] is False


async def test_onchain_horizon_unavailable_degrades_gracefully(client, monkeypatch):
    async def fake_fetch(address):
        raise horizon.HorizonUnavailable("connection refused")

    monkeypatch.setattr(horizon, "_fetch_raw", fake_fetch)

    resp = await client.get(f"{API_PREFIX}/lookup/wallet/{VALID_ADDRESS}/onchain")
    assert resp.status_code == 200
    body = resp.json()
    assert body["verdict"] == "unavailable"
    assert body["profile"] is None
