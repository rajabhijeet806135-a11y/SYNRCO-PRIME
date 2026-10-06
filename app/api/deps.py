from fastapi import Header, HTTPException, status
from typing import Optional, Dict, Any
from app.subsystems.auth.jwt_manager import JwtManager
from app.subsystems.auth.session_store import SessionStore
from app.core.token_bucket import default_rate_limiter

async def get_current_user(
    authorization: Optional[str] = Header(None),
    x_session_id: Optional[str] = Header(None)
) -> Dict[str, Any]:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme, expected Bearer <token>"
        )

    token = parts[1]
    payload = JwtManager.verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or invalid"
        )

    # Optional Redis Session Fast Check
    if x_session_id:
        sess = await SessionStore.get_session(x_session_id)
        if not sess:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session revoked or expired"
            )

    return payload

async def rate_limit_guard(
    x_forwarded_for: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None)
):
    key = authorization or x_forwarded_for or "127.0.0.1"
    allowed = default_rate_limiter.check_limit(key, cost=1)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Throttling active."
        )
