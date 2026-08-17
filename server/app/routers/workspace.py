
"""
Workspace Router Module

Provides endpoints for root workspace state retrieval, first-run onboarding completion,
company & founder profile updates, approval-gated action queue approvals, decision ledger CRUD,
system connector management, and full workspace data purging (reset).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlmodel import select, delete
from pydantic import BaseModel, Field
from typing import List, Optional
from app.db import get_async_session
from app.models import Workspace, CompanyProfile, FounderProfile, Connector, ActionItem, Decision, AuditLog, Task, Evidence, BusinessModelEnum, PlatformFocusEnum, FundingStateEnum, RevenueRangeEnum, StageEnum, TeamSizeEnum, FounderRole, FounderBackground, ExperienceLevel, FounderSuperpower

router = APIRouter(prefix="/api", tags=["Workspace"])



class CompanyUpdateSchema(BaseModel):
    name: str = Field(..., max_length=255)
    
    websiteUrl: Optional[str] = Field(None, max_length=500, pattern=r"^(https?://)?([\da-z\.-]+)\.([a-z\.]{2,6})([/\w \.-]*)*/?$")
    linkedinUrl: Optional[str] = Field(None, max_length=500, pattern=r"^(https?://)?(www\.)?linkedin\.com/.*$")
    socialUrl: Optional[str] = Field(None, max_length=500, pattern=r"^(https?://)?.*$")
    
    businessModel: Optional[BusinessModelEnum] = None
    platformFocus: Optional[PlatformFocusEnum] = None
    fundingState: Optional[FundingStateEnum] = None
    revenueRange: Optional[RevenueRangeEnum] = None
    
    stage: StageEnum
    teamSize: TeamSizeEnum
    idealCustomer: str = Field(..., max_length=500)
    objective: str = Field(..., max_length=1000)
    primaryMetric: str = Field(..., max_length=500)
    primaryConstraint: str = Field(..., max_length=500)
    runwayMonths: int = Field(..., ge=0, le=120)


class FounderUpdateSchema(BaseModel):
    name: str = Field(..., max_length=255)
    role: FounderRole
    background: FounderBackground
    experienceLevel: ExperienceLevel
    domainExpertise: str = Field(..., max_length=500)
    superpower: FounderSuperpower
    primaryGap: FounderSuperpower
    learningFocus: str = Field(..., max_length=500)

class OnboardingSchema(BaseModel):
    company: CompanyUpdateSchema
    founder: FounderUpdateSchema
    selectedConnectors: List[str]


class NewDecisionSchema(BaseModel):
    title: str = Field(..., max_length=255)
    detail: str = Field(..., max_length=2000)
    status: Optional[str] = "Open"


@router.get("/workspace")
async def get_workspace(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Workspace))
    workspace = result.scalars().first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    company_res = await session.execute(select(CompanyProfile).where(CompanyProfile.workspace_id == workspace.id))
    company = company_res.scalars().first()

    founder_res = await session.execute(select(FounderProfile).where(FounderProfile.workspace_id == workspace.id))
    founder = founder_res.scalars().first()

    connectors_res = await session.execute(select(Connector).where(Connector.workspace_id == workspace.id))
    connectors = connectors_res.scalars().all()

    actions_res = await session.execute(select(ActionItem).where(ActionItem.workspace_id == workspace.id, ActionItem.status != "Approved"))
    actions = actions_res.scalars().all()

    decisions_res = await session.execute(select(Decision).where(Decision.workspace_id == workspace.id))
    decisions = decisions_res.scalars().all()

    # Safe company model fallback dictionary
    company_data = {
        "name": company.name if company else "FounderOS",
        "websiteUrl": company.website_url if company else "",
        "linkedinUrl": company.linkedin_url if company else "",
        "socialUrl": company.social_url if company else "",
        "businessModel": company.business_model if company else "B2B SaaS",
        "platformFocus": company.platform_focus if company else "Web Application",
        "fundingState": company.funding_state if company else "Bootstrapped",
        "revenueRange": company.revenue_range if company else "$10k-$100k MRR",
        "stage": company.stage if company else "Early revenue",
        "teamSize": company.team_size if company else "1–10 people",
        "idealCustomer": company.ideal_customer if company else "Mid-market logistics teams",
        "objective": company.objective if company else "Reach $60k MRR with sustainable activation",
        "primaryMetric": company.primary_metric if company else "Weekly activated accounts",
        "primaryConstraint": company.primary_constraint if company else "First-value completion",
        "runwayMonths": company.runway_months if company else 12,
        "burnRate": company.burn_rate if company else "Unknown",
        "gtmMotion": company.gtm_motion if company else "Product-Led Growth",
        "techStack": company.tech_stack if company else "React, Node.js, Postgres",
        "competitiveMoat": company.competitive_moat if company else "First mover advantage",
    }

    return {
        "id": str(workspace.id),
        "isOnboarded": workspace.is_onboarded,
        "company": company_data,
        "founder": {
            "name": founder.name if founder else "",
            "role": founder.role if founder else "Solo Founder",
            "background": founder.background if founder else "Engineering / Technical",
            "experienceLevel": founder.experience_level if founder else "First-time Founder",
            "domainExpertise": founder.domain_expertise if founder else "",
            "superpower": founder.superpower if founder else "Building & Engineering",
            "primaryGap": founder.primary_gap if founder else "Sales & Closing Deals",
            "learningFocus": founder.learning_focus if founder else "",
            "communicationStyle": founder.communication_style if founder else "Direct and brief",
            "energyState": founder.energy_state if founder else "Steady pace",
            "coreValues": founder.core_values if founder else "Speed, Customer Obsession",
        } if founder else None,
        "connectors": [
            {
                "id": c.connector_id,
                "name": c.name,
                "description": c.description,
                "category": c.category,
                "status": c.status
            }
            for c in connectors
        ],
        "actions": [
            {
                "id": a.id,
                "title": a.title,
                "detail": a.detail,
                "source": a.source,
                "status": a.status
            }
            for a in actions
        ],
        "decisions": [
            {
                "id": d.id,
                "decisionCode": d.decision_code,
                "title": d.title,
                "detail": d.detail,
                "status": d.status
            }
            for d in decisions
        ]
    }


@router.post("/onboarding")
async def complete_onboarding(payload: OnboardingSchema, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Workspace))
    workspace = result.scalars().first()
    if not workspace:
        workspace = Workspace(is_onboarded=True)
        session.add(workspace)
        await session.commit()
        await session.refresh(workspace)
    else:
        workspace.is_onboarded = True
        session.add(workspace)
        
    assert workspace.id is not None

    # Update company profile
    c_res = await session.execute(select(CompanyProfile).where(CompanyProfile.workspace_id == workspace.id))
    company = c_res.scalars().first()
    if not company:
        company = CompanyProfile(workspace_id=workspace.id, **payload.company.model_dump())
    else:
        company.name = payload.company.name
        company.website_url = payload.company.websiteUrl
        company.linkedin_url = payload.company.linkedinUrl
        company.social_url = payload.company.socialUrl
        company.business_model = payload.company.businessModel
        company.platform_focus = payload.company.platformFocus
        company.funding_state = payload.company.fundingState
        company.revenue_range = payload.company.revenueRange
        company.stage = payload.company.stage
        company.team_size = payload.company.teamSize
        company.ideal_customer = payload.company.idealCustomer
        company.objective = payload.company.objective
        company.primary_metric = payload.company.primaryMetric
        company.primary_constraint = payload.company.primaryConstraint
        company.runway_months = payload.company.runwayMonths
        
        # Deep Company Context
        company.burn_rate = getattr(payload.company, 'burnRate', "Unknown")
        company.gtm_motion = getattr(payload.company, 'gtmMotion', "Product-Led Growth")
        company.tech_stack = getattr(payload.company, 'techStack', "React, Node.js, Postgres")
        company.competitive_moat = getattr(payload.company, 'competitiveMoat', "First mover advantage")
    session.add(company)

    # Update founder profile
    f_res = await session.execute(select(FounderProfile).where(FounderProfile.workspace_id == workspace.id))
    founder_profile = f_res.scalars().first()
    if not founder_profile:
        founder_profile = FounderProfile(
            workspace_id=workspace.id,
            name=payload.founder.name,
            role=payload.founder.role,
            background=payload.founder.background,
            experience_level=payload.founder.experienceLevel,
            domain_expertise=payload.founder.domainExpertise,
            superpower=payload.founder.superpower,
            primary_gap=payload.founder.primaryGap,
            learning_focus=payload.founder.learningFocus,
        )
    else:
        founder_profile.name = payload.founder.name
        founder_profile.role = payload.founder.role
        founder_profile.background = payload.founder.background
        founder_profile.experience_level = payload.founder.experienceLevel
        founder_profile.domain_expertise = payload.founder.domainExpertise
        founder_profile.superpower = payload.founder.superpower
        founder_profile.primary_gap = payload.founder.primaryGap
        founder_profile.learning_focus = payload.founder.learningFocus
        
        # Deep Founder Context
        founder_profile.communication_style = getattr(payload.founder, 'communicationStyle', "Direct and brief")
        founder_profile.energy_state = getattr(payload.founder, 'energyState', "Steady pace")
        founder_profile.core_values = getattr(payload.founder, 'coreValues', "Speed, Customer Obsession")
    session.add(founder_profile)

    # Update connectors safely
    connectors_res = await session.execute(select(Connector).where(Connector.workspace_id == workspace.id))
    connectors = connectors_res.scalars().all()
    for conn in connectors:
        if conn.connector_id in payload.selectedConnectors:
            conn.status = "configured"
            session.add(conn)

    audit = AuditLog(
        workspace_id=workspace.id,
        actor="founder",
        event="ONBOARDING_COMPLETED",
        details={"selectedConnectors": payload.selectedConnectors}
    )
    session.add(audit)

    await session.commit()
    return {"message": "Onboarding saved successfully"}


@router.put("/company")
async def update_company(payload: CompanyUpdateSchema, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Workspace))
    workspace = result.scalars().first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    assert workspace.id is not None

    c_res = await session.execute(select(CompanyProfile).where(CompanyProfile.workspace_id == workspace.id))
    company = c_res.scalars().first()
    if not company:
        company = CompanyProfile(workspace_id=workspace.id, **payload.model_dump(exclude_unset=True))
    else:
        company.name = payload.name
        company.website_url = payload.websiteUrl
        company.linkedin_url = payload.linkedinUrl
        company.social_url = payload.socialUrl
        company.business_model = payload.businessModel
        company.platform_focus = payload.platformFocus
        company.funding_state = payload.fundingState
        company.revenue_range = payload.revenueRange
        company.stage = payload.stage
        company.team_size = payload.teamSize
        company.ideal_customer = payload.idealCustomer
        company.objective = payload.objective
        company.primary_metric = payload.primaryMetric
        company.primary_constraint = payload.primaryConstraint
        company.runway_months = payload.runwayMonths
        company.burn_rate = getattr(payload, 'burnRate', company.burn_rate)
        company.gtm_motion = getattr(payload, 'gtmMotion', company.gtm_motion)
        company.tech_stack = getattr(payload, 'techStack', company.tech_stack)
        company.competitive_moat = getattr(payload, 'competitiveMoat', company.competitive_moat)
    session.add(company)
    await session.commit()

    return {"message": "Company model updated"}

@router.put("/founder")
async def update_founder(payload: FounderUpdateSchema, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Workspace))
    workspace = result.scalars().first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    assert workspace.id is not None

    f_res = await session.execute(select(FounderProfile).where(FounderProfile.workspace_id == workspace.id))
    founder_profile = f_res.scalars().first()
    if not founder_profile:
        founder_profile = FounderProfile(
            workspace_id=workspace.id,
            name=payload.name,
            role=payload.role,
            background=payload.background,
            experience_level=payload.experienceLevel,
            domain_expertise=payload.domainExpertise,
            superpower=payload.superpower,
            primary_gap=payload.primaryGap,
            learning_focus=payload.learningFocus
        )
    else:
        founder_profile.name = payload.name
        founder_profile.role = payload.role
        founder_profile.background = payload.background
        founder_profile.experience_level = payload.experienceLevel
        founder_profile.domain_expertise = payload.domainExpertise
        founder_profile.superpower = payload.superpower
        founder_profile.primary_gap = payload.primaryGap
        founder_profile.learning_focus = payload.learningFocus
        founder_profile.communication_style = getattr(payload, 'communicationStyle', founder_profile.communication_style)
        founder_profile.energy_state = getattr(payload, 'energyState', founder_profile.energy_state)
        founder_profile.core_values = getattr(payload, 'coreValues', founder_profile.core_values)
    session.add(founder_profile)
    await session.commit()

    return {"message": "Founder profile updated"}


@router.post("/actions/{action_id}/approve")
async def approve_action(action_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(ActionItem).where(ActionItem.id == action_id))
    action = result.scalars().first()
    if not action:
        raise HTTPException(status_code=404, detail="Action item not found")

    action.status = "Approved"
    session.add(action)

    # Dispatch action via live platforms dispatcher
    from app.services.dispatchers import ActionDispatcher
    dispatch_res = await ActionDispatcher.dispatch_approved_action(action.id, action.title, action.detail, action.source, session)

    audit = AuditLog(
        workspace_id=action.workspace_id,
        actor="founder",
        event="ACTION_APPROVED_AND_DISPATCHED",
        details={"actionId": action.id, "title": action.title, "receipt": dispatch_res.get("receipt")}
    )
    session.add(audit)

    await session.commit()
    return {"message": f"Action '{action.title}' approved and dispatched", "dispatch": dispatch_res}


@router.post("/connectors/{connector_id}/configure")
async def configure_connector(connector_id: str, session: AsyncSession = Depends(get_async_session)):
    ws_result = await session.execute(select(Workspace))
    workspace = ws_result.scalars().first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    result = await session.execute(
        select(Connector).where(
            Connector.workspace_id == workspace.id,
            Connector.connector_id == connector_id
        )
    )
    connector = result.scalars().first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")

    connector.status = "configured"
    
    # Simulate an OAuth code exchange and vault encryption
    from app.vault import encrypt_token
    mock_token = f"ya29.a0AfB_{connector_id}_mock_token_123"
    connector.encrypted_oauth_token = encrypt_token(mock_token)
    
    session.add(connector)

    audit = AuditLog(
        workspace_id=connector.workspace_id,
        actor="founder",
        event="CONNECTOR_CONFIGURED_WITH_OAUTH",
        details={"connectorId": connector_id}
    )
    session.add(audit)

    await session.commit()
    return {"message": f"Connector '{connector.name}' setup saved and OAuth token vaulted"}


@router.post("/decisions")
async def create_decision(payload: NewDecisionSchema, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Workspace))
    workspace = result.scalars().first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Fast indexed count
    count_res = await session.execute(select(func.count(Decision.id)).where(Decision.workspace_id == workspace.id))
    total_decisions = count_res.scalar_one_or_none() or 0
    next_code = f"#{total_decisions + 25:03d}"

    decision = Decision(
        workspace_id=workspace.id,
        decision_code=next_code,
        title=payload.title,
        detail=payload.detail,
        status=payload.status or "Open"
    )
    session.add(decision)
    await session.commit()
    await session.refresh(decision)

    return {"message": "Decision record created", "decision": decision}

@router.delete("/workspace")
async def reset_workspace(session: AsyncSession = Depends(get_async_session)):
    """Deletes all workspace data securely to reset the system."""
    result = await session.execute(select(Workspace))
    workspace = result.scalars().first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    assert workspace.id is not None
    wid = workspace.id

    # Parameterized ORM deletes to avoid SQL injection
    await session.execute(delete(CompanyProfile).where(CompanyProfile.workspace_id == wid))
    await session.execute(delete(FounderProfile).where(FounderProfile.workspace_id == wid))
    await session.execute(delete(ActionItem).where(ActionItem.workspace_id == wid))
    await session.execute(delete(Decision).where(Decision.workspace_id == wid))
    await session.execute(delete(Task).where(Task.workspace_id == wid))
    await session.execute(delete(Evidence).where(Evidence.workspace_id == wid))
    await session.execute(delete(AuditLog).where(AuditLog.workspace_id == wid))
    await session.execute(delete(Connector).where(Connector.workspace_id == wid))

    # Re-seed default connectors in pristine unconfigured state
    default_connectors = [
        Connector(workspace_id=wid, connector_id="gmail", name="Google Workspace", description="Email and calendar signals", category="Communication", status="not_connected"),
        Connector(workspace_id=wid, connector_id="slack", name="Slack", description="Team decisions and delivery context", category="Communication", status="not_connected"),
        Connector(workspace_id=wid, connector_id="linear", name="Linear", description="Product and engineering execution", category="Product", status="not_connected"),
        Connector(workspace_id=wid, connector_id="hubspot", name="HubSpot", description="Deals, pipeline, and customer history", category="Revenue", status="not_connected"),
        Connector(workspace_id=wid, connector_id="stripe", name="Stripe", description="Revenue, subscriptions, and churn", category="Finance", status="not_connected"),
    ]
    for c in default_connectors:
        session.add(c)

    workspace.is_onboarded = False
    session.add(workspace)
    await session.commit()

    # Notify connected clients via WebSocket
    from app.services.events import manager
    await manager.broadcast_refresh(str(workspace.id))

    return {"message": "Workspace reset successfully"}
