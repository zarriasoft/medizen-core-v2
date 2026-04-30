import os
from slowapi import Limiter
from slowapi.util import get_remote_address

_enabled = os.getenv("DISABLE_RATE_LIMIT") != "1"

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"] if _enabled else [],
    enabled=_enabled,
)
