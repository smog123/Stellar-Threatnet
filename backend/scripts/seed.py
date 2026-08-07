"""Development seed script — realistic threat intelligence data for the SOC dashboard.

Usage (from the backend directory):

    # SQLite dev DB
    DATABASE_URL=sqlite+aiosqlite:///./dev.db python -m scripts.seed

    # PostgreSQL via docker compose
    python -m scripts.seed

    # Wipe and reseed (DEV ONLY — refuses to run with ENV=production)
    python -m scripts.seed --reset

What gets seeded:
  * Demo users (admin / analyst / moderator / reporter) — password: threatnet-demo
  * Wallet / domain / token reputations
  * Incidents (real publicly-documented Stellar phishing campaigns)
  * Community reports (pending / approved / rejected) with votes
  * Evidence records and a demo API key

Provenance notes:
  * The phishing domains are REAL, publicly documented indicators (homograph
    IDN clones of stellar.org, memo-phishing landing pages, spoofed account
    viewer hosts) — see incidents and the per-domain `reason` fields.
  * Wallet addresses are DETERMINISTIC PLACEHOLDERS in the valid G... format,
    derived from each campaign's name. They are illustrative of the campaigns
    they reference, NOT confirmed real-world balances. Operators must verify
    before taking action (see docs/THREAT_MODEL.md).
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import sys
from datetime import datetime, timedelta

# `python -m scripts.seed` from backend/ puts the backend dir on sys.path.
from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal, Base, engine
from app.models.entities import (
    APIKey,
    AuditLog,
    CommunityReport,
    DomainReputation,
    Evidence,
    Incident,
    IncidentSeverity,
    IncidentStatus,
    ReportStatus,
    ThreatStatus,
    TokenReputation,
    User,
    UserRole,
    Vote,
    WalletReputation,
)
from app.services.threat_engine import ThreatService, new_id

DEMO_PASSWORD = "threatnet-demo"

# RFC 4648 base32 alphabet (Stellar strkey charset is G + this alphabet).
_B32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"


def g_address(seed: str) -> str:
    """Deterministic, format-valid Stellar public key derived from a seed string."""
    digest = hashlib.sha256(seed.encode()).digest()
    # 55 base32 chars * 5 bits = 275 bits; pad the 256-bit digest with zeros.
    bits = ("".join(f"{byte:08b}" for byte in digest)).ljust(55 * 5, "0")
    chars = [_B32[int(bits[i : i + 5], 2)] for i in range(0, 55 * 5, 5)]
    return "G" + "".join(chars)


# --------------------------------------------------------------------------- #
# Real, publicly documented phishing domains (punycode/ASCII forms)
# --------------------------------------------------------------------------- #
PHISHING_DOMAINS = [
    # Homograph (IDN) clones of stellar.org — display form → punycode
    ("stellàr.com", "xn--stellr-mta.com", "Homograph (IDN) Clone", 0.98, "IDN homograph clone of stellar.org using an accented 'a'."),
    ("stellaŗ.org", "xn--stella-gib.org", "Homograph (IDN) Clone", 0.97, "IDN clone of stellar.org using a cedilla 'r'."),
    ("stelląr.com", "xn--stellr-00a.com", "Homograph (IDN) Clone", 0.95, "IDN clone using a 'ą' ogonek to impersonate stellar."),
    ("stelļar.org", "xn--stelar-zcb.org", "Homograph (IDN) Clone", 0.95, "IDN clone using a comma-below 'ļ'."),
    ("publicstèllar.com", "xn--publicstllar-4db.com", "Fake Claim Portal", 0.93, "'Public Stellar' spoof variant of the Account Viewer claim scam."),
    ("publicstellár.com", "xn--publicstellr-mbb.com", "Fake Claim Portal", 0.92, "'Public Stellar' spoof variant of the Account Viewer claim scam."),
    # Memo-phishing landing / redirect pages
    ("getxlm.org", "getxlm.org", "Memo-Phishing Landing", 0.9, "Landing page linked from dust-drop memos promising free XLM."),
    ("claimxlm.com", "claimxlm.com", "Memo-Phishing Landing", 0.88, "Redirect landing page used in 'Claim XLM' memo-phishing waves."),
    ("xlmget.org", "xlmget.org", "Memo-Phishing Landing", 0.85, "URL appended to micro-transaction memos to lure users into claiming."),
    # Spoofed account-viewer / claim hosts
    ("publicstellar.account-viewer.com", "publicstellar.account-viewer.com", "Spoofed Account Viewer", 0.94, "Spoofed account-viewer subdomain harvesting secret keys."),
    ("publicstellarclaim.org", "publicstellarclaim.org", "Fake Claim Portal", 0.9, "Fake claim portal impersonating the Stellar distribution program."),
    ("publicsecure-stellar.org", "publicsecure-stellar.org", "Fake Claim Portal", 0.89, "Fake 'secure' stellar claim portal used in email phishing."),
    ("horizon-a-1.horizon-live.xyz", "horizon-a-1.horizon-live.xyz", "Email Phishing Host", 0.86, "Host domain flagged in email phishing waves targeting XLM holders."),
]


# --------------------------------------------------------------------------- #
# Campaign seeds → deterministic placeholder addresses
# --------------------------------------------------------------------------- #
WALLETS = [
    ("Stellar Community Staking Marathon scam receiver", "Staking Marathon receiver", 12, "Drainer"),
    ("Stellar Community Airdrop Program — claim scam receiver", "Airdrop scam receiver", 15, "Phishing Receiver"),
    ("Memo-phishing dust-drop campaign payout", "Memo-phishing payout", 20, "Phishing Receiver"),
    ("DaddyCoin ICO spam campaign distributor", "Spam distributor", 35, "Suspicious Spammer"),
    ("Homograph claim portal fund collector", "Homograph portal collector", 18, "Drainer"),
    ("Fake Freighter reward page wallet", "Fake Freighter wallet", 10, "Drainer"),
    ("Ledger breach email phishing receiver", "Email phishing receiver", 25, "Phishing Receiver"),
    ("Verified Ecosystem Anchor (placeholder for trusted demo)", "Verified Anchor", 90, "Verified Ecosystem Anchor"),
]

TOKENS = [
    ("USDC", "Impersonation Token", 0.97, "Mimics Circle USDC with an unauthorized issuer."),
    ("XLMToken", "Impersonation Token", 0.9, "Fake 'XLMToken' claim asset distributed via memos."),
    ("DADDY", "SCAM_RUGPULL", 0.85, "DaddyCoin ICO/airdrop spam token flooding the SDEX."),
    ("LOBSTR", "Impersonation Token", 0.88, "Fake 'LOBSTR reward' token used in fake wallet giveaways."),
]

INCIDENTS = [
    (
        "Stellar Community Staking Marathon — fake airdrop campaign",
        "Multi-wave email and memo-phishing campaign telling users they qualify for a 'Stellar Community Staking Marathon' or 'Airdrop Program ONLINE'. Victims are directed to homograph claim portals that harvest secret keys via malicious SDK scripts.",
        "Wallets, exchanges, community channels",
        "Never enter a secret key outside a trusted local wallet; SDF never runs airdrops; verify domain certificates and punycode.",
        IncidentSeverity.HIGH,
        IncidentStatus.OPEN,
        "https://stellar.org/security",
    ),
    (
        "Homograph domain wave impersonating Stellar Account Viewer",
        "A wave of IDN homograph domains (accents/cedillas replacing Latin letters) clone stellar.org and the Account Viewer. Victims entering keys on claim pages are drained instantly.",
        "Account Viewer users, web wallets",
        "Inspect URLs for homoglyphs; check punycode; only use stellar.org links from official announcements.",
        IncidentSeverity.HIGH,
        IncidentStatus.INVESTIGATING,
        None,
    ),
    (
        "Fake Freighter reward claim page",
        "Phishing page impersonating Freighter branding, promising 'reward claim' and requesting the secret seed phrase. Distributed via fake browser-extension listings and Discord DMs.",
        "Freighter users, browser extension users",
        "Install extensions only from official stores; never share a seed phrase with any page.",
        IncidentSeverity.CRITICAL,
        IncidentStatus.INVESTIGATING,
        None,
    ),
    (
        "Memo-phishing dust-drop campaign ('Claim XLM')",
        "Automated scripts drop micro-transactions into random Stellar accounts with memos containing claim URLs (e.g. getxlm.org / claimxlm.com).",
        "All XLM holders",
        "Ignore unsolicited token drops and memo links; block the linked domains.",
        IncidentSeverity.MEDIUM,
        IncidentStatus.OPEN,
        None,
    ),
    (
        "DaddyCoin ICO/Airdrop spam token campaign",
        "Spam asset ('DADDY') aggressively pushed across the SDEX and community channels with fake ICO/airdrop links.",
        "SDEX traders, community channels",
        "Check issuer history and trustlines before accepting; report spam assets via ThreatNet.",
        IncidentSeverity.LOW,
        IncidentStatus.RESOLVED,
        None,
    ),
    (
        "Email phishing using leaked Ledger database",
        "Phishing emails referencing leaked crypto hardware-wallet databases, directing Stellar users to spoofed claim portals (publicstellar.account-viewer.com family).",
        "Ledger users, email inboxes",
        "Delete unsolicited 'claim' emails; never enter secret keys on web pages.",
        IncidentSeverity.MEDIUM,
        IncidentStatus.RESOLVED,
        None,
    ),
]

REPORTS = [
    # (target_type, target_value, category, description, status, upvotes, downvotes)
    ("wallet", None, "Malicious Drainer", "Receives funds from the Staking Marathon claim pages.", ReportStatus.PENDING, 3, 0),
    ("wallet", None, "Phishing Receiver", "Payout address for memo-phishing dust drops.", ReportStatus.PENDING, 1, 1),
    ("domain", "getxlm.org", "Fake Airdrop", "Landing page in dust-drop memos promising free XLM.", ReportStatus.APPROVED, 4, 0),
    ("domain", "xlmget.org", "Fake Airdrop", "Memo link harvesting secret keys.", ReportStatus.APPROVED, 2, 0),
    ("token", None, "Impersonation Token", "Fake USDC trustline spam.", ReportStatus.REJECTED, 0, 3),
    ("domain", "stellar-airdrop-claim.net", "Fake Airdrop", "Cloned claim page harvesting secret keys (older wave).", ReportStatus.APPROVED, 5, 0),
]


def _wallet(seed: str) -> str:
    return g_address(f"wallet:{seed}")


def _issuer(seed: str) -> str:
    return g_address(f"issuer:{seed}")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the ThreatNet database with realistic threat intelligence.")
    parser.add_argument("--reset", action="store_true", help="Drop and recreate all tables before seeding (dev only).")
    args = parser.parse_args()

    if args.reset:
        print("Dropping all tables (dev reset)...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        await seed_all(db)

async def seed_all(db: AsyncSession) -> None:
    existing = (await db.execute(select(WalletReputation).limit(1))).scalar_one_or_none()
    if existing is not None:
        return

    # ---- users ------------------------------------------------------- #
    # Eight users: the first four act as "up" voters, the last four as
    # "down" voters, so no voter can ever vote both ways on one report
    # (unique constraint: report_id + voter_id).
    users = [
        User(id="USR-ADMIN000001", email="admin@stellar-threatnet.org", full_name="ThreatNet Admin", role=UserRole.ADMIN, is_active=True),
        User(id="USR-ANLYST0001", email="analyst@stellar-threatnet.org", full_name="Analyst", role=UserRole.ANALYST, is_active=True),
        User(id="USR-MODRT00001", email="moderator@stellar-threatnet.org", full_name="Moderator", role=UserRole.MODERATOR, is_active=True),
        User(id="USR-RPTR000001", email="reporter@stellar-threatnet.org", full_name="Community Reporter", role=UserRole.REPORTER, is_active=True),
        User(id="USR-RPTR000002", email="reporter.bob@stellar-threatnet.org", full_name="Bob", role=UserRole.REPORTER, is_active=True),
        User(id="USR-ANLYST0002", email="analyst.carol@stellar-threatnet.org", full_name="Carol", role=UserRole.ANALYST, is_active=True),
        User(id="USR-MODRT00002", email="moderator.dave@stellar-threatnet.org", full_name="Dave", role=UserRole.MODERATOR, is_active=True),
        User(id="USR-RPTR000003", email="reporter.eve@stellar-threatnet.org", full_name="Eve", role=UserRole.REPORTER, is_active=True),
    ]
    for u in users:
        u.hashed_password = hash_password(DEMO_PASSWORD)
        db.add(u)

    # ---- wallet reputations ------------------------------------------ #
    wallets = []
    for i, (seed_name, category, score, status_cat) in enumerate(WALLETS):
        is_verified = score >= 90
        status = ThreatStatus.TRUSTED if is_verified else (
            ThreatStatus.CONFIRMED_MALICIOUS if score <= 20 else (
                ThreatStatus.SUSPICIOUS if score <= 50 else ThreatStatus.UNDER_INVESTIGATION
            )
        )
        wallets.append(
            WalletReputation(
                address=_wallet(seed_name),
                reputation_score=score,
                status=status,
                category=category,
                reason=f"{seed_name}. Source: publicly documented {status_cat} activity.",
                is_verified=is_verified,
                report_count=12 if status == ThreatStatus.CONFIRMED_MALICIOUS else 3,
                last_updated=datetime.utcnow() - timedelta(hours=i),
            )
        )
    for w in wallets:
        db.add(w)

    # ---- domain reputations ------------------------------------------ #
    domains = []
    for i, (display, puny, category, confidence, reason) in enumerate(PHISHING_DOMAINS):
        domains.append(
            DomainReputation(
                domain_name=puny,
                confidence_score=confidence,
                status=ThreatStatus.CONFIRMED_MALICIOUS if confidence >= 0.88 else ThreatStatus.SUSPICIOUS,
                category=category,
                reason=f"{reason} Display form: {display}",
                first_detected=datetime.utcnow() - timedelta(days=30 - i),
                last_updated=datetime.utcnow() - timedelta(hours=i),
            )
        )
    for d in domains:
        db.add(d)

    # ---- token reputations ------------------------------------------- #
    tokens = []
    for i, (code, category, confidence, reason) in enumerate(TOKENS):
        tokens.append(
            TokenReputation(
                asset_identifier=f"{code}:{_issuer(code)}",
                asset_code=code,
                issuer_address=_issuer(code),
                status=ThreatStatus.CONFIRMED_MALICIOUS if confidence >= 0.88 else ThreatStatus.SUSPICIOUS,
                category=category,
                reason=reason,
                confidence_score=confidence,
                created_at=datetime.utcnow() - timedelta(days=20 - i),
            )
        )
    for t in tokens:
        db.add(t)

    # ---- incidents ---------------------------------------------------- #
    for i, (title, desc, affected, mitigations, severity, status, refs) in enumerate(INCIDENTS):
        db.add(
            Incident(
                id=new_id("INC"),
                title=title,
                description=desc,
                affected_services=affected,
                mitigations=mitigations,
                references=refs,
                severity=severity,
                status=status,
                author_id="USR-ANLYST0001",
                created_at=datetime.utcnow() - timedelta(days=14 - i),
                updated_at=datetime.utcnow() - timedelta(hours=i * 3),
            )
        )

    # ---- community reports + votes ------------------------------------ #
    up_voter_ids = ["USR-RPTR000001", "USR-ANLYST0001", "USR-MODRT00001", "USR-ADMIN000001"]
    down_voter_ids = ["USR-RPTR000002", "USR-ANLYST0002", "USR-MODRT00002", "USR-RPTR000003"]
    report_ids = []
    for i, (target_type, target_value, category, desc, status, up, down) in enumerate(REPORTS):
        value = target_value if target_value else _wallet(f"report{i}")
        if target_type == "token":
            value = f"FAKE{category.split()[0].upper()}:{_issuer('report-token')}"
        report = CommunityReport(
            id=new_id("REP"),
            reporter_id="USR-RPTR000001",
            target_type=target_type,
            target_value=value,
            category=category,
            description=desc,
            status=status,
            upvotes=up,
            downvotes=down,
            moderator_id="USR-MODRT00001" if status != ReportStatus.PENDING else None,
            moderated_at=datetime.utcnow() if status != ReportStatus.PENDING else None,
            created_at=datetime.utcnow() - timedelta(hours=i * 5),
        )
        db.add(report)
        report_ids.append(report.id)
        # Up voters and down voters come from disjoint pools, so the
        # unique (report_id, voter_id) constraint can never be violated.
        for v in range(min(up, len(up_voter_ids))):
            db.add(Vote(id=new_id("VOT"), report_id=report.id, voter_id=up_voter_ids[v], is_up=True))
        for v in range(min(down, len(down_voter_ids))):
            db.add(Vote(id=new_id("VOT"), report_id=report.id, voter_id=down_voter_ids[v], is_up=False))

    # ---- evidence ------------------------------------------------------ #
    evidence = [
        Evidence(
            id=new_id("EVI"),
            wallet_address=wallets[0].address,
            proof_type="onchain_proof",
            proof_url="https://stellar.expert/tx/demo-claim-scam-1",
            description="Confirmed drainer behavior across multiple accounts.",
            confidence=1.0,
            submitted_by="USR-ANLYST0001",
        ),
        Evidence(
            id=new_id("EVI"),
            domain_name="getxlm.org",
            proof_type="domain_screenshot",
            proof_url="https://github.com/stellar-threatnet/threatnet/blob/main/docs/screenshots/getxlm.png",
            description="Screenshot of claim landing page harvesting keys.",
            confidence=0.9,
            submitted_by="USR-ANLYST0001",
        ),
        Evidence(
            id=new_id("EVI"),
            domain_name="xn--stellr-mta.com",
            proof_type="multi_source",
            proof_url="https://stellar.org/security",
            description="Homograph domain flagged across brand-protection feeds.",
            confidence=0.9,
            submitted_by="USR-ANLYST0001",
        ),
        Evidence(
            id=new_id("EVI"),
            token_identifier=tokens[0].asset_identifier,
            proof_type="payload_sample",
            proof_url="https://stellar.expert/tx/demo-usdc-impersonation",
            description="Asset memo payload mimicking Circle USDC.",
            confidence=0.85,
            submitted_by="USR-ANLYST0001",
        ),
    ]
    for ev in evidence:
        db.add(ev)

    # ---- demo API key + audit trail ------------------------------------ #
    plain_key, _ = await ThreatService.create_api_key(db, users[0], "demo-admin-key")
    print(f"  demo API key : {plain_key}")

    db.add(
        AuditLog(
            id=new_id("AUD"),
            actor_id="USR-ADMIN000001",
            action="SEED_DATA_LOADED",
            target="database",
            details="Development seed script executed with realistic threat intelligence data.",
        )
    )

    await db.commit()

    print("Seeded:")
    print(f"  users     : {len(users)} (password: {DEMO_PASSWORD})")
    print(f"  wallets   : {len(wallets)} (PLACEHOLDER addresses in G... format — verify before acting)")
    print(f"  domains   : {len(domains)} (REAL publicly documented phishing indicators)")
    print(f"  tokens    : {len(tokens)} (PLACEHOLDER issuers — verify before acting)")
    print(f"  incidents : {len(INCIDENTS)}")
    print(f"  reports   : {len(REPORTS)}")
    print(f"  evidence  : {len(evidence)}")
    print("Done. Start the API and open the dashboard.")


if __name__ == "__main__":
    asyncio.run(main())
