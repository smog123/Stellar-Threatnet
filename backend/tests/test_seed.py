"""Guards for the development seed script (scripts/seed.py)."""

import re

from scripts.seed import PHISHING_DOMAINS, g_address

STELLAR_PUBLIC_KEY_RE = re.compile(r"^G[A-Z2-7]{55}$")


def test_g_address_is_valid_stellar_format():
    a = g_address("wallet:Stellar Community Staking Marathon scam receiver")
    assert STELLAR_PUBLIC_KEY_RE.match(a), a
    assert len(a) == 56


def test_g_address_is_deterministic():
    assert g_address("seed-a") == g_address("seed-a")
    assert g_address("seed-a") != g_address("seed-b")


def test_phishing_domains_are_ascii_and_unique():
    puny = [d for _, d, *_ in PHISHING_DOMAINS]
    assert len(puny) == len(set(puny))
    assert all(d == d.encode("ascii").decode("ascii") for d in puny)
