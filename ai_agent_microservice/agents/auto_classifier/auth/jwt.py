from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from agents.auto_classifier.config import get_classifier_settings

_bearer = HTTPBearer()


def create_token(account_id: str, name: str, scopes: list[str]) -> str:
    cfg = get_classifier_settings()
    expire = datetime.now(UTC) + timedelta(minutes=cfg.jwt_expire_minutes)
    payload = {"sub": account_id, "name": name, "scopes": scopes, "exp": expire}
    return jwt.encode(payload, cfg.jwt_secret, algorithm=cfg.jwt_algorithm)


def verify_token(token: str) -> dict:
    cfg = get_classifier_settings()
    try:
        return jwt.decode(token, cfg.jwt_secret, algorithms=[cfg.jwt_algorithm])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def require_scope(scope: str):
    def dependency(credentials: HTTPAuthorizationCredentials = Depends(_bearer)) -> dict:
        payload = verify_token(credentials.credentials)
        if scope not in payload.get("scopes", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing scope: {scope}",
            )
        return payload
    return dependency
