"""
AI Observability & Token Cost Accounting Router

Exposes endpoints for tracking AI provider spend, token consumption, inference latency,
and model ROI across C-suite board debates, morning briefings, and autonomous tasks.
"""

from typing import Dict, Any, List
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc
from app.db import get_async_session
from app.auth import get_current_workspace
from app.models import Workspace, TokenUsageLedger

router = APIRouter(prefix="/api/observability", tags=["AI Observability & Cost Engine"])


@router.get("/usage")
async def get_token_usage_summary(
    session: AsyncSession = Depends(get_async_session),
    workspace: Workspace = Depends(get_current_workspace)
) -> Dict[str, Any]:
    """Returns aggregated AI token consumption, latency, and estimated USD spend."""
    if not workspace or workspace.id is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    result = await session.execute(
        select(TokenUsageLedger)
        .where(TokenUsageLedger.workspace_id == workspace.id)
        .order_by(desc(TokenUsageLedger.created_at))
    )
    records = result.scalars().all()

    total_tokens = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_reasoning_tokens = 0
    total_cost_usd = 0.0
    total_latency_ms = 0.0

    provider_map: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"tokens": 0, "cost_usd": 0.0, "calls": 0})
    model_map: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"tokens": 0, "cost_usd": 0.0, "calls": 0})
    daily_map: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"tokens": 0, "cost_usd": 0.0, "calls": 0})

    for r in records:
        entry_tokens = r.prompt_tokens + r.completion_tokens + r.reasoning_tokens
        total_tokens += entry_tokens
        total_prompt_tokens += r.prompt_tokens
        total_completion_tokens += r.completion_tokens
        total_reasoning_tokens += r.reasoning_tokens
        total_cost_usd += r.estimated_cost_usd
        total_latency_ms += r.latency_ms

        # By provider
        prov = r.provider or "unknown"
        provider_map[prov]["tokens"] += entry_tokens
        provider_map[prov]["cost_usd"] += r.estimated_cost_usd
        provider_map[prov]["calls"] += 1

        # By model
        mod = r.model or "default"
        model_map[mod]["tokens"] += entry_tokens
        model_map[mod]["cost_usd"] += r.estimated_cost_usd
        model_map[mod]["calls"] += 1

        # Daily trend
        day_str = r.created_at.strftime("%Y-%m-%d") if r.created_at else datetime.now(timezone.utc).strftime("%Y-%m-%d")
        daily_map[day_str]["tokens"] += entry_tokens
        daily_map[day_str]["cost_usd"] += r.estimated_cost_usd
        daily_map[day_str]["calls"] += 1

    total_inferences = len(records)
    avg_latency = round(total_latency_ms / total_inferences, 1) if total_inferences > 0 else 0.0

    provider_breakdown = [
        {"provider": k, "tokens": v["tokens"], "cost_usd": round(v["cost_usd"], 4), "calls": v["calls"]}
        for k, v in provider_map.items()
    ]
    model_breakdown = [
        {"model": k, "tokens": v["tokens"], "cost_usd": round(v["cost_usd"], 4), "calls": v["calls"]}
        for k, v in model_map.items()
    ]

    # Fill last 7 days for daily trend
    daily_trend = []
    now = datetime.now(timezone.utc)
    for i in range(6, -1, -1):
        d_str = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        daily_trend.append({
            "date": d_str,
            "tokens": daily_map[d_str]["tokens"],
            "cost_usd": round(daily_map[d_str]["cost_usd"], 4),
            "calls": daily_map[d_str]["calls"]
        })

    provider_map_dict = {
        k: {
            "calls": v["calls"],
            "totalTokens": v["tokens"],
            "tokens": v["tokens"],
            "costUsd": round(v["cost_usd"], 4),
            "cost_usd": round(v["cost_usd"], 4),
        }
        for k, v in provider_map.items()
    }

    return {
        "totalSpendUsd": round(total_cost_usd, 4),
        "totalCostUsd": round(total_cost_usd, 4),
        "totalTokens": total_tokens,
        "promptTokens": total_prompt_tokens,
        "completionTokens": total_completion_tokens,
        "reasoningTokens": total_reasoning_tokens,
        "totalInferences": total_inferences,
        "averageLatencyMs": avg_latency,
        "avgLatencyMs": avg_latency,
        "providerBreakdown": provider_map_dict,
        "providerList": provider_breakdown,
        "modelBreakdown": model_breakdown,
        "dailyTrend": daily_trend
    }


@router.get("/recent")
async def get_recent_inferences(
    session: AsyncSession = Depends(get_async_session),
    workspace: Workspace = Depends(get_current_workspace)
) -> List[Dict[str, Any]]:
    """Returns the most recent 25 inference events recorded in the telemetry ledger."""
    if not workspace or workspace.id is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    result = await session.execute(
        select(TokenUsageLedger)
        .where(TokenUsageLedger.workspace_id == workspace.id)
        .order_by(desc(TokenUsageLedger.created_at))
        .limit(25)
    )
    records = result.scalars().all()

    return [
        {
            "id": r.id,
            "provider": r.provider,
            "model": r.model,
            "callType": r.call_type,
            "promptTokens": r.prompt_tokens,
            "completionTokens": r.completion_tokens,
            "reasoningTokens": r.reasoning_tokens,
            "latencyMs": r.latency_ms,
            "estimatedCostUsd": r.estimated_cost_usd,
            "createdAt": r.created_at.isoformat() if r.created_at else None
        }
        for r in records
    ]
