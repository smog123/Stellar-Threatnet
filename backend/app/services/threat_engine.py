"""Database-backed threat intelligence engine.

Implements the reputation scoring model defined in docs/THREAT_MODEL.md:

    S(E) = BASE_SCORE - sum(W_i * C_i) + VERIFIED_BOOST

where BASE_SCORE = 80, W_i is the weight of evidence i, C_i is its confidence
(0..1) and VERIFIED_BOOST = 20 for verified ecosystem anchors.
"""
import csv
import hashlib
import io
import uuid
from datetime import datetime, timezone
from typing import Any, Optional, Sequence

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.entities import (
    APIKey,
    AuditLog,
    CommunityReport,
    DomainReputation,
    Evidence,
    Incident,
    IncidentStatus,
    ReportStatus,
    ThreatStatus,
    TokenReputation,
    User,
    Vote,
    WalletReputation,
)
from app.schemas.threats import (
    AIQueryResponse,
    DomainLookupResponse,
    GlobalStatsResponse,
    IncidentCreate,
    IncidentResponse,
    IncidentUpdate,
    LatestThreatItem,
    ModuleStats,
    NetworkStatusOut,
    ReportOut,
    SearchResultItem,
    SearchResults,
    SocOverviewResponse,
    StatusCounts,
    ThreatLandscape,
    TokenLookupResponse,
    WalletLookupResponse,
)
from app.services import cache

# Evidence weights per proof type (see docs/THREAT_MODEL.md section 2).
EVIDENCE_WEIGHTS: dict[str, float] = {
    "onchain_proof": 50.0,
    "payload_sample": 40.0,
    "tx_hash": 30.0,
    "domain_screenshot": 25.0,
    "multi_source": 20.0,
    "other": 15.0,
}

CATEGORY_BY_TYPE: dict[str, str] = {
    "wallet": "Suspicious Spammer",
    "domain": "Fake Wallet",
    "token": "Impersonation Token",
}


def compute_score(evidence_items: Sequence[Evidence], is_verified: bool = False) -> tuple[int, ThreatStatus]:
    """Compute reputation score (0-100) and derived status from evidence."""
    score = float(settings.BASE_REPUTATION_SCORE)
    for ev in evidence_items:
        weight = EVIDENCE_WEIGHTS.get(ev.proof_type, EVIDENCE_WEIGHTS["other"])
        confidence = min(max(float(ev.confidence or 0.0), 0.0), 1.0)
        score -= weight * confidence
    if is_verified:
        score += float(settings.VERIFIED_BOOST)
    score = max(0.0, min(100.0, score))
    int_score = round(score)

    if int_score <= 20:
        status = ThreatStatus.CONFIRMED_MALICIOUS
    elif int_score <= 50:
        status = ThreatStatus.SUSPICIOUS
    elif int_score <= 79:
        status = ThreatStatus.UNDER_INVESTIGATION
    else:
        status = ThreatStatus.TRUSTED
    return int_score, status


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


async def log_action(db: AsyncSession, actor_id: Optional[str], action: str, target: str, details: str) -> None:
    """Append to the audit log (append-only)."""
    db.add(
        AuditLog(
            id=new_id("AUD"),
            actor_id=actor_id,
            action=action,
            target=target,
            details=details[:4000],
        )
    )


class ThreatService:
    # ------------------------------------------------------------------ #
    # Wallet reputation
    # ------------------------------------------------------------------ #
    @staticmethod
    async def get_wallet_reputation(db: AsyncSession, address: str) -> Optional[WalletLookupResponse]:
        cache_key = cache.cache_key("wallet", address)
        cached = await cache.cache_get(cache_key)
        if cached:
            return WalletLookupResponse.model_validate_json(cached)

        row = await db.get(WalletReputation, address)
        if row is None:
            return None

        response = WalletLookupResponse(
            address=row.address,
            reputation_score=row.reputation_score,
            status=row.status,
            category=row.category,
            reason=row.reason,
            report_count=row.report_count,
            last_updated=row.last_updated,
        )
        await cache.cache_set(cache_key, response.model_dump_json())
        return response

    # ------------------------------------------------------------------ #
    # Domain reputation
    # ------------------------------------------------------------------ #
    @staticmethod
    async def get_domain_reputation(db: AsyncSession, domain: str) -> Optional[DomainLookupResponse]:
        cache_key = cache.cache_key("domain", domain)
        cached = await cache.cache_get(cache_key)
        if cached:
            return DomainLookupResponse.model_validate_json(cached)

        row = await db.get(DomainReputation, domain)
        if row is None:
            return None

        response = DomainLookupResponse(
            domain_name=row.domain_name,
            confidence_score=row.confidence_score,
            status=row.status,
            category=row.category,
            reason=row.reason,
            ip_address=row.ip_address,
            first_detected=row.first_detected,
        )
        await cache.cache_set(cache_key, response.model_dump_json())
        return response

    # ------------------------------------------------------------------ #
    # Token reputation
    # ------------------------------------------------------------------ #
    @staticmethod
    async def get_token_reputation(
        db: AsyncSession, asset_code: str, issuer: str
    ) -> Optional[TokenLookupResponse]:
        identifier = f"{asset_code.upper()}:{issuer}"
        cache_key = cache.cache_key("token", identifier)
        cached = await cache.cache_get(cache_key)
        if cached:
            return TokenLookupResponse.model_validate_json(cached)

        row = await db.get(TokenReputation, identifier)
        if row is None:
            return None

        response = TokenLookupResponse(
            asset_identifier=row.asset_identifier,
            asset_code=row.asset_code,
            issuer_address=row.issuer_address,
            status=row.status,
            category=row.category,
            reason=row.reason,
            confidence_score=row.confidence_score,
        )
        await cache.cache_set(cache_key, response.model_dump_json())
        return response

    # ------------------------------------------------------------------ #
    # Incidents
    # ------------------------------------------------------------------ #
    @staticmethod
    async def list_incidents(
        db: AsyncSession,
        status: Optional[IncidentStatus] = None,
        severity: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[int, list[IncidentResponse]]:
        """severity is validated to IncidentSeverity at the endpoint layer."""
        query = select(Incident)
        count_query = select(func.count(Incident.id))
        if status is not None:
            query = query.where(Incident.status == status)
            count_query = count_query.where(Incident.status == status)
        if severity is not None:
            query = query.where(Incident.severity == severity)
            count_query = count_query.where(Incident.severity == severity)

        total = (await db.execute(count_query)).scalar_one()
        rows = (
            await db.execute(query.order_by(Incident.created_at.desc()).limit(limit).offset(offset))
        ).scalars().all()
        return total, [ThreatService._incident_response(r) for r in rows]

    @staticmethod
    async def get_incident(db: AsyncSession, incident_id: str) -> Optional[IncidentResponse]:
        row = await db.get(Incident, incident_id)
        return ThreatService._incident_response(row) if row else None

    @staticmethod
    async def create_incident(
        db: AsyncSession, author: User, payload: IncidentCreate
    ) -> IncidentResponse:
        incident = Incident(
            id=new_id("INC"),
            title=payload.title,
            description=payload.description,
            affected_services=payload.affected_services,
            mitigations=payload.mitigations,
            references=payload.references,
            severity=payload.severity,
            status=IncidentStatus.OPEN,
            author_id=author.id,
        )
        db.add(incident)
        await db.flush()
        await log_action(db, author.id, "INCIDENT_CREATED", incident.id, payload.title)
        await db.commit()
        await db.refresh(incident)
        return ThreatService._incident_response(incident)

    @staticmethod
    async def update_incident(
        db: AsyncSession, moderator: User, incident_id: str, payload: IncidentUpdate
    ) -> Optional[IncidentResponse]:
        incident = await db.get(Incident, incident_id)
        if incident is None:
            return None
        data = payload.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(incident, field, value)
        await log_action(db, moderator.id, "INCIDENT_UPDATED", incident_id, str(data))
        await db.commit()
        await db.refresh(incident)
        return ThreatService._incident_response(incident)

    @staticmethod
    def _incident_response(row: Incident) -> IncidentResponse:
        return IncidentResponse(
            id=row.id,
            title=row.title,
            description=row.description,
            affected_services=row.affected_services,
            mitigations=row.mitigations,
            references=row.references,
            severity=row.severity,
            status=row.status,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    # ------------------------------------------------------------------ #
    # Latest threats & feed
    # ------------------------------------------------------------------ #
    @staticmethod
    async def latest_threats(db: AsyncSession, limit: int = 10) -> list[LatestThreatItem]:
        items: list[LatestThreatItem] = []

        wallets = (
            await db.execute(
                select(WalletReputation)
                .where(WalletReputation.status != ThreatStatus.TRUSTED)
                .order_by(WalletReputation.last_updated.desc())
                .limit(limit)
            )
        ).scalars().all()
        for w in wallets:
            items.append(
                LatestThreatItem(
                    entity_type="wallet",
                    identifier=w.address,
                    status=w.status,
                    score=float(w.reputation_score),
                    category=w.category,
                    reason=w.reason,
                    updated_at=w.last_updated,
                )
            )

        domains = (
            await db.execute(
                select(DomainReputation)
                .where(DomainReputation.status != ThreatStatus.TRUSTED)
                .order_by(DomainReputation.last_updated.desc())
                .limit(limit)
            )
        ).scalars().all()
        for d in domains:
            items.append(
                LatestThreatItem(
                    entity_type="domain",
                    identifier=d.domain_name,
                    status=d.status,
                    score=d.confidence_score * 100,
                    category=d.category,
                    reason=d.reason,
                    updated_at=d.last_updated,
                )
            )

        tokens = (
            await db.execute(
                select(TokenReputation)
                .where(TokenReputation.status != ThreatStatus.TRUSTED)
                .order_by(TokenReputation.last_updated.desc())
                .limit(limit)
            )
        ).scalars().all()
        for t in tokens:
            items.append(
                LatestThreatItem(
                    entity_type="token",
                    identifier=t.asset_identifier,
                    status=t.status,
                    score=t.confidence_score * 100,
                    category=t.category,
                    reason=t.reason,
                    updated_at=t.last_updated,
                )
            )

        items.sort(key=lambda i: i.updated_at or datetime.min, reverse=True)
        return items[:limit]

    @staticmethod
    async def feed_csv(db: AsyncSession, limit: int = 5000) -> str:
        """Downloadable CSV threat feed (wallets, domains, tokens).

        `reputation_score` (0-100) is populated for wallets; `confidence_score`
        (0-1) for domains and tokens.
        """
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            [
                "entity_type",
                "identifier",
                "status",
                "reputation_score",
                "confidence_score",
                "category",
                "reason",
                "updated_at",
            ]
        )

        wallets = (
            await db.execute(select(WalletReputation).limit(limit))
        ).scalars().all()
        for w in wallets:
            writer.writerow(
                [
                    "wallet", w.address, w.status.value, w.reputation_score, "",
                    w.category or "", w.reason, w.last_updated.isoformat(),
                ]
            )

        domains = (
            await db.execute(select(DomainReputation).limit(limit))
        ).scalars().all()
        for d in domains:
            writer.writerow(
                [
                    "domain", d.domain_name, d.status.value, "", d.confidence_score,
                    d.category, d.reason, d.last_updated.isoformat(),
                ]
            )

        tokens = (
            await db.execute(select(TokenReputation).limit(limit))
        ).scalars().all()
        for t in tokens:
            writer.writerow(
                [
                    "token", t.asset_identifier, t.status.value, "", t.confidence_score,
                    t.category, t.reason, t.last_updated.isoformat(),
                ]
            )

        return buffer.getvalue()

    # ------------------------------------------------------------------ #
    # Statistics
    # ------------------------------------------------------------------ #
    @staticmethod
    async def get_stats(db: AsyncSession) -> GlobalStatsResponse:
        malicious_wallets = (
            await db.execute(
                select(func.count(WalletReputation.address)).where(
                    WalletReputation.status == ThreatStatus.CONFIRMED_MALICIOUS
                )
            )
        ).scalar_one()
        phishing_domains = (
            await db.execute(
                select(func.count(DomainReputation.domain_name)).where(
                    DomainReputation.status == ThreatStatus.CONFIRMED_MALICIOUS
                )
            )
        ).scalar_one()
        scam_tokens = (
            await db.execute(
                select(func.count(TokenReputation.asset_identifier)).where(
                    TokenReputation.status == ThreatStatus.CONFIRMED_MALICIOUS
                )
            )
        ).scalar_one()
        total_incidents = (
            await db.execute(select(func.count(Incident.id)))
        ).scalar_one()
        active_campaigns = (
            await db.execute(
                select(func.count(Incident.id)).where(
                    Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.INVESTIGATING])
                )
            )
        ).scalar_one()
        pending_reports = (
            await db.execute(
                select(func.count(CommunityReport.id)).where(
                    CommunityReport.status == ReportStatus.PENDING
                )
            )
        ).scalar_one()
        total_indicators = malicious_wallets + phishing_domains + scam_tokens

        return GlobalStatsResponse(
            total_malicious_wallets=malicious_wallets,
            total_phishing_domains=phishing_domains,
            total_scam_tokens=scam_tokens,
            total_incidents_recorded=total_incidents,
            active_campaigns_count=active_campaigns,
            pending_reports=pending_reports,
            total_indicators=total_indicators,
        )

    # ------------------------------------------------------------------ #
    # Security Operations Center (SOC) overview
    # ------------------------------------------------------------------ #
    @staticmethod
    async def get_soc_overview(db: AsyncSession) -> SocOverviewResponse:
        """Aggregate everything the SOC dashboard needs in a single call.

        Derives the network security level from live signal (active campaigns
        and confirmed-malicious totals) so the banner reflects reality rather
        than a hardcoded state.
        """
        stats = await ThreatService.get_stats(db)

        async def _status_counts(model: Any, id_col: Any) -> StatusCounts:
            rows = (await db.execute(select(model.status, func.count(id_col)).group_by(model.status))).all()
            counts = {
                "confirmed_malicious": 0,
                "suspicious": 0,
                "under_investigation": 0,
                "trusted": 0,
            }
            for status, count in rows:
                key = status.value if hasattr(status, "value") else str(status)
                if key in counts:
                    counts[key] = count
            return StatusCounts(**counts)

        landscape = ThreatLandscape(
            wallets=await _status_counts(WalletReputation, WalletReputation.address),
            domains=await _status_counts(DomainReputation, DomainReputation.domain_name),
            tokens=await _status_counts(TokenReputation, TokenReputation.asset_identifier),
        )

        active_rows = (
            await db.execute(
                select(Incident)
                .where(Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.INVESTIGATING]))
                .order_by(Incident.updated_at.desc())
                .limit(5)
            )
        ).scalars().all()
        active_campaigns = [ThreatService._incident_response(r) for r in active_rows]

        recent_rows = (
            await db.execute(
                select(CommunityReport).order_by(CommunityReport.created_at.desc()).limit(6)
            )
        ).scalars().all()
        recent_reports = [ThreatService._report_out(r) for r in recent_rows]

        latest_threats = await ThreatService.latest_threats(db, 8)

        # Derive network posture from live signal.
        malicious_total = (
            landscape.wallets.confirmed_malicious
            + landscape.domains.confirmed_malicious
            + landscape.tokens.confirmed_malicious
        )
        active_count = len(active_campaigns)
        if active_count >= 3 or malicious_total >= 10:
            level, label = "high", "Elevated Threat Activity"
            summary = (
                f"{malicious_total} confirmed malicious indicators and {active_count} active "
                "campaigns are being tracked. Apply extra scrutiny to unsolicited airdrops, "
                "homograph domains, and requests for secret keys."
            )
        elif active_count >= 1 or stats.pending_reports > 5:
            level, label = "elevated", "Heightened Awareness"
            summary = (
                f"{active_count} active campaign(s) and {stats.pending_reports} report(s) awaiting "
                "moderation. Community reporting is engaged — verify entities before transacting."
            )
        else:
            level, label = "normal", "Baseline Monitoring"
            summary = (
                "No active campaigns detected. ThreatNet is monitoring wallets, domains, and "
                "tokens across the Stellar ecosystem."
            )

        return SocOverviewResponse(
            generated_at=datetime.now(timezone.utc),
            network_status=NetworkStatusOut(level=level, label=label, summary=summary),
            landscape=landscape,
            counts=stats,
            modules=ModuleStats(),
            active_campaigns=active_campaigns,
            latest_threats=latest_threats,
            recent_reports=recent_reports,
        )

    # ------------------------------------------------------------------ #
    # Search
    # ------------------------------------------------------------------ #
    @staticmethod
    async def search(db: AsyncSession, query: str, entity_type: Optional[str], limit: int = 20) -> SearchResults:
        q = f"%{query.strip()}%"
        results: list[SearchResultItem] = []
        entities = entity_type.split(",") if entity_type else ["wallet", "domain", "token", "incident"]

        if "wallet" in entities:
            rows = (
                await db.execute(
                    select(WalletReputation)
                    .where(WalletReputation.address.ilike(q))
                    .limit(limit)
                )
            ).scalars().all()
            for r in rows:
                results.append(
                    SearchResultItem(
                        entity_type="wallet",
                        identifier=r.address,
                        status=r.status.value,
                        score=float(r.reputation_score),
                        category=r.category,
                        reason=r.reason,
                        updated_at=r.last_updated,
                    )
                )

        if "domain" in entities:
            rows = (
                await db.execute(
                    select(DomainReputation)
                    .where(or_(DomainReputation.domain_name.ilike(q), DomainReputation.category.ilike(q)))
                    .limit(limit)
                )
            ).scalars().all()
            for r in rows:
                results.append(
                    SearchResultItem(
                        entity_type="domain",
                        identifier=r.domain_name,
                        status=r.status.value,
                        score=r.confidence_score,
                        category=r.category,
                        reason=r.reason,
                        updated_at=r.last_updated,
                    )
                )

        if "token" in entities:
            rows = (
                await db.execute(
                    select(TokenReputation)
                    .where(
                        or_(
                            TokenReputation.asset_identifier.ilike(q),
                            TokenReputation.asset_code.ilike(q),
                        )
                    )
                    .limit(limit)
                )
            ).scalars().all()
            for r in rows:
                results.append(
                    SearchResultItem(
                        entity_type="token",
                        identifier=r.asset_identifier,
                        status=r.status.value,
                        score=r.confidence_score,
                        category=r.category,
                        reason=r.reason,
                        updated_at=r.last_updated,
                    )
                )

        if "incident" in entities:
            rows = (
                await db.execute(
                    select(Incident)
                    .where(
                        or_(
                            Incident.title.ilike(q),
                            Incident.description.ilike(q),
                            Incident.affected_services.ilike(q),
                        )
                    )
                    .limit(limit)
                )
            ).scalars().all()
            for r in rows:
                results.append(
                    SearchResultItem(
                        entity_type="incident",
                        identifier=r.id,
                        status=r.status.value,
                        category=r.severity.value,
                        reason=r.title,
                        updated_at=r.updated_at,
                    )
                )

        return SearchResults(query=query, total=len(results), results=results)

    # ------------------------------------------------------------------ #
    # Community reports & moderation
    # ------------------------------------------------------------------ #
    @staticmethod
    async def submit_report(db: AsyncSession, reporter: User, payload: Any) -> ReportOut:
        report = CommunityReport(
            id=new_id("REP"),
            reporter_id=reporter.id,
            target_type=payload.target_type.lower(),
            target_value=payload.target_value.strip(),
            category=payload.category,
            description=payload.description,
            evidence_url=payload.evidence_url,
        )
        db.add(report)
        await db.flush()
        await log_action(db, reporter.id, "REPORT_SUBMITTED", f"{report.target_type}:{report.target_value}", report.description[:200])
        await db.commit()
        await db.refresh(report)
        return ThreatService._report_out(report)

    @staticmethod
    async def vote_report(db: AsyncSession, user: User, report_id: str, up: bool) -> Optional[ReportOut]:
        report = await db.get(CommunityReport, report_id)
        if report is None or report.status != ReportStatus.PENDING:
            return None

        existing = (
            await db.execute(
                select(Vote).where(Vote.report_id == report_id, Vote.voter_id == user.id)
            )
        ).scalar_one_or_none()
        if existing is not None:
            raise HTTPException(status_code=409, detail="Already voted on this report")

        db.add(Vote(id=new_id("VOT"), report_id=report_id, voter_id=user.id, is_up=up))
        if up:
            report.upvotes += 1
        else:
            report.downvotes += 1
        await db.commit()
        await db.refresh(report)
        return ThreatService._report_out(report)

    @staticmethod
    async def list_pending_reports(db: AsyncSession, limit: int = 50) -> list[ReportOut]:
        rows = (
            await db.execute(
                select(CommunityReport)
                .where(CommunityReport.status == ReportStatus.PENDING)
                .order_by(CommunityReport.created_at.asc())
                .limit(limit)
            )
        ).scalars().all()
        return [ThreatService._report_out(r) for r in rows]

    @staticmethod
    async def moderate_report(
        db: AsyncSession,
        moderator: User,
        report_id: str,
        action: str,
        note: Optional[str],
        proof_type: Optional[str],
        confidence: Optional[float],
    ) -> Optional[ReportOut]:
        report = await db.get(CommunityReport, report_id)
        if report is None or report.status != ReportStatus.PENDING:
            return None

        report.moderator_id = moderator.id
        report.moderated_at = datetime.utcnow()
        report.moderation_note = note

        if action == "reject":
            report.status = ReportStatus.REJECTED
            await log_action(
                db, moderator.id, "REPORT_REJECTED", report.id,
                f"Rejected report for {report.target_type}:{report.target_value}",
            )
            await db.commit()
            await db.refresh(report)
            return ThreatService._report_out(report)

        # Approve: attach evidence to the target entity and recompute its score.
        confidence = confidence if confidence is not None else 0.9
        proof_type = proof_type or "other"
        target = report.target_value.strip()
        ttype = report.target_type.lower()

        # Validate the target format BEFORE approving, so we never mark a report
        # approved without attaching usable evidence.
        if ttype == "token":
            code, sep, issuer = target.partition(":")
            if not sep or not code or not issuer:
                raise HTTPException(
                    status_code=422, detail="Malformed token target; expected CODE:ISSUER"
                )

        report.status = ReportStatus.APPROVED
        evidence = Evidence(
            id=new_id("EVI"),
            proof_type=proof_type,
            proof_url=report.evidence_url or f"https://stellar-threatnet.org/reports/{report.id}",
            description=report.description[:1000],
            confidence=confidence,
            submitted_by=report.reporter_id,
        )

        if ttype == "wallet":
            evidence.wallet_address = target
            entity = await db.get(WalletReputation, target)
            if entity is None:
                entity = WalletReputation(
                    address=target,
                    category=report.category or "Reported Malicious",
                    reason=report.description[:500],
                    status=ThreatStatus.UNDER_INVESTIGATION,
                )
                db.add(entity)
        elif ttype == "domain":
            evidence.domain_name = target
            entity = await db.get(DomainReputation, target)
            if entity is None:
                entity = DomainReputation(
                    domain_name=target,
                    category=report.category or "Reported Phishing",
                    reason=report.description[:500],
                    status=ThreatStatus.SUSPICIOUS,
                )
                db.add(entity)
        elif ttype == "token":
            identifier = f"{code.upper()}:{issuer}"
            evidence.token_identifier = identifier
            entity = await db.get(TokenReputation, identifier)
            if entity is None:
                entity = TokenReputation(
                    asset_identifier=identifier,
                    asset_code=code.upper(),
                    issuer_address=issuer,
                    category=report.category or "Impersonation Token",
                    reason=report.description[:500],
                    status=ThreatStatus.SUSPICIOUS,
                )
                db.add(entity)

        db.add(evidence)
        await db.flush()
        await ThreatService.recompute_entity_score(db, entity)
        await log_action(
            db, moderator.id, "REPORT_APPROVED", report.id,
            f"Approved {ttype} report for {target}; evidence {evidence.id} attached.",
        )
        await db.commit()
        await db.refresh(report)
        return ThreatService._report_out(report)

    @staticmethod
    async def recompute_entity_score(db: AsyncSession, entity: Any) -> None:
        """Recompute score + status for a Wallet/Domain/Token from its evidence."""
        if isinstance(entity, WalletReputation):
            evidence = (
                await db.execute(
                    select(Evidence).where(Evidence.wallet_address == entity.address)
                )
            ).scalars().all()
            score, status = compute_score(evidence, entity.is_verified)
            entity.reputation_score = score
            entity.status = status
            entity.report_count = len([e for e in evidence if e.proof_type in ("tx_hash", "multi_source", "payload_sample")])
            await cache.cache_delete_pattern(cache.cache_key("wallet", entity.address))
        elif isinstance(entity, DomainReputation):
            evidence = (
                await db.execute(
                    select(Evidence).where(Evidence.domain_name == entity.domain_name)
                )
            ).scalars().all()
            score, status = compute_score(evidence, entity.is_verified)
            entity.confidence_score = ThreatService._evidence_confidence(evidence)
            entity.status = status
            await cache.cache_delete_pattern(cache.cache_key("domain", entity.domain_name))
        elif isinstance(entity, TokenReputation):
            evidence = (
                await db.execute(
                    select(Evidence).where(Evidence.token_identifier == entity.asset_identifier)
                )
            ).scalars().all()
            score, status = compute_score(evidence, entity.is_verified)
            entity.confidence_score = ThreatService._evidence_confidence(evidence)
            entity.status = status
            await cache.cache_delete_pattern(cache.cache_key("token", entity.asset_identifier))

    # ------------------------------------------------------------------ #
    # AI threat assistant
    # ------------------------------------------------------------------ #
    @staticmethod
    async def process_ai_assistant_query(db: AsyncSession, query: str) -> AIQueryResponse:
        q_lower = query.lower()
        sources: list[str] = ["ThreatNet Core Matrix"]

        # Try to enrich with real telemetry: detect wallet addresses and domains.
        words = query.split()
        for word in words:
            clean = word.strip(",.!?;:'\"()")
            if len(clean) == 56 and clean.startswith("G") and clean.isalnum():
                result = await ThreatService.get_wallet_reputation(db, clean)
                if result:
                    return AIQueryResponse(
                        query=query,
                        analysis=(
                            f"Reputation lookup for `{clean}` returned a score of "
                            f"{result.reputation_score}/100 ({result.status.value}). "
                            f"{result.reason} Category: {result.category or 'unspecified'}."
                        ),
                        sources_referenced=["On-chain wallet telemetry", "ThreatNet evidence database"],
                    )

        if "phishing" in q_lower or "campaign" in q_lower:
            analysis = (
                "Recent active phishing campaigns target Stellar users via fake 'Stellar Community "
                "Rewards' pages and spoofed browser extensions that ask for secret seed phrases or "
                "secret keys (S...). Always verify the domain against the official project site and "
                "never share a secret key."
            )
            sources = ["Domain Intelligence DB", "Ecosystem Security Reports"]
        elif "wallet" in q_lower or "suspicious" in q_lower:
            analysis = (
                "Wallets flagged by ThreatNet typically show rapid claimable-balance creation, "
                "unsolicited memo payloads, or received funds from confirmed phishing domains. "
                "Use GET /lookup/wallet/{address} to check a specific address before signing."
            )
            sources = ["Wallet telemetry feed"]
        elif "today" in q_lower or "threats" in q_lower:
            analysis = (
                "Query the latest threats via GET /threats/latest or download the full CSV feed "
                "from GET /feed. The dashboard shows live aggregate statistics."
            )
            sources = ["Live threat feed"]
        elif "attack" in q_lower or "exploit" in q_lower or "vulnerab" in q_lower:
            analysis = (
                "Stellar/Soroban incidents typically involve reentrancy on AMM contracts, "
                "clawback/freeze abuse by malicious issuers, or signature phishing. Check the "
                "incident database (GET /incidents) for timelines and mitigations."
            )
            sources = ["Incident Intelligence DB"]
        else:
            analysis = (
                "Stellar ThreatNet monitors network accounts, asset issuances, and web endpoints "
                "to calculate dynamic threat reputation scores in real time. You can ask about a "
                "specific wallet address, a phishing campaign, or today's threats."
            )

        return AIQueryResponse(
            query=query,
            analysis=analysis,
            confidence_disclaimer=(
                "This analysis is derived from reported Stellar threat telemetry and heuristic "
                "correlation. It does not constitute absolute financial or legal certainty."
            ),
            sources_referenced=sources,
        )

    # ------------------------------------------------------------------ #
    # API keys & audit
    # ------------------------------------------------------------------ #
    @staticmethod
    def hash_api_key(plain_key: str) -> str:
        return hashlib.sha256(plain_key.encode()).hexdigest()

    @staticmethod
    async def create_api_key(db: AsyncSession, user: User, name: str) -> tuple[str, dict]:
        plain_key = f"tn_{uuid.uuid4().hex}{uuid.uuid4().hex[:16]}"
        row = APIKey(
            id=new_id("KEY"),
            key_hash=ThreatService.hash_api_key(plain_key),
            owner_id=user.id,
            name=name,
        )
        db.add(row)
        await db.flush()
        await log_action(db, user.id, "API_KEY_CREATED", row.id, name)
        await db.commit()
        return plain_key, {
            "id": row.id,
            "name": row.name,
            "rate_limit": row.rate_limit,
            "is_active": row.is_active,
            "created_at": row.created_at,
            "last_used_at": row.last_used_at,
        }

    @staticmethod
    def _evidence_confidence(evidence_items: Sequence[Evidence]) -> float:
        """Confidence in the current verdict = strongest attached evidence.

        No evidence means low confidence (0.1); evidence confidence follows the
        levels in docs/THREAT_MODEL.md (0.3 community .. 1.0 on-chain proof).
        """
        max_conf = max((float(e.confidence or 0.0) for e in evidence_items), default=0.1)
        return round(min(max(max_conf, 0.1), 1.0), 2)

    @staticmethod
    def _report_out(report: CommunityReport) -> ReportOut:
        return ReportOut(
            id=report.id,
            target_type=report.target_type,
            target_value=report.target_value,
            category=report.category,
            description=report.description,
            evidence_url=report.evidence_url,
            upvotes=report.upvotes,
            downvotes=report.downvotes,
            status=report.status,
            created_at=report.created_at,
        )
