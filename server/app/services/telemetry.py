"""
FounderOS AI Observability & Token Cost Accounting Service

Tracks token consumption, reasoning effort, execution latency, and financial costs
across all supported AI providers (OpenAI, Anthropic, Gemini, DeepSeek, Groq, Ollama).
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.db import async_session_maker
from app.models import TokenUsageLedger

logger = logging.getLogger("founderos.telemetry")

# Standardized Pricing Catalog (USD per 1,000,000 tokens)
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    # OpenAI
    "gpt-4o": {"prompt": 2.50, "completion": 10.00, "reasoning": 10.00},
    "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60, "reasoning": 0.60},
    "o3-mini": {"prompt": 1.10, "completion": 4.40, "reasoning": 4.40},
    "o1": {"prompt": 15.00, "completion": 60.00, "reasoning": 60.00},
    "gpt-5.6-sol": {"prompt": 3.00, "completion": 12.00, "reasoning": 12.00},

    # Anthropic
    "claude-3-7-sonnet": {"prompt": 3.00, "completion": 15.00, "reasoning": 15.00},
    "claude-3-5-sonnet": {"prompt": 3.00, "completion": 15.00, "reasoning": 15.00},
    "claude-3-5-haiku": {"prompt": 0.80, "completion": 4.00, "reasoning": 4.00},
    "claude-opus-5": {"prompt": 15.00, "completion": 75.00, "reasoning": 75.00},

    # Google Gemini
    "gemini-2.0-flash": {"prompt": 0.10, "completion": 0.40, "reasoning": 0.40},
    "gemini-1.5-pro": {"prompt": 1.25, "completion": 5.00, "reasoning": 5.00},
    "gemini-3.7-flash": {"prompt": 0.15, "completion": 0.60, "reasoning": 0.60},

    # DeepSeek
    "deepseek-chat": {"prompt": 0.14, "completion": 0.28, "reasoning": 0.28},
    "deepseek-reasoner": {"prompt": 0.55, "completion": 2.19, "reasoning": 2.19},
    "deepseek-v4-pro-0813": {"prompt": 0.55, "completion": 2.19, "reasoning": 2.19},

    # Groq & Open Source
    "llama-3.1-8b-instant": {"prompt": 0.05, "completion": 0.08, "reasoning": 0.08},
    "llama-3.3-70b-versatile": {"prompt": 0.59, "completion": 0.79, "reasoning": 0.79},
    "llama-3.1-70b-versatile": {"prompt": 0.59, "completion": 0.79, "reasoning": 0.79},
    "groq-4.6": {"prompt": 2.00, "completion": 8.00, "reasoning": 8.00},
    "kimi-k3": {"prompt": 1.00, "completion": 3.00, "reasoning": 3.00},
    "glm-5.2": {"prompt": 1.00, "completion": 3.00, "reasoning": 3.00},

    # Local / Private Ollama (Zero API Cost)
    "ollama": {"prompt": 0.0, "completion": 0.0, "reasoning": 0.0},
    "default": {"prompt": 1.00, "completion": 3.00, "reasoning": 3.00},
}


def count_tokens_approx(text: str) -> int:
    """Heuristic approximation: 1 token ~ 0.75 words (or ~4 chars)."""
    if not text:
        return 0
    words = len(text.split())
    return max(1, int(words * 1.33))


def estimate_cost(
    provider: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    reasoning_tokens: int = 0
) -> float:
    """Calculates estimated USD cost for an inference call based on model rates."""
    if provider.lower() in ["ollama", "local"]:
        return 0.0

    pricing = None
    # 1. Exact model match
    for k, v in MODEL_PRICING.items():
        if k in model.lower():
            pricing = v
            break

    # 2. Fallback to default
    if not pricing:
        pricing = MODEL_PRICING["default"]

    prompt_cost = (prompt_tokens / 1_000_000.0) * pricing["prompt"]
    completion_cost = (completion_tokens / 1_000_000.0) * pricing["completion"]
    reasoning_cost = (reasoning_tokens / 1_000_000.0) * pricing.get("reasoning", pricing["completion"])

    return round(prompt_cost + completion_cost + reasoning_cost, 6)


async def record_token_usage(
    workspace_id: int,
    provider: str,
    model: str,
    call_type: str,
    prompt_tokens: int,
    completion_tokens: int,
    latency_ms: float,
    reasoning_tokens: int = 0
) -> Optional[TokenUsageLedger]:
    """Records an inference event in the TokenUsageLedger table asynchronously."""
    cost = estimate_cost(provider, model, prompt_tokens, completion_tokens, reasoning_tokens)

    try:
        async with async_session_maker() as session:
            entry = TokenUsageLedger(
                workspace_id=workspace_id,
                provider=provider,
                model=model,
                call_type=call_type,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                reasoning_tokens=reasoning_tokens,
                latency_ms=round(latency_ms, 2),
                estimated_cost_usd=cost,
                created_at=datetime.now(timezone.utc)
            )
            session.add(entry)
            await session.commit()
            await session.refresh(entry)
            return entry
    except Exception as e:
        logger.warning(f"Failed to record token usage telemetry: {e}")
        return None
