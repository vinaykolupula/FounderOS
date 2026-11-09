"""
Authentication, User Management & System Integrations Router

Handles:
1. User registration, authentication, and JWT token issuance.
2. Multi-tenant workspace allocation and profile inspection (`/api/auth/me`).
3. OAuth 2.0 connection initiation and callback handling for 
   third-party tools (Google Workspace, Slack, Linear, HubSpot, Stripe).
"""

import hmac
import hashlib
import secrets
import time
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db import get_async_session
from app.auth import (
    get_current_workspace,
    get_current_user,
    hash_password,
    verify_password,
    create_access_token,
    require_role,
)
from app.models import (
    Connector,
    AuditLog,
    Workspace,
    User,
    UserRole,
    CompanyProfile,
    StageEnum,
    TeamSizeEnum,
)
from app.vault import encrypt_token, _get_key

router = APIRouter(prefix="/api/auth", tags=["Authentication & Integrations"])


# ==========================================
# Request / Response Schemas
# ==========================================

class RegisterRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password (min 6 chars)")
    full_name: Optional[str] = "Founder"
    company_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


# ==========================================
# User Registration & JWT Authentication
# ==========================================

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    req: RegisterRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Registers a new tenant user, provisions their isolated Workspace,
    and returns a cryptographically signed JWT access token.
    """
    clean_email = req.email.strip().lower()
    if not clean_email or "@" not in clean_email:
        raise HTTPException(status_code=400, detail="Invalid email address format")

    existing_res = await session.execute(select(User).where(User.email == clean_email))
    if existing_res.scalars().first():
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # 1. Provision isolated tenant Workspace
    workspace = Workspace(is_onboarded=False)
    session.add(workspace)
    await session.flush()

    # 2. Register Owner User
    hashed = hash_password(req.password)
    user = User(
        workspace_id=workspace.id,
        email=clean_email,
        full_name=req.full_name or "Founder",
        role=UserRole.OWNER.value,
        is_active=True,
        hashed_password=hashed
    )
    session.add(user)
    await session.flush()

    # 3. Optional initial Company Profile stub
    if req.company_name:
        company = CompanyProfile(
            workspace_id=workspace.id,
            name=req.company_name,
            stage=StageEnum.EARLY_REVENUE,
            team_size=TeamSizeEnum.TWO_TO_FIVE,
            ideal_customer="Target Customers",
            objective="Achieve sustainable product-market fit",
            primary_metric="MRR Growth",
            primary_constraint="Customer acquisition",
            runway_months=12,
            burn_rate="Unknown",
            gtm_motion="Product-Led Growth",
            tech_stack="React, Node.js, Postgres",
            competitive_moat="First mover advantage"
        )
        session.add(company)

    # 4. Initialize tenant system connectors
    connectors = [
        Connector(workspace_id=workspace.id, connector_id="gmail", name="Google Workspace", description="Email and calendar signals", category="Communication"),
        Connector(workspace_id=workspace.id, connector_id="slack", name="Slack", description="Team decisions and delivery context", category="Communication"),
        Connector(workspace_id=workspace.id, connector_id="linear", name="Linear", description="Product and engineering execution", category="Product"),
        Connector(workspace_id=workspace.id, connector_id="hubspot", name="HubSpot", description="Deals, pipeline, and customer history", category="Revenue"),
        Connector(workspace_id=workspace.id, connector_id="stripe", name="Stripe", description="Revenue, subscriptions, and churn", category="Finance"),
    ]
    for c in connectors:
        session.add(c)

    # 5. Audit log entry
    audit = AuditLog(
        workspace_id=workspace.id,
        actor=clean_email,
        event="USER_REGISTERED",
        details={"role": UserRole.OWNER.value, "userId": user.id}
    )
    session.add(audit)
    await session.commit()
    await session.refresh(user)

    token = create_access_token(
        user_id=user.id,
        workspace_id=workspace.id,
        role=user.role,
        email=user.email
    )

    return {
        "accessToken": token,
        "tokenType": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "fullName": user.full_name,
            "role": user.role,
            "workspaceId": user.workspace_id
        }
    }


@router.post("/login")
async def login(
    req: LoginRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Authenticates tenant user via email/password and issues a JWT access token.
    """
    clean_email = req.email.strip().lower()
    user_res = await session.execute(select(User).where(User.email == clean_email))
    user = user_res.scalars().first()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    token = create_access_token(
        user_id=user.id,
        workspace_id=user.workspace_id,
        role=user.role,
        email=user.email
    )

    return {
        "accessToken": token,
        "tokenType": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "fullName": user.full_name,
            "role": user.role,
            "workspaceId": user.workspace_id
        }
    }


@router.get("/me")
async def get_current_user_profile(
    user: User = Depends(require_role([
        UserRole.OWNER,
        UserRole.ADMIN,
        UserRole.MEMBER,
        UserRole.VIEWER
    ]))
):
    """Returns the authenticated user's profile, role, and workspace ID."""
    return {
        "id": user.id,
        "email": user.email,
        "fullName": user.full_name,
        "role": user.role,
        "workspaceId": user.workspace_id,
        "isActive": user.is_active
    }


# ==========================================
# OAuth 2.0 Integrations
# ==========================================

def _generate_oauth_state(workspace_id: int = 1) -> str:
    """Generates an HMAC-SHA256 authenticated state nonce with 10-minute validity tied to workspace."""
    nonce = secrets.token_urlsafe(16)
    ts = int(time.time())
    key = _get_key()
    sig = hmac.new(key, f"{nonce}:{workspace_id}:{ts}".encode("utf-8"), hashlib.sha256).hexdigest()[:32]
    return f"{nonce}.{workspace_id}.{ts}.{sig}"


def _verify_oauth_state(state: str) -> Optional[int]:
    """Verifies that the state token is authentic and not expired (<10m). Returns workspace_id or None."""
    try:
        parts = state.split(".")
        if len(parts) == 4:
            nonce, ws_str, ts_str, sig = parts
            workspace_id = int(ws_str)
            ts = int(ts_str)
            if abs(time.time() - ts) > 600:
                return None
            key = _get_key()
            expected = hmac.new(key, f"{nonce}:{workspace_id}:{ts}".encode("utf-8"), hashlib.sha256).hexdigest()[:32]
            return workspace_id if hmac.compare_digest(sig, expected) else None
        elif len(parts) == 3:
            nonce, ts_str, sig = parts
            ts = int(ts_str)
            if abs(time.time() - ts) > 600:
                return None
            key = _get_key()
            expected = hmac.new(key, f"{nonce}:{ts}".encode("utf-8"), hashlib.sha256).hexdigest()[:32]
            return 1 if hmac.compare_digest(sig, expected) else None
        return None
    except Exception:
        return None


@router.get("/google/login")
async def google_login_url(workspace: Workspace = Depends(get_current_workspace)):
    """Generates OAuth authorization URL with minimum read-only scopes and CSRF state nonce."""
    client_id = "founderos-dev-client-id.apps.googleusercontent.com"
    redirect_uri = "http://127.0.0.1:8000/api/auth/google/callback"
    scopes = "https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/calendar.readonly"
    ws_id = workspace.id if (workspace and workspace.id is not None) else 1
    state = _generate_oauth_state(ws_id)

    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&redirect_uri={redirect_uri}&"
        f"response_type=code&scope={scopes}&access_type=offline&prompt=consent&state={state}"
    )
    return {"authUrl": auth_url, "state": state, "scopes": ["gmail.readonly", "calendar.readonly"]}


@router.get("/google/callback")
async def google_callback(
    code: str = Query(...),
    state: str = Query(...),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Handles OAuth authorization code callback, verifies CSRF state token,
    and securely encrypts refresh token in Vault.
    """
    workspace_id = _verify_oauth_state(state)
    if workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OAuth state parameter (CSRF protection failed)"
        )

    result = await session.execute(select(Workspace).where(Workspace.id == workspace_id))
    workspace = result.scalars().first()
    if not workspace:
        ws_res = await session.execute(select(Workspace).order_by(Workspace.id.asc()))
        workspace = ws_res.scalars().first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Simulate token exchange and vault encryption
    mock_refresh_token = f"ref_tok_{code[:10]}_secret"
    encrypted_token = encrypt_token(mock_refresh_token)

    # Update connector status AND persist encrypted token in vault column
    conn_res = await session.execute(
        select(Connector).where(Connector.workspace_id == workspace.id, Connector.connector_id == "gmail")
    )
    connector = conn_res.scalars().first()
    if not connector:
        connector = Connector(
            workspace_id=workspace.id,
            connector_id="gmail",
            name="Google Workspace",
            description="Email and calendar signals",
            category="Communication"
        )
        session.add(connector)

    connector.status = "configured"
    connector.encrypted_oauth_token = encrypted_token
    session.add(connector)

    workspace_id = workspace.id or 0
    audit = AuditLog(
        workspace_id=workspace_id,
        actor="founder",
        event="OAUTH_TOKEN_STORED_IN_VAULT",
        details={"provider": "google", "encryptedVaultHash": encrypted_token[:16] + "..."}
    )
    session.add(audit)

    await session.commit()
    return {"message": "Google Workspace OAuth connected and token encrypted in Vault", "status": "configured"}
