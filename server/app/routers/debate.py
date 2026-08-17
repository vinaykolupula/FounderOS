"""
Executive Board Debate Router

Triggers concurrent multi-agent C-suite board debates (CRO, Skeptic, VP CS, CFO, CTO) 
to evaluate strategic decisions against real-time company constraints.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db import get_async_session
from app.models import Workspace, CompanyProfile
from app.services.llm import LLMEngine

router = APIRouter(prefix="/api/debate", tags=["Executive Board Debate Engine"])


class DebateRequestSchema(BaseModel):
    decisionTitle: str = Field(..., max_length=255)


@router.post("")
async def trigger_executive_debate(payload: DebateRequestSchema, session: AsyncSession = Depends(get_async_session)):
    """Triggers multi-perspective AI Executive Board debate powered by LLM agents."""
    result = await session.execute(select(Workspace))
    workspace = result.scalars().first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    company_res = await session.execute(select(CompanyProfile).where(CompanyProfile.workspace_id == workspace.id))
    company = company_res.scalars().first()

    company_context = {
        "objective": company.objective if company else "Reach target MRR",
        "primaryConstraint": company.primary_constraint if company else "First-value completion",
        "runwayFloor": f"{company.runway_months} months" if company else "12 months",
        "idealCustomer": company.ideal_customer if company else "Mid-market logistics teams",
        "burnRate": company.burn_rate if company else "Unknown",
        "gtmMotion": company.gtm_motion if company else "Product-Led Growth",
        "techStack": company.tech_stack if company else "React, Node.js, Postgres",
        "competitiveMoat": company.competitive_moat if company else "First mover advantage",
    }

    # Runs live LLM Multi-Agent Debate engine (with graceful fallback if no API key set)
    debate_result = await LLMEngine.run_multi_agent_executive_debate(payload.decisionTitle, company_context)
    return debate_result
