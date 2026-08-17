"""
Technical RFC, ADR & Gary Klein Pre-Mortem Service (CTO / Technical Architect)

Inspired by Dan McKinley's 'Boring Technology Rule', Amazon's 'Two-Way Door Decisions',
and Gary Klein's 'Pre-Mortem Failure Analysis':
1. Generates structured Architecture Decision Records (ADRs) with innovation token budgeting.
2. Conducts automated Pre-Mortems on major technical migrations to uncover hidden friction points.
"""

from typing import Dict, Any, List, Optional
from app.services.llm import LLMEngine


class TechnicalRfcService:
    """
    Assists the CTO / technical founding team in de-risking architecture and generating ADRs.
    """

    @staticmethod
    async def run_gary_klein_pre_mortem(
        proposal_title: str,
        technical_scope: str,
        tech_stack: str = "FastAPI + React + PostgreSQL",
        primary_constraint: str = "Engineering team bandwidth"
    ) -> Dict[str, Any]:
        """
        Runs a prospective Gary Klein Pre-Mortem: 'Assume this release failed catastrophically in 6 months.'
        """
        system_prompt = """
        You are an elite CTO and Principal Reliability Architect conducting a Gary Klein Pre-Mortem.
        Your goal is NOT to be polite, but to ruthlessly identify realistic failure modes, hidden dependency risks,
        and subtle scaling bottlenecks before code is written.
        
        Respond strictly in valid JSON matching this schema:
        {
            "proposalTitle": "String",
            "catastrophicFailureNarrative": "2-3 sentences vivid post-mortem scenario 6 months from now",
            "topFailureModes": [
                {
                    "mode": "Failure Mode Title",
                    "rootCause": "Deep underlying technical/operational reason",
                    "likelihood": "High | Medium | Low",
                    "severity": "Critical | High | Medium",
                    "preventativeSafeguard": "Concrete engineering action to eliminate this risk today"
                }
            ],
            "reversibilityAssessment": {
                "decisionType": "One-Way Door | Two-Way Door",
                "rollbackPlan": "Step-by-step procedure if this migration must be abandoned in production",
                "innovationTokenBudget": "0 Tokens (Boring Tech) | 1 Token (Justified Novelty) | Dangerous Overhead"
            },
            "recommendation": "PROCEED WITH SAFEGUARDS | REJECT / SIMPLIFY | CONDUCT TIME-BOXED SPIKE"
        }
        """

        prompt = f"""
        Proposed Technical Change: {proposal_title}
        Technical Scope & Plan: {technical_scope}
        Existing Tech Stack: {tech_stack}
        Current Primary Constraint: {primary_constraint}
        """

        try:
            llm_res = await LLMEngine.generate_completion(
                prompt=prompt,
                system_instruction=system_prompt,
                temperature=0.3
            )
            if llm_res:
                import json
                clean_json = llm_res.strip()
                if clean_json.startswith("```json"):
                    clean_json = clean_json[7:-3].strip()
                elif clean_json.startswith("```"):
                    clean_json = clean_json[3:-3].strip()
                return json.loads(clean_json)
        except Exception:
            pass

        # Offline heuristic fallback
        return {
            "proposalTitle": proposal_title,
            "catastrophicFailureNarrative": f"Six months after initiating '{proposal_title}', engineering bandwidth was consumed by subtle operational overhead, leaving core customer roadmap stalled while debugging distributed state.",
            "topFailureModes": [
                {
                    "mode": "Operational & Debugging Overhead",
                    "rootCause": f"Team lacked production runbook experience with newly introduced architecture under {primary_constraint}.",
                    "likelihood": "High",
                    "severity": "Critical",
                    "preventativeSafeguard": "Enforce Dan McKinley's Boring Tech rule: Favor existing proven PostgreSQL/FastAPI components."
                },
                {
                    "mode": "Data Migration / State Drift",
                    "rootCause": "Lack of automated schema dual-write verification during the transition window.",
                    "likelihood": "Medium",
                    "severity": "High",
                    "preventativeSafeguard": "Implement dark-traffic dual-write verification for 14 days before cutting over."
                }
            ],
            "reversibilityAssessment": {
                "decisionType": "Two-Way Door",
                "rollbackPlan": "Maintain shadow reads and feature-flagged routing to switch back in under 60 seconds.",
                "innovationTokenBudget": "1 Token (Requires explicit team sign-off)"
            },
            "recommendation": "PROCEED WITH SAFEGUARDS"
        }

    @staticmethod
    async def generate_architecture_decision_record(
        title: str,
        context_problem: str,
        options_considered: List[str],
        chosen_solution: str,
        tech_stack: str = "FastAPI + React + PostgreSQL"
    ) -> Dict[str, Any]:
        """
        Generates a standard ADR (Architecture Decision Record) in markdown and JSON format.
        """
        adr_md = f"""# ADR: {title}

## Status: Proposed / Validated
**Date:** {datetime_today()}
**Stack Context:** {tech_stack}

## Context & Problem Statement
{context_problem}

## Considered Options
{chr(10).join(f'- {opt}' for opt in options_considered)}

## Decision Outcome
**Chosen Option:** {chosen_solution}

### Justification & Boring Tech Alignment
- Aligns with team bandwidth and operational simplicity.
- Treats architecture as a reversible experiment.

## Consequences & Mitigations
- **Positive:** Reduces latency, accelerates developer shipping velocity.
- **Negative / Risks:** Adds a new dependency; mitigated by integration tests and automated telemetry.
"""
        return {
            "title": title,
            "status": "Proposed",
            "chosenOption": chosen_solution,
            "adrMarkdown": adr_md
        }


def datetime_today() -> str:
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d")
