from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.entities import (
    IncidentSeverity,
    IncidentStatus,
    ReportStatus,
    ThreatStatus,
    UserRole,
)


# --------------------------------------------------------------------------- #
# Reputation lookups
# --------------------------------------------------------------------------- #
class WalletLookupResponse(BaseModel):
    address: str
    reputation_score: int
    status: ThreatStatus
    category: Optional[str] = None
    reason: str
    report_count: int
    last_updated: datetime


class DomainLookupResponse(BaseModel):
    domain_name: str
    confidence_score: float
    status: ThreatStatus
    category: str
    reason: str
    ip_address: Optional[str] = None
    first_detected: datetime


class TokenLookupResponse(BaseModel):
    asset_identifier: str
    asset_code: str
    issuer_address: str
    status: ThreatStatus
    category: str
    reason: str
    confidence_score: float


# --------------------------------------------------------------------------- #
# Live on-chain wallet profile (Stellar Horizon)
# --------------------------------------------------------------------------- #
class OnChainProfile(BaseModel):
    """Facts read directly from Horizon for an account (no threat opinion)."""
    exists: bool
    funded: bool
    native_balance: Optional[str] = None
    account_age_days: Optional[int] = None
    num_subentries: Optional[int] = None
    trustline_count: Optional[int] = None
    signer_count: Optional[int] = None
    thresholds_high: Optional[int] = None
    home_domain: Optional[str] = None
    has_home_domain: bool = False


class WalletOnChainResponse(BaseModel):
    """Heuristic verdict for a wallet NOT in the threat DB, derived from live
    on-chain signal. `verdict` is intentionally soft ("no reports" is not proof
    of safety) — see docs/THREAT_MODEL.md.
    """
    address: str
    source: str = "stellar_horizon"
    verdict: str  # unknown_new | unknown_established | unfunded | not_found | unavailable
    risk_level: str  # info | caution | neutral
    summary: str
    signals: List[str] = []
    profile: Optional[OnChainProfile] = None


# --------------------------------------------------------------------------- #
# Incidents
# --------------------------------------------------------------------------- #
class IncidentResponse(BaseModel):
    id: str
    title: str
    description: str
    affected_services: str
    mitigations: str
    references: Optional[str] = None
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime


class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    affected_services: str = Field(..., min_length=3)
    mitigations: str = Field(..., min_length=3)
    references: Optional[str] = None
    severity: IncidentSeverity = IncidentSeverity.MEDIUM


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    affected_services: Optional[str] = None
    mitigations: Optional[str] = None
    references: Optional[str] = None
    severity: Optional[IncidentSeverity] = None
    status: Optional[IncidentStatus] = None


# --------------------------------------------------------------------------- #
# Community reports & moderation
# --------------------------------------------------------------------------- #
class ReportCreate(BaseModel):
    target_type: str = Field(..., description="wallet, domain, or token")
    target_value: str = Field(..., min_length=1, max_length=128)
    category: Optional[str] = Field(None, description="Suggested category, e.g. Fake Airdrop")
    description: str = Field(..., min_length=10, max_length=5000)
    evidence_url: Optional[str] = Field(None, max_length=1024)


class ReportOut(BaseModel):
    id: str
    target_type: str
    target_value: str
    category: Optional[str] = None
    description: str
    evidence_url: Optional[str] = None
    upvotes: int
    downvotes: int
    status: ReportStatus
    created_at: datetime


class VoteRequest(BaseModel):
    vote: str = Field(..., pattern="^(up|down)$")


class ModerateRequest(BaseModel):
    action: str = Field(..., pattern="^(approve|reject)$")
    moderation_note: Optional[str] = Field(None, max_length=2000)
    proof_type: Optional[str] = Field(None, description="Evidence proof type on approve")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


# --------------------------------------------------------------------------- #
# Authentication & users
# --------------------------------------------------------------------------- #
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=120)


class UserOut(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# --------------------------------------------------------------------------- #
# API keys
# --------------------------------------------------------------------------- #
class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)


class ApiKeyOut(BaseModel):
    id: str
    name: str
    rate_limit: int
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None


class ApiKeyCreated(ApiKeyOut):
    key: str  # plaintext key, shown exactly once


# --------------------------------------------------------------------------- #
# Search, feed, stats, AI
# --------------------------------------------------------------------------- #
class SearchResultItem(BaseModel):
    entity_type: str  # wallet | domain | token | incident
    identifier: str
    status: Optional[str] = None
    score: Optional[float] = None
    category: Optional[str] = None
    reason: Optional[str] = None
    updated_at: Optional[datetime] = None


class SearchResults(BaseModel):
    query: str
    total: int
    results: List[SearchResultItem]


class LatestThreatItem(BaseModel):
    entity_type: str  # wallet | domain | token
    identifier: str
    status: ThreatStatus
    score: float
    category: Optional[str] = None
    reason: str
    updated_at: datetime


class AIQueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000)
    context_type: Optional[str] = "general"


class AIQueryResponse(BaseModel):
    query: str
    analysis: str
    confidence_disclaimer: str = (
        "This analysis is derived from reported Stellar threat telemetry and heuristic "
        "correlation. It does not constitute absolute financial or legal certainty."
    )
    sources_referenced: List[str] = []


class GlobalStatsResponse(BaseModel):
    total_malicious_wallets: int
    total_phishing_domains: int
    total_scam_tokens: int
    total_incidents_recorded: int
    active_campaigns_count: int
    pending_reports: int
    total_indicators: int


class AuditLogEntry(BaseModel):
    id: str
    action: str
    target: str
    details: str
    timestamp: datetime


class PaginatedIncidents(BaseModel):
    total: int
    offset: int
    limit: int
    items: List[IncidentResponse]


# --------------------------------------------------------------------------- #
# Security Operations Center (SOC) overview
# --------------------------------------------------------------------------- #
class StatusCounts(BaseModel):
    confirmed_malicious: int = 0
    suspicious: int = 0
    under_investigation: int = 0
    trusted: int = 0


class ThreatLandscape(BaseModel):
    wallets: StatusCounts
    domains: StatusCounts
    tokens: StatusCounts


class ModuleStats(BaseModel):
    """Per-module counters for modules landing in later phases (anchors, scanner, SEP)."""
    anchors: int = 0
    soroban_scans: int = 0
    sep_validations: int = 0


class NetworkStatusOut(BaseModel):
    level: str  # normal | elevated | high
    label: str
    summary: str


class SocOverviewResponse(BaseModel):
    generated_at: datetime
    network_status: NetworkStatusOut
    landscape: ThreatLandscape
    counts: GlobalStatsResponse
    modules: ModuleStats
    active_campaigns: List[IncidentResponse]
    latest_threats: List[LatestThreatItem]
    recent_reports: List[ReportOut]
