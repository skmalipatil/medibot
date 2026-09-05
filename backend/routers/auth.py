"""
medibot — /login router.

Demo authentication only (this is a learning project). A small in-memory
user table maps username -> (password, role). On success we mint a short
JWT carrying {sub, role, exp}; downstream routes decode it into a
`Principal`.

TODO:
  * replace DEMO_USERS with a real store + hashed passwords (passlib)
  * move token decode into backend/deps.py as `get_current_principal`
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from backend.config import (
    ROLE_ADMIN,
    ROLE_DOCTOR,
    ROLE_NURSE,
    ROLE_PHARMACIST,
    ROLE_RECEPTIONIST,
    settings,
)
from backend.utils.rbac import Principal, RBACError

router = APIRouter(prefix="/auth", tags=["auth"])
_bearer = HTTPBearer(auto_error=True)

# username -> (password, role)  — DEMO ONLY
DEMO_USERS: dict[str, tuple[str, str]] = {
    "dr_house": ("diagnosis", ROLE_DOCTOR),
    "nurse_joy": ("vitals", ROLE_NURSE),
    "pharm_phil": ("dosage", ROLE_PHARMACIST),
    "reception_rita": ("frontdesk", ROLE_RECEPTIONIST),
    "admin_ada": ("root", ROLE_ADMIN),
}


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    success: bool = True
    access_token: str
    token_type: str = "bearer"
    role: str


def _create_token(username: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "role": role,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
        "iat": now,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest) -> TokenResponse:
    record = DEMO_USERS.get(body.username)
    if record is None or record[0] != body.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    _, role = record
    return TokenResponse(access_token=_create_token(body.username, role), role=role)


async def get_current_principal(
    creds: HTTPAuthorizationCredentials = Depends(_bearer),
) -> Principal:
    """FastAPI dependency: decode the bearer JWT into a validated Principal."""
    try:
        payload = jwt.decode(
            creds.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return Principal(username=payload["sub"], role=payload["role"])
    except (JWTError, KeyError, RBACError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc
