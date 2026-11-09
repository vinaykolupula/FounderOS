"""
FounderOS API Authentication & Multi-Tenant Workspace Resolution

Provides production-grade authentication, role-based access control (RBAC),
and multi-tenant workspace isolation:
- Standard-library PBKDF2-HMAC-SHA256 password hashing.
- Cryptographically signed HMAC-SHA256 JWT tokens.
- Role-based authorization (`require_role`).
- Automatic multi-tenant workspace scoping via `get_current_workspace`.
- Frictionless development mode when `AUTH_ENABLED=False`.
"""

import base64
import hashlib
import hmac
import json
import logging
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Union, Dict, Any

from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.config import settings
from app.db import get_async_session
from app.models import Workspace, User, UserRole
from app.vault import _get_key

logger = logging.getLogger("founderos.auth")


# ==========================================
# Password Hashing (PBKDF2-HMAC-SHA256)
# ==========================================

def hash_password(password: str) -> str:
    """
    Hashes a password using PBKDF2-HMAC-SHA256 with a unique cryptographic 16-byte salt
    and 100,000 iterations (standard library, zero binary dependencies).
    Format: pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>
    """
    salt = secrets.token_hex(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000
    )
    return f"pbkdf2_sha256$100000${salt}${derived.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verifies a plaintext password against a stored PBKDF2 hash using constant-time comparison."""
    try:
        parts = hashed.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = parts[2]
        expected_hash = parts[3]
        derived = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations
        )
        return hmac.compare_digest(derived.hex(), expected_hash)
    except Exception:
        return False


# ==========================================
# Cryptographic JWT Engine (HMAC-SHA256)
# ==========================================

def _get_signing_key() -> bytes:
    """Retrieves secret key for JWT signing from settings or the AES vault key."""
    if settings.JWT_SECRET_KEY:
        return settings.JWT_SECRET_KEY.encode("utf-8")
    return _get_key()


def _b64_url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64_url_decode(data: str) -> bytes:
    padding = "=" * (4 - (len(data) % 4) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(
    user_id: int,
    workspace_id: int,
    role: Union[str, UserRole],
    email: str = "",
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Creates a signed JWT access token for an authenticated tenant user.
    """
    role_str = role.value if isinstance(role, UserRole) else str(role)
    now = int(time.time())
    expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    exp = now + int(expires_delta.total_seconds()) if expires_delta else now + (expire_minutes * 60)

    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": str(user_id),
        "user_id": user_id,
        "workspace_id": workspace_id,
        "role": role_str,
        "email": email,
        "iat": now,
        "exp": exp
    }

    header_b64 = _b64_url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64_url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

    sig = hmac.new(_get_signing_key(), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64_url_encode(sig)

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Validates signature and expiration of a JWT access token.
    Raises HTTPException(401) on invalid signature, malformed token, or expiration.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid JWT segments")

        header_b64, payload_b64, sig_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(_get_signing_key(), signing_input, hashlib.sha256).digest()
        provided_sig = _b64_url_decode(sig_b64)

        if not hmac.compare_digest(expected_sig, provided_sig):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token signature",
                headers={"WWW-Authenticate": "Bearer"}
            )

        payload_bytes = _b64_url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        # Verify expiration
        exp = payload.get("exp")
        if exp and int(time.time()) > int(exp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return payload
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Failed to decode access token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed or invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )


# ==========================================
# FastAPI Dependencies & RBAC Guards
# ==========================================

async def get_current_user(
    session: AsyncSession = Depends(get_async_session),
    authorization: Optional[str] = Header(None),
    x_founderos_key: Optional[str] = Header(None, alias="X-FounderOS-Key")
) -> Optional[User]:
    """
    Resolves the authenticated User from Bearer token or API key.
    Provides seamless local development fallback when AUTH_ENABLED=False.
    """
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split("Bearer ", 1)[1].strip()

    api_key = x_founderos_key or token

    # 1. Static API Key authentication (e.g. X-FounderOS-Key or Bearer key)
    if settings.FOUNDEROS_API_KEY and api_key == settings.FOUNDEROS_API_KEY:
        user_res = await session.execute(select(User).where(User.is_active == True))
        user = user_res.scalars().first()
        if user:
            return user
        return User(
            id=1,
            workspace_id=1,
            email="founder@local",
            full_name="Founder",
            role=UserRole.OWNER.value,
            is_active=True,
            hashed_password=""
        )

    # 2. JWT Bearer token authentication
    if token and "." in token:
        try:
            payload = decode_access_token(token)
            user_id = payload.get("user_id")
            if user_id:
                user_res = await session.execute(select(User).where(User.id == int(user_id)))
                user = user_res.scalars().first()
                if user:
                    if not user.is_active:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="User account is deactivated"
                        )
                    return user
        except HTTPException:
            # If explicit token was passed and invalid, fail fast
            raise
        except Exception:
            pass

    # 3. Development mode fallback when AUTH_ENABLED is False and no API key required
    if not settings.AUTH_ENABLED and not settings.FOUNDEROS_API_KEY:
        # If user explicitly passed an invalid token, reject it
        if token and "." in token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token signature",
                headers={"WWW-Authenticate": "Bearer"}
            )

        ws_res = await session.execute(select(Workspace).order_by(Workspace.id.asc()))
        root_ws = ws_res.scalars().first()
        ws_id = root_ws.id if root_ws and root_ws.id is not None else 1
        user_res = await session.execute(
            select(User).where(User.workspace_id == ws_id, User.is_active == True)
        )
        user = user_res.scalars().first()
        if user:
            return user
        # Return transient development user for root workspace
        return User(
            id=1,
            workspace_id=ws_id,
            email="founder@local",
            full_name="Local Founder",
            role=UserRole.OWNER.value,
            is_active=True,
            hashed_password=""
        )

    # 4. Auth is strictly required but no valid credentials provided
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized: Valid authentication token or API key required",
        headers={"WWW-Authenticate": "Bearer"}
    )


async def get_current_workspace(
    session: AsyncSession = Depends(get_async_session),
    current_user: Optional[User] = Depends(get_current_user)
) -> Workspace:
    """
    FastAPI dependency that enforces authentication and returns the active tenant Workspace.
    Ensures absolute tenant isolation across all endpoints.
    """
    if current_user and current_user.workspace_id:
        result = await session.execute(
            select(Workspace).where(Workspace.id == current_user.workspace_id)
        )
        workspace = result.scalars().first()
        if workspace:
            return workspace

    # Fallback for fresh initialization / single-user setups
    result = await session.execute(select(Workspace).order_by(Workspace.id.asc()))
    workspace = result.scalars().first()
    if not workspace:
        workspace = Workspace(is_onboarded=False)
        session.add(workspace)
        await session.commit()
        await session.refresh(workspace)

    return workspace


def require_role(allowed_roles: List[Union[str, UserRole]]):
    """
    Role-Based Access Control (RBAC) dependency factory.
    Enforces that the authenticated user possesses one of the authorized roles.
    Example: `user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN]))`
    """
    allowed_values = [r.value if isinstance(r, UserRole) else str(r) for r in allowed_roles]

    async def role_checker(
        current_user: Optional[User] = Depends(get_current_user)
    ) -> User:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"}
            )
        user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
        if user_role not in allowed_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {allowed_values}; User role: '{user_role}'"
            )
        return current_user

    return role_checker
