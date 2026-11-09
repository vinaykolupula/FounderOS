"""
Executive Board Debate Router

Triggers concurrent multi-agent C-suite board debates (CRO, Skeptic, VP CS, CFO, CTO) 
to evaluate strategic decisions against real-time company constraints.
"""

import json
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db import get_async_session
from app.auth import get_current_workspace
from app.models import Workspace, CompanyProfile
from app.services.llm import LLMEngine

router = APIRouter(prefix="/api/debate", tags=["Executive Board Debate Engine"])


class DebateRequestSchema(BaseModel):
    decisionTitle: str = Field(..., max_length=255)


def _build_company_context(company: CompanyProfile | None) -> dict:
    return {
        "objective": company.objective if company else "Reach target MRR",
        "primaryConstraint": company.primary_constraint if company else "First-value completion",
        "runwayFloor": f"{company.runway_months} months" if company else "12 months",
        "idealCustomer": company.ideal_customer if company else "Mid-market logistics teams",
        "burnRate": company.burn_rate if company else "Unknown",
        "gtmMotion": company.gtm_motion if company else "Product-Led Growth",
        "techStack": company.tech_stack if company else "React, Node.js, Postgres",
        "competitiveMoat": company.competitive_moat if company else "First mover advantage",
    }


@router.post("")
async def trigger_executive_debate(
    payload: DebateRequestSchema,
    session: AsyncSession = Depends(get_async_session),
    workspace: Workspace = Depends(get_current_workspace)
):
    """Triggers multi-perspective AI Executive Board debate powered by LLM agents."""
    if not workspace or workspace.id is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    company_res = await session.execute(select(CompanyProfile).where(CompanyProfile.workspace_id == workspace.id))
    company = company_res.scalars().first()
    company_context = _build_company_context(company)

    # Runs live LLM Multi-Agent Debate engine (with graceful fallback if no API key set)
    debate_result = await LLMEngine.run_multi_agent_executive_debate(payload.decisionTitle, company_context)
    return debate_result


@router.get("/stream")
async def stream_executive_debate(
    decisionTitle: str = Query(..., max_length=255),
    session: AsyncSession = Depends(get_async_session),
    workspace: Workspace = Depends(get_current_workspace)
):
    """
    Streams multi-perspective AI Executive Board debate via Server-Sent Events (SSE).
    Emits events: round1_start, round1_persona, round2_start, round2_dialectic, round3_start, debate_complete.
    """
    if not workspace or workspace.id is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    company_res = await session.execute(select(CompanyProfile).where(CompanyProfile.workspace_id == workspace.id))
    company = company_res.scalars().first()
    company_context = _build_company_context(company)

    async def sse_event_stream():
        async for item in LLMEngine.stream_multi_agent_executive_debate(decisionTitle, company_context):
            event_name = item.get("event", "message")
            data_str = json.dumps(item.get("data", {}))
            yield f"event: {event_name}\ndata: {data_str}\n\n"

    return StreamingResponse(
        sse_event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

