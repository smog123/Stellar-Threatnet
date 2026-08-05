from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.entities import APIKey, AuditLog, User, UserRole
from app.schemas.threats import ApiKeyCreated, ApiKeyCreate, ApiKeyOut, AuditLogEntry
from app.services.threat_engine import ThreatService

router = APIRouter(tags=["API Keys & Audit"])


# --------------------------------------------------------------------------- #
# API keys (authenticated users)
# --------------------------------------------------------------------------- #
@router.post("/api-keys", response_model=ApiKeyCreated, status_code=201, summary="Create an API key")
async def create_api_key(
    payload: ApiKeyCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a new API key. The plaintext key is returned exactly once — store it securely."""
    plain_key, data = await ThreatService.create_api_key(db, user, payload.name)
    return ApiKeyCreated(**data, key=plain_key)


@router.get("/api-keys", response_model=List[ApiKeyOut], summary="List my API keys")
async def list_api_keys(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(select(APIKey).where(APIKey.owner_id == user.id).order_by(APIKey.created_at.desc()))
    ).scalars().all()
    return [
        ApiKeyOut(
            id=r.id,
            name=r.name,
            rate_limit=r.rate_limit,
            is_active=r.is_active,
            created_at=r.created_at,
            last_used_at=r.last_used_at,
        )
        for r in rows
    ]


@router.delete("/api-keys/{key_id}", status_code=204, summary="Revoke an API key")
async def revoke_api_key(
    key_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.get(APIKey, key_id)
    if row is None or row.owner_id != user.id:
        raise HTTPException(status_code=404, detail="API key not found")
    row.is_active = False
    await db.commit()


# --------------------------------------------------------------------------- #
# Audit logs (admin only)
# --------------------------------------------------------------------------- #
@router.get("/admin/audit-logs", response_model=List[AuditLogEntry], summary="Browse the audit log")
async def list_audit_logs(
    action: str | None = Query(None),
    limit: int = Query(50, le=500),
    _: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    query = select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit)
    if action:
        query = query.where(AuditLog.action == action)
    rows = (await db.execute(query)).scalars().all()
    return [
        AuditLogEntry(id=r.id, action=r.action, target=r.target, details=r.details, timestamp=r.timestamp)
        for r in rows
    ]
