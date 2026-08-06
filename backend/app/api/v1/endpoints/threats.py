import re

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_roles
from app.core.ratelimit import limiter
from app.db.session import get_db
from app.models.entities import (
    IncidentSeverity,
    IncidentStatus,
    User,
    UserRole,
)
from app.schemas.threats import (
    AIQueryRequest,
    AIQueryResponse,
    DomainLookupResponse,
    GlobalStatsResponse,
    IncidentCreate,
    IncidentResponse,
    IncidentUpdate,
    LatestThreatItem,
    ModerateRequest,
    PaginatedIncidents,
    ReportCreate,
    ReportOut,
    SearchResults,
    SocOverviewResponse,
    TokenLookupResponse,
    VoteRequest,
    WalletLookupResponse,
)
from app.services.threat_engine import ThreatService

router = APIRouter()

STELLAR_PUBLIC_KEY_RE = re.compile(r"^G[A-Z2-7]{55}$")
DOMAIN_RE = re.compile(r"^(?=.{4,253}$)(?!-)[a-z0-9-]{1,63}(?<!-)(\.(?!-)[a-z0-9-]{1,63}(?<!-))*\.?$")
ASSET_CODE_RE = re.compile(r"^[A-Za-z0-9]{1,12}$")
ISSUER_RE = re.compile(r"^G[A-Z2-7]{55}$")


def _validated_address(address: str) -> str:
    if not STELLAR_PUBLIC_KEY_RE.match(address):
        raise HTTPException(status_code=400, detail="Invalid Stellar public key format (expected G... 56 chars)")
    return address


def _validated_domain(domain: str) -> str:
    clean = domain.lower().strip().rstrip(".")
    if not DOMAIN_RE.match(clean):
        raise HTTPException(status_code=400, detail="Invalid domain name format")
    return clean


# --------------------------------------------------------------------------- #
# Reputation lookups
# --------------------------------------------------------------------------- #
@router.get(
    "/lookup/wallet/{address}",
    response_model=WalletLookupResponse,
    summary="Lookup Stellar wallet reputation",
)
@limiter.limit("120/minute")
async def lookup_wallet(request: Request, address: str, db: AsyncSession = Depends(get_db)):
    """Retrieve reputation score, threat category, and explanation for a Stellar `G...` address."""
    address = _validated_address(address)
    result = await ThreatService.get_wallet_reputation(db, address)
    if result is None:
        raise HTTPException(status_code=404, detail="No threat data found for this address")
    return result


@router.get(
    "/lookup/domain/{domain}",
    response_model=DomainLookupResponse,
    summary="Lookup domain reputation",
)
@limiter.limit("120/minute")
async def lookup_domain(request: Request, domain: str, db: AsyncSession = Depends(get_db)):
    """Query reputation for phishing, fake wallets, and malicious token sale sites."""
    domain = _validated_domain(domain)
    result = await ThreatService.get_domain_reputation(db, domain)
    if result is None:
        raise HTTPException(status_code=404, detail="No threat data found for this domain")
    return result


@router.get(
    "/lookup/token/{asset_code}/{issuer}",
    response_model=TokenLookupResponse,
    summary="Lookup token reputation",
)
@limiter.limit("120/minute")
async def lookup_token(
    request: Request, asset_code: str, issuer: str, db: AsyncSession = Depends(get_db)
):
    """Query reputation and impersonation checks for a Stellar asset (`CODE:ISSUER`)."""
    if not ASSET_CODE_RE.match(asset_code) or not ISSUER_RE.match(issuer):
        raise HTTPException(status_code=400, detail="Invalid asset code or issuer format")
    result = await ThreatService.get_token_reputation(db, asset_code, issuer)
    if result is None:
        raise HTTPException(status_code=404, detail="No threat data found for this token")
    return result


# --------------------------------------------------------------------------- #
# Incidents
# --------------------------------------------------------------------------- #
@router.get("/incidents", response_model=PaginatedIncidents, summary="List incidents")
async def list_incidents(
    status: IncidentStatus | None = Query(None),
    severity: IncidentSeverity | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Timeline of attacks, scams, phishing campaigns, and contract vulnerabilities."""
    total, items = await ThreatService.list_incidents(db, status, severity, limit, offset)
    return PaginatedIncidents(total=total, offset=offset, limit=limit, items=items)


@router.get("/incidents/{incident_id}", response_model=IncidentResponse, summary="Get an incident")
async def get_incident(incident_id: str, db: AsyncSession = Depends(get_db)):
    result = await ThreatService.get_incident(db, incident_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return result


@router.post("/incidents", response_model=IncidentResponse, status_code=201, summary="Create an incident")
async def create_incident(
    payload: IncidentCreate,
    user: User = Depends(require_roles(UserRole.ANALYST, UserRole.MODERATOR, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Create a security incident entry (analysts, moderators, admins)."""
    return await ThreatService.create_incident(db, user, payload)


@router.patch("/incidents/{incident_id}", response_model=IncidentResponse, summary="Update an incident")
async def update_incident(
    incident_id: str,
    payload: IncidentUpdate,
    user: User = Depends(require_roles(UserRole.MODERATOR, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Update an incident's status, severity, or details (moderators, admins)."""
    result = await ThreatService.update_incident(db, user, incident_id, payload)
    if result is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return result


# --------------------------------------------------------------------------- #
# Feed, latest threats, stats, search
# --------------------------------------------------------------------------- #
@router.get("/threats/latest", response_model=list[LatestThreatItem], summary="Latest threats")
async def latest_threats(
    limit: int = Query(10, ge=1, le=50), db: AsyncSession = Depends(get_db)
):
    """Most recently updated non-trusted wallets, domains, and tokens."""
    return await ThreatService.latest_threats(db, limit)


@router.get("/feed", summary="Download the threat feed (CSV)")
@limiter.limit("30/minute")
async def download_feed(request: Request, db: AsyncSession = Depends(get_db)):
    """Machine-readable CSV of all tracked wallets, domains, and tokens."""
    csv_data = await ThreatService.feed_csv(db)
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=threatnet-feed.csv"},
    )


@router.get("/stats", response_model=GlobalStatsResponse, summary="Global statistics")
async def get_global_statistics(db: AsyncSession = Depends(get_db)):
    """Aggregate dashboard metrics: threats by type, incidents, pending reports."""
    return await ThreatService.get_stats(db)


@router.get(
    "/stats/overview",
    response_model=SocOverviewResponse,
    summary="Security Operations Center overview",
)
@limiter.limit("60/minute")
async def soc_overview(request: Request, db: AsyncSession = Depends(get_db)):
    """Single-payload SOC dashboard: network posture, threat landscape, active campaigns,
    latest threats, and recent community reports."""
    return await ThreatService.get_soc_overview(db)


@router.get("/search", response_model=SearchResults, summary="Search across entities")
async def search(
    q: str = Query(..., min_length=2, max_length=128),
    type: str | None = Query(None, description="Comma-separated: wallet,domain,token,incident"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Full-text-style search across wallets, domains, tokens, and incidents."""
    return await ThreatService.search(db, q, type, limit)


# --------------------------------------------------------------------------- #
# Community reports & moderation queue
# --------------------------------------------------------------------------- #
@router.post("/reports", response_model=ReportOut, status_code=201, summary="Submit a community report")
async def submit_report(
    payload: ReportCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Report a malicious wallet, phishing site, or fake token. Queued for moderation."""
    if payload.target_type not in ("wallet", "domain", "token"):
        raise HTTPException(status_code=422, detail="target_type must be wallet, domain, or token")
    # Validate the target format up front so reports can never create garbage entities.
    if payload.target_type == "wallet":
        _validated_address(payload.target_value)
    elif payload.target_type == "domain":
        _validated_domain(payload.target_value)
    else:
        code, sep, _issuer = payload.target_value.partition(":")
        if not sep or not ASSET_CODE_RE.match(code.strip()):
            raise HTTPException(status_code=422, detail="Token target must be CODE:ISSUER")
    return await ThreatService.submit_report(db, user, payload)


@router.get("/reports/queue", response_model=list[ReportOut], summary="Moderation queue")
async def moderation_queue(
    user: User = Depends(require_roles(UserRole.MODERATOR, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Pending community reports awaiting review (moderators, admins)."""
    return await ThreatService.list_pending_reports(db)


@router.post("/reports/{report_id}/vote", response_model=ReportOut, summary="Vote on a report")
async def vote_report(
    report_id: str,
    payload: VoteRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upvote or downvote a pending report (reputation-weighted consensus signal)."""
    result = await ThreatService.vote_report(db, user, report_id, payload.vote == "up")
    if result is None:
        raise HTTPException(status_code=404, detail="Report not found or already moderated")
    return result


@router.post("/reports/{report_id}/moderate", response_model=ReportOut, summary="Moderate a report")
async def moderate_report(
    report_id: str,
    payload: ModerateRequest,
    user: User = Depends(require_roles(UserRole.MODERATOR, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Approve (attaches evidence + recomputes reputation) or reject a report."""
    result = await ThreatService.moderate_report(
        db,
        user,
        report_id,
        payload.action,
        payload.moderation_note,
        payload.proof_type,
        payload.confidence,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Report not found or already moderated")
    return result


# --------------------------------------------------------------------------- #
# AI threat assistant
# --------------------------------------------------------------------------- #
@router.post("/ai/query", response_model=AIQueryResponse, summary="Ask the AI threat assistant")
@limiter.limit("20/minute")
async def query_ai_threat_assistant(
    request: Request, payload: AIQueryRequest, db: AsyncSession = Depends(get_db)
):
    """Ask about a wallet, a phishing campaign, or today's threats. Evidence-based, never overconfident."""
    return await ThreatService.process_ai_assistant_query(db, payload.query)
