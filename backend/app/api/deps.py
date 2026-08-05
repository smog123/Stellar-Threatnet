from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.entities import APIKey, User, UserRole
from app.services.threat_engine import ThreatService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

_credentials_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    """Resolve the authenticated user.

    Supports two auth methods:
      * Bearer JWT access token (interactive clients)
      * `X-API-Key` header (programmatic clients / SDKs)
    """
    api_key = request.headers.get("X-API-Key")
    if api_key:
        key_hash = ThreatService.hash_api_key(api_key)
        row = (
            await db.execute(select(APIKey).where(APIKey.key_hash == key_hash))
        ).scalar_one_or_none()
        if row is None or not row.is_active:
            raise _credentials_exc
        # Persisted when the calling endpoint commits; read-only paths leave it untouched.
        row.last_used_at = datetime.utcnow()
        user = await db.get(User, row.owner_id)
        if user is None or not user.is_active:
            raise _credentials_exc
        return user

    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        raise _credentials_exc
    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise _credentials_exc
    user = await db.get(User, payload["sub"])
    if user is None or not user.is_active:
        raise _credentials_exc
    return user


def require_roles(*roles: UserRole):
    """Dependency factory enforcing role-based access control."""

    async def _checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(r.value for r in roles)}",
            )
        return user

    return _checker
