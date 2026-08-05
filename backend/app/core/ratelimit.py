from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

# Shared slowapi limiter. `enabled` mirrors settings so the test suite can
# disable rate limiting entirely via RATE_LIMIT_ENABLED=false.
limiter = Limiter(
    key_func=get_remote_address,
    enabled=settings.RATE_LIMIT_ENABLED,
)
