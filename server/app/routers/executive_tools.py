"""
Executive Daily Operating Tools Router

Exposes high-leverage daily workflows for the C-Suite:
- CEO: Investor Update Synthesizer & LNO Task Prioritizer
- CFO: Default Alive Runway Lab & What-If Hiring Simulator
- CTO: Gary Klein Pre-Mortem & Boring Tech ADR Generator
- CRO: MEDDPICC Deal Health Radar & Objection Coach
- VP CS: Superhuman PMF Engine
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db import get_async_session
from app.auth import get_current_workspace
from app.models import Workspace, ActionItem
from app.services.investor_update import InvestorUpdateService
from app.services.lno_prioritizer import LNOClassificationService
from app.services.runway_lab import RunwayScenarioService
from app.services.technical_rfc import TechnicalRfcService
from app.services.deal_radar import DealInspectionService
from app.services.pmf_engine import PMFEngineService

router = APIRouter(prefix="/api/executive-tools", tags=["Executive Daily Operations"])


# ==========================================
# CEO / Solo Founder Endpoints
# ==========================================

class GenerateInvestorUpdateSchema(BaseModel):
    monthYear: Optional[str] = None
    customHighlights: Optional[List[str]] = None
    customLowlights: Optional[List[str]] = None
    customAsks: Optional[List[str]] = None


class StageInvestorActionSchema(BaseModel):
    subjectLine: str
    fullMarkdown: str


@router.post("/investor-update/generate")
async def generate_investor_update(
    payload: GenerateInvestorUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
    workspace: Workspace = Depends(get_current_workspace)
):
    if not workspace or workspace.id is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    result = await InvestorUpdateService.generate_investor_update(
        session=session,
        workspace_id=workspace.id,
        month_year=payload.monthYear,
        custom_highlights=payload.customHighlights,
        custom_lowlights=payload.customLowlights,
        custom_asks=payload.customAsks
    )
    return result


@router.post("/investor-update/stage-action")
async def stage_investor_update_action(
    payload: StageInvestorActionSchema,
    session: AsyncSession = Depends(get_async_session),
    workspace: Workspace = Depends(get_current_workspace)
):
    if not workspace or workspace.id is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    action = ActionItem(
        workspace_id=workspace.id,
        title=f"Send Investor Update: {payload.subjectLine}",
        detail=payload.fullMarkdown,
        source="CEO Investor Engine",
        action_type="email_broadcast",
        status="Ready",
        payload={"subject": payload.subjectLine, "body": payload.fullMarkdown}
    )
    session.add(action)
    await session.commit()
    await session.refresh(action)

    return {"message": "Investor update staged to Action Queue for sign-off", "actionId": action.id}


class ClassifyLnoSchema(BaseModel):
    tasks: List[Dict[str, Any]]


@router.post("/tasks/classify-lno")
async def classify_tasks_lno(payload: ClassifyLnoSchema):
    results = await LNOClassificationService.classify_tasks_batch(payload.tasks)
    return {"classifiedTasks": results}


# ==========================================
# CFO / Finance Lead Endpoints
# ==========================================

class RunwayAnalysisSchema(BaseModel):
    cashBalance: float = Field(..., ge=0)
    monthlyBurn: float = Field(..., ge=0)
    monthlyRevenue: float = Field(..., ge=0)
    momGrowthRate: float = Field(default=0.05, ge=0)


class ScenarioSimulationSchema(BaseModel):
    cashBalance: float = Field(..., ge=0)
    monthlyBurn: float = Field(..., ge=0)
    monthlyRevenue: float = Field(..., ge=0)
    momGrowthRate: float = Field(default=0.05, ge=0)
    headcountDelta: int = Field(default=0)
    avgAnnualSalary: float = Field(default=140000.0, ge=0)
    revGrowthDeltaPct: float = Field(default=0.0)
    monthlyToolingSpendDelta: float = Field(default=0.0)


@router.post("/finance/runway-analysis")
async def calculate_runway_analysis(payload: RunwayAnalysisSchema):
    result = RunwayScenarioService.calculate_default_alive_status(
        cash_balance=payload.cashBalance,
        monthly_burn=payload.monthlyBurn,
        monthly_revenue=payload.monthlyRevenue,
        mom_growth_rate=payload.momGrowthRate
    )
    return result


@router.post("/finance/simulate-scenario")
async def simulate_financial_scenario(payload: ScenarioSimulationSchema):
    result = RunwayScenarioService.simulate_scenario(
        base_cash=payload.cashBalance,
        base_monthly_burn=payload.monthlyBurn,
        base_monthly_rev=payload.monthlyRevenue,
        base_growth_rate=payload.momGrowthRate,
        headcount_delta=payload.headcountDelta,
        avg_annual_salary=payload.avgAnnualSalary,
        rev_growth_delta_pct=payload.revGrowthDeltaPct,
        monthly_tooling_spend_delta=payload.monthlyToolingSpendDelta
    )
    return result


# ==========================================
# CTO / Technical Lead Endpoints
# ==========================================

class PreMortemSchema(BaseModel):
    proposalTitle: str = Field(..., max_length=255)
    technicalScope: str = Field(..., max_length=2000)
    techStack: Optional[str] = "FastAPI + React + PostgreSQL"
    primaryConstraint: Optional[str] = "Engineering team bandwidth"


class AdrGeneratorSchema(BaseModel):
    title: str = Field(..., max_length=255)
    contextProblem: str = Field(..., max_length=2000)
    optionsConsidered: List[str]
    chosenSolution: str
    techStack: Optional[str] = "FastAPI + React + PostgreSQL"


@router.post("/technical/pre-mortem")
async def run_pre_mortem(payload: PreMortemSchema):
    result = await TechnicalRfcService.run_gary_klein_pre_mortem(
        proposal_title=payload.proposalTitle,
        technical_scope=payload.technicalScope,
        tech_stack=payload.techStack or "FastAPI + React + PostgreSQL",
        primary_constraint=payload.primaryConstraint or "Engineering team bandwidth"
    )
    return result


@router.post("/technical/adr")
async def generate_adr(payload: AdrGeneratorSchema):
    result = await TechnicalRfcService.generate_architecture_decision_record(
        title=payload.title,
        context_problem=payload.contextProblem,
        options_considered=payload.optionsConsidered,
        chosen_solution=payload.chosenSolution,
        tech_stack=payload.techStack or "FastAPI + React + PostgreSQL"
    )
    return result


# ==========================================
# CRO / Head of Sales Endpoints
# ==========================================

class MeddpiccScorecardSchema(BaseModel):
    metricsDefined: bool = True
    hasEconomicBuyer: bool = False
    decisionCriteriaKnown: bool = True
    decisionProcessMapped: bool = False
    paperProcessMapped: bool = False
    painImplicated: bool = True
    hasChampion: bool = True
    competitionIdentified: bool = True


class ObjectionCoachSchema(BaseModel):
    objection: str = Field(..., max_length=500)
    prospectRole: Optional[str] = "VP of Engineering"
    productValueProp: Optional[str] = "Faster autonomous execution with security guardrails"


@router.post("/sales/meddpicc-audit")
async def audit_meddpicc_deal(payload: MeddpiccScorecardSchema):
    result = DealInspectionService.calculate_meddpicc_scorecard(
        metrics_defined=payload.metricsDefined,
        has_economic_buyer=payload.hasEconomicBuyer,
        decision_criteria_known=payload.decisionCriteriaKnown,
        decision_process_mapped=payload.decisionProcessMapped,
        paper_process_mapped=payload.paperProcessMapped,
        pain_implicated=payload.painImplicated,
        has_champion=payload.hasChampion,
        competition_identified=payload.competitionIdentified
    )
    return result


@router.post("/sales/objection-coach")
async def coach_sales_objection(payload: ObjectionCoachSchema):
    result = await DealInspectionService.generate_objection_response(
        objection=payload.objection,
        prospect_role=payload.prospectRole or "VP of Engineering",
        product_value_prop=payload.productValueProp or "Faster autonomous execution"
    )
    return result


# ==========================================
# VP CS / Product Lead Endpoints
# ==========================================

class PmfScoreSchema(BaseModel):
    veryDisappointedCount: int = Field(..., ge=0)
    somewhatDisappointedCount: int = Field(..., ge=0)
    notDisappointedCount: int = Field(..., ge=0)


class PmfFeedbackSchema(BaseModel):
    feedbackItems: List[Dict[str, str]]


@router.post("/product/pmf-score")
async def calculate_pmf_score(payload: PmfScoreSchema):
    result = PMFEngineService.calculate_pmf_score(
        very_disappointed_count=payload.veryDisappointedCount,
        somewhat_disappointed_count=payload.somewhatDisappointedCount,
        not_disappointed_count=payload.notDisappointedCount
    )
    return result


@router.post("/product/pmf-analysis")
async def analyze_pmf_feedback(payload: PmfFeedbackSchema):
    result = await PMFEngineService.analyze_pmf_feedback(payload.feedbackItems)
    return result
