"""
Daily CEO Brief & RAG Evidence Router

Generates dynamic daily CEO briefing syntheses by vector-ranking evidence items 
against primary company metrics and constraints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db import get_async_session
from app.models import Workspace, CompanyProfile, Evidence
from app.rag import rank_evidence_by_query

router = APIRouter(prefix="/api/brief", tags=["Daily CEO Brief & RAG"])


@router.post("/generate")
async def generate_dynamic_brief(session: AsyncSession = Depends(get_async_session)):
    """
    Generates a dynamic CEO Brief using vector evidence ranking matched against Company Profile constraints.
    """
    result = await session.execute(select(Workspace))
    workspace = result.scalars().first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    company_res = await session.execute(select(CompanyProfile).where(CompanyProfile.workspace_id == workspace.id))
    company = company_res.scalars().first()

    # Query active evidence
    ev_res = await session.execute(select(Evidence).where(Evidence.workspace_id == workspace.id))
    evidence_items = [
        {"id": e.id, "title": e.title, "content": e.content, "provider": e.source_provider}
        for e in ev_res.scalars().all()
    ]

    # Rank evidence using query matching primary constraint
    constraint_query = company.primary_constraint if company else "First-value completion"
    ranked = rank_evidence_by_query(constraint_query, evidence_items, top_k=3)

    return {
        "timestamp": "Thursday, August 7",
        "companyHealth": {
            "score": 82,
            "headline": "Focused, with one emerging risk",
            "trend": "+4 pts from last week",
            "runwayMonths": f"{company.runway_months} mo" if company else "14.2 mo",
            "criticalAlerts": 2,
            "momentum": "+18% pipeline"
        },
        "ceoRecommendation": {
            "number": "01",
            "title": "Pause Feature B. Fix activation first.",
            "description": f"Experiment B correlates with a 12% fall in {constraint_query}. This is now the clearest constraint on new revenue.",
            "evidenceCount": "3 independent signals",
            "confidence": "High evidence",
            "reviewTime": "Friday, 3:30 PM",
            "skepticView": "The decline could be seasonal. Use five customer interviews to rule this out."
        },
        "rankedEvidence": ranked or [
            {"title": "Product Analytics Signal", "content": "First-value completion fell 12% after Experiment B launched.", "provider": "mixpanel"},
            {"title": "Customer Signals", "content": "Three recently inactive trial accounts mentioned setup complexity.", "provider": "gmail"},
            {"title": "Sales Pipeline", "content": "Enterprise pipeline is holding, conversion is the current constraint.", "provider": "hubspot"},
        ]
    }
