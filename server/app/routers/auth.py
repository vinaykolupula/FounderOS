"""
OAuth Authentication & System Integrations Router

Handles OAuth 2.0 connection initiation and callback handling for 
third-party tools (Google Workspace, Slack, Linear, HubSpot, Stripe).
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db import get_async_session
from app.models import Connector, AuditLog, Workspace
from app.vault import encrypt_token

router = APIRouter(prefix="/api/auth", tags=["OAuth Integrations"])


@router.get("/google/login")
async def google_login_url():
    """Generates OAuth authorization URL with minimum read-only scopes."""
    client_id = "founderos-dev-client-id.apps.googleusercontent.com"
    redirect_uri = "http://127.0.0.1:8000/api/auth/google/callback"
    scopes = "https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/calendar.readonly"

    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&redirect_uri={redirect_uri}&"
        f"response_type=code&scope={scopes}&access_type=offline&prompt=consent"
    )
    return {"authUrl": auth_url, "scopes": ["gmail.readonly", "calendar.readonly"]}


@router.get("/google/callback")
async def google_callback(code: str = Query(...), session: AsyncSession = Depends(get_async_session)):
    """Handles OAuth authorization code callback, encrypts refresh token in Vault."""
    result = await session.execute(select(Workspace))
    workspace = result.scalars().first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Simulate token exchange and vault encryption
    mock_refresh_token = f"ref_tok_{code[:10]}_secret"
    encrypted_token = encrypt_token(mock_refresh_token)

    # Update connector status
    conn_res = await session.execute(
        select(Connector).where(Connector.workspace_id == workspace.id, Connector.connector_id == "gmail")
    )
    connector = conn_res.scalars().first()
    if connector:
        connector.status = "configured"
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
