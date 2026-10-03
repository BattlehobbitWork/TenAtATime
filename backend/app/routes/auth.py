"""Authentication routes — simple password-based login for single-user mode."""

import secrets
import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.config import settings

router = APIRouter()


class LoginRequest(BaseModel):
    password: str


class LoginResponse(BaseModel):
    token: str
    expires_in: int = 86400  # 24 hours


class VerifyResponse(BaseModel):
    valid: bool


# Simple in-memory token store (resets on restart, which is fine for single-user)
_active_tokens: set[str] = set()


def _make_token(password: str) -> str:
    """Create a token from the password + a random salt."""
    salt = secrets.token_hex(16)
    raw = f"{password}:{salt}"
    return hashlib.sha256(raw.encode()).hexdigest()


@router.post("/auth/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    """Check password and return a session token."""
    if not settings.auth_password:
        # No password configured -- allow access without auth
        token = _make_token("open")
        _active_tokens.add(token)
        return LoginResponse(token=token)

    if req.password != settings.auth_password:
        raise HTTPException(status_code=401, detail="Not quite. Try again.")

    token = _make_token(req.password)
    _active_tokens.add(token)
    return LoginResponse(token=token)


@router.post("/auth/verify", response_model=VerifyResponse)
async def verify_token(request: Request):
    """Check if the current token is still valid."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
        return VerifyResponse(valid=token in _active_tokens)
    return VerifyResponse(valid=False)


@router.post("/auth/logout")
async def logout(request: Request):
    """Remove the current token."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
        _active_tokens.discard(token)
    return {"success": True}


async def require_auth(request: Request):
    """Dependency that checks for a valid auth token."""
    if not settings.auth_password:
        return  # No password configured, allow all

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Please sign in.")

    token = auth[7:]
    if token not in _active_tokens:
        raise HTTPException(status_code=401, detail="Session expired. Please sign in again.")
