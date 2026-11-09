"""
CEO Executive Morning Briefing Router

Inspired by Y Combinator QM's morning-digest skill:
Serves a daily consolidated executive brief analyzing overnight signals, OMTM tracking,
and recommending the single highest-leverage founder priority today.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db import get_async_session
from app.auth import get_current_workspace
from app.models import Workspace
from app.services.briefing import BriefingService

router = APIRouter(prefix="/api/briefing", tags=["Executive Morning Briefing"])


@router.get("")
async def get_morning_briefing(
    session: AsyncSession = Depends(get_async_session),
    workspace: Workspace = Depends(get_current_workspace)
):
    """Returns a consolidated CEO Morning Briefing synthesized from live startup signals."""
    if not workspace or workspace.id is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    briefing = await BriefingService.generate_morning_briefing(session, workspace.id or 0)
    return briefing
