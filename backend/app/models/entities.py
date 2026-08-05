import datetime
import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db.session import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    MODERATOR = "moderator"
    REPORTER = "reporter"
    READ_ONLY = "read_only"


class ThreatStatus(str, enum.Enum):
    CONFIRMED_MALICIOUS = "confirmed_malicious"
    SUSPICIOUS = "suspicious"
    UNDER_INVESTIGATION = "under_investigation"
    TRUSTED = "trusted"


class IncidentStatus(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class IncidentSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.REPORTER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    reports = relationship("CommunityReport", back_populates="reporter", foreign_keys="CommunityReport.reporter_id")
    moderated_reports = relationship("CommunityReport", back_populates="moderator", foreign_keys="CommunityReport.moderator_id")
    api_keys = relationship("APIKey", back_populates="owner")
    audit_logs = relationship("AuditLog", back_populates="actor")
    authored_incidents = relationship("Incident", back_populates="author")


class WalletReputation(Base):
    __tablename__ = "wallets"

    address = Column(String, primary_key=True, index=True)  # Stellar G... key
    reputation_score = Column(Integer, default=80, index=True, nullable=False)  # 0 to 100
    status = Column(Enum(ThreatStatus), default=ThreatStatus.UNDER_INVESTIGATION, index=True, nullable=False)
    category = Column(String, nullable=True)  # e.g., Drainer, Phishing Receiver
    reason = Column(Text, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)  # verified ecosystem anchor
    report_count = Column(Integer, default=0, nullable=False)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    evidence_items = relationship("Evidence", back_populates="wallet")


class DomainReputation(Base):
    __tablename__ = "domains"

    domain_name = Column(String, primary_key=True, index=True)  # e.g., stellar-fake.com
    confidence_score = Column(Float, default=0.5, nullable=False)  # 0.0 to 1.0
    status = Column(Enum(ThreatStatus), default=ThreatStatus.SUSPICIOUS, index=True, nullable=False)
    category = Column(String, nullable=False)  # Fake Wallet, Fake Airdrop
    reason = Column(Text, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    ip_address = Column(String, nullable=True)
    first_detected = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    evidence_items = relationship("Evidence", back_populates="domain")


class TokenReputation(Base):
    __tablename__ = "tokens"

    asset_identifier = Column(String, primary_key=True, index=True)  # CODE:ISSUER
    asset_code = Column(String, index=True, nullable=False)
    issuer_address = Column(String, index=True, nullable=False)
    status = Column(Enum(ThreatStatus), default=ThreatStatus.SUSPICIOUS, index=True, nullable=False)
    category = Column(String, nullable=False)  # Impersonation, Rugpull
    reason = Column(Text, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    confidence_score = Column(Float, default=0.5, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    evidence_items = relationship("Evidence", back_populates="token")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    affected_services = Column(Text, nullable=False)
    mitigations = Column(Text, nullable=False)
    references = Column(Text, nullable=True)
    severity = Column(Enum(IncidentSeverity), default=IncidentSeverity.MEDIUM, nullable=False)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.OPEN, nullable=False)
    author_id = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    author = relationship("User", back_populates="authored_incidents")


class CommunityReport(Base):
    __tablename__ = "community_reports"

    id = Column(String, primary_key=True, index=True)
    reporter_id = Column(String, ForeignKey("users.id"), nullable=False)
    target_type = Column(String, nullable=False)  # wallet, domain, token
    target_value = Column(String, nullable=False)  # Address, domain or CODE:ISSUER string
    category = Column(String, nullable=True)  # suggested category, e.g. Fake Airdrop
    description = Column(Text, nullable=False)
    evidence_url = Column(String, nullable=True)
    upvotes = Column(Integer, default=0, nullable=False)
    downvotes = Column(Integer, default=0, nullable=False)
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING, index=True, nullable=False)
    moderator_id = Column(String, ForeignKey("users.id"), nullable=True)
    moderation_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    moderated_at = Column(DateTime, nullable=True)

    reporter = relationship("User", back_populates="reports", foreign_keys=[reporter_id])
    moderator = relationship("User", back_populates="moderated_reports", foreign_keys=[moderator_id])


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String, primary_key=True, index=True)
    wallet_address = Column(String, ForeignKey("wallets.address"), nullable=True)
    domain_name = Column(String, ForeignKey("domains.domain_name"), nullable=True)
    token_identifier = Column(String, ForeignKey("tokens.asset_identifier"), nullable=True)
    proof_type = Column(String, nullable=False)  # tx_hash, domain_screenshot, payload_sample, onchain_proof, multi_source
    proof_url = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0, nullable=False)  # 0.0 to 1.0
    submitted_by = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    wallet = relationship("WalletReputation", back_populates="evidence_items")
    domain = relationship("DomainReputation", back_populates="evidence_items")
    token = relationship("TokenReputation", back_populates="evidence_items")


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, index=True)
    key_hash = Column(String, unique=True, index=True, nullable=False)  # sha256 of the plaintext key
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    rate_limit = Column(Integer, default=1000, nullable=False)  # requests / hour
    is_active = Column(Boolean, default=True, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="api_keys")


class Vote(Base):
    """One authenticated user's vote on a community report (unique per voter)."""

    __tablename__ = "votes"
    __table_args__ = (UniqueConstraint("report_id", "voter_id", name="uq_vote_report_voter"),)

    id = Column(String, primary_key=True, index=True)
    report_id = Column(String, ForeignKey("community_reports.id"), nullable=False)
    voter_id = Column(String, ForeignKey("users.id"), nullable=False)
    is_up = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, index=True)
    actor_id = Column(String, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)  # e.g., UPDATE_WALLET_SCORE, REPORT_MODERATED
    target = Column(String, nullable=False)
    details = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    actor = relationship("User", back_populates="audit_logs")
