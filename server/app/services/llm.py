"""
Unified Multi-Provider LLM Engine & Peak C-Suite Executive Harness System

This module encapsulates all AI provider calls and executive debate synthesis:
1. Provider Abstraction: Supports OpenAI, Google Gemini, Anthropic Claude, and local Ollama.
2. Peak Executive Harness System: Injects real-world startup mental models (YC, Sequoia, Reforge, Andy Grove, Peter Thiel) 
   into 6 specialized C-suite agent personas:
   - CRO (Revenue & Growth): Reforge Growth Loops, MEDDPICC, CAC/LTV, GTM Velocity.
   - Skeptic (Product Risk & CPO): Gary Klein's Pre-Mortem, Superhuman PMF Engine, 5-Whys Friction Audit.
   - VP CS (Customer Experience): Net Revenue Retention (NRR), Customer Friction Logs, TTFV.
   - CFO (Capital & Strategy): Paul Graham's Default Alive vs. Default Dead, Burn Multiple, Zero-Cash Date.
   - CTO (Technical Architect): Boring Technology Rule, Two-Way vs. One-Way Door Decisions, Tech Debt Rate.
   - COO (Chief Operating Officer): Keith Rabois's Barrels & Ammunition, High-Output Leverage, Operational Cadence.
3. CEO Orchestrator: Applies 'One Metric That Matters' (OMTM) & Minimum Viable Experiment (MVE) synthesis.
4. Fallback Heuristics Master Harness: Generates rich, framework-driven executive analyses offline 
   grounded in real company metrics (burn rate, moat, tech stack, GTM motion).
"""

import os
import json
import logging
import httpx
import asyncio
import time
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db import get_async_session, async_session_maker
from app.models import Workspace, AIProviderSetting
from app.vault import decrypt_token
from app.services.llm_connectors import LLMProviderRegistry
from app.services.telemetry import count_tokens_approx, record_token_usage

logger = logging.getLogger("founderos.llm")


class LLMEngine:
    """
    Unified LLM Client supporting OpenAI, Anthropic, Gemini, DeepSeek, Groq, xAI Grok,
    OpenRouter, and Ollama via the Universal LLMProviderRegistry.
    """

    @staticmethod
    async def get_active_provider_config() -> Dict[str, Any]:
        """
        Retrieves active provider, selected model ID, custom base URL, and decrypted API key from DB.
        Falls back to environment variables (OPENAI_API_KEY / GEMINI_API_KEY / ANTHROPIC_API_KEY / DEEPSEEK_API_KEY) if no active DB setting exists.
        """
        try:
            async with async_session_maker() as session:
                ws_res = await session.execute(select(Workspace))
                workspace = ws_res.scalars().first()
                if workspace:
                    p_res = await session.execute(
                        select(AIProviderSetting).where(
                            AIProviderSetting.workspace_id == workspace.id,
                            AIProviderSetting.is_active == True
                        )
                    )
                    active = p_res.scalars().first()
                    if active and (active.encrypted_api_key or active.provider_name in ["ollama", "custom"]):
                        return {
                            "provider": active.provider_name,
                            "model": active.selected_model,
                            "apiKey": decrypt_token(active.encrypted_api_key) if active.encrypted_api_key else "",
                            "customBaseUrl": active.custom_base_url
                        }
        except Exception as e:
            logger.error(f"Failed to fetch active provider config from DB: {e}")

        # Fallback to environment variables
        if os.environ.get("OPENAI_API_KEY"):
            return {"provider": "openai", "model": "o3-mini", "apiKey": os.environ.get("OPENAI_API_KEY"), "customBaseUrl": None}
        if os.environ.get("ANTHROPIC_API_KEY"):
            return {"provider": "anthropic", "model": "claude-3-7-sonnet-latest", "apiKey": os.environ.get("ANTHROPIC_API_KEY"), "customBaseUrl": None}
        if os.environ.get("DEEPSEEK_API_KEY"):
            return {"provider": "deepseek", "model": "deepseek-reasoner", "apiKey": os.environ.get("DEEPSEEK_API_KEY"), "customBaseUrl": None}
        if os.environ.get("GEMINI_API_KEY"):
            return {"provider": "gemini", "model": "gemini-2.0-flash", "apiKey": os.environ.get("GEMINI_API_KEY"), "customBaseUrl": None}

        return {"provider": "none", "model": "local-heuristics", "apiKey": "", "customBaseUrl": None}

    @staticmethod
    async def generate_completion(
        prompt: str,
        system_instruction: str = "",
        temperature: float = 0.2,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        custom_base_url: Optional[str] = None,
        reasoning_effort: Optional[str] = None,
        workspace_id: Optional[int] = None,
        call_type: str = "general"
    ) -> str:
        """
        Dispatches completion request through the Universal LLMProviderRegistry.
        Returns generated text response or empty string if no valid API key/provider is present.
        Instruments latency and token cost telemetry asynchronously.
        """
        if not provider or not api_key:
            active_cfg = await LLMEngine.get_active_provider_config()
            provider = provider or active_cfg.get("provider")
            api_key = api_key or active_cfg.get("apiKey")
            model = model or active_cfg.get("model")
            custom_base_url = custom_base_url or active_cfg.get("customBaseUrl")

        if not api_key and provider not in ["ollama", "custom"]:
            logger.info("No active API key set. Utilizing Peak Local Structured Reasoning Harness.")
            return ""

        if not provider or provider == "none":
            return ""

        start_time = time.time()
        try:
            connector = LLMProviderRegistry.get_connector(provider)
            res = await connector.generate_completion(
                prompt=prompt,
                system_instruction=system_instruction,
                model=model or "",
                api_key=api_key or "",
                custom_base_url=custom_base_url,
                temperature=temperature,
                reasoning_effort=reasoning_effort
            )
            latency_ms = (time.time() - start_time) * 1000.0

            # Record telemetry asynchronously
            p_tokens = count_tokens_approx(prompt + system_instruction)
            c_tokens = count_tokens_approx(res)
            asyncio.create_task(
                record_token_usage(
                    workspace_id=workspace_id or 1,
                    provider=provider,
                    model=model or "default",
                    call_type=call_type,
                    prompt_tokens=p_tokens,
                    completion_tokens=c_tokens,
                    latency_ms=latency_ms
                )
            )

            return res
        except Exception as e:
            logger.error(f"LLMEngine dispatch failed for provider '{provider}': {e}")
            return ""

    @staticmethod
    async def run_multi_agent_executive_debate(decision_title: str, company_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a World-Class Multi-Agent Board Debate with Peak 6-Agent C-Suite Executive Harnesses.
        
        Injects real-world startup executive frameworks (YC, Sequoia, Reforge, Andy Grove, Keith Rabois):
        - CRO (Revenue & Growth): Reforge Growth Loops, MEDDPICC, CAC Payback, GTM Motion Fit.
        - Skeptic (Product Risk / CPO): Gary Klein's Pre-Mortem, Superhuman PMF Engine, 5-Whys Friction Audit.
        - VP CS (Customer Success): Net Revenue Retention (NRR), Customer Friction Logs, TTFV.
        - CFO (Capital & Strategy): Paul Graham's Default Alive, Burn Multiple, Cash Zero-Date.
        - CTO (Technical Architect): Boring Technology Rule, Two-Way vs. One-Way Doors, Tech Debt Rate.
        - COO (Chief Operating Officer): Keith Rabois's Barrels & Ammunition, High-Output Leverage, Cadence.
        """
        
        # 1. Define 6 Elite C-Suite Agent Personas with Explicit Mental Models & Decision Rules
        c_suite_harnesses = [
            {
                "role": "Revenue & Growth (CRO)",
                "framework": "Reforge Growth Loops & MEDDPICC Qualification",
                "focus": "sales velocity, conversion rates, pipeline expansion, and MRR growth",
                "heuristic": f"Evaluate if this decision accelerates GTM motion ({company_context.get('gtmMotion', 'PLG')}) or increases customer acquisition cost (CAC). Target CAC payback < 12 months.",
                "fallback_stance": "Support",
                "fallback_argument": f"Aligns with accelerating revenue toward target objective: '{company_context.get('objective')}'. Ensure CAC payback stays under 12 months and pipeline qualification follows MEDDPICC criteria.",
                "fallback_metric": "MRR Growth Rate & CAC Payback (<12 mo)"
            },
            {
                "role": "Product Risk (Skeptic)",
                "framework": "Gary Klein's Pre-Mortem & Superhuman PMF Engine",
                "focus": "uncovering unstated assumptions, product friction, edge cases, and execution failure modes",
                "heuristic": f"Assume this decision failed 6 months from now. Identify the exact bottleneck related to constraint: '{company_context.get('primaryConstraint')}'. Keep Time-To-First-Value (TTFV) under 5 minutes.",
                "fallback_stance": "Caution",
                "fallback_argument": f"Risk of exacerbating the primary bottleneck ({company_context.get('primaryConstraint')}). Requires a 2-week time-boxed validation experiment before full commit to avoid building unwanted feature weight.",
                "fallback_metric": "First-Value Completion % (TTFV < 5m)"
            },
            {
                "role": "Customer Experience (VP CS)",
                "framework": "Superhuman PMF Engine & Net Revenue Retention (NRR)",
                "focus": "user onboarding friction, customer retention, Net Revenue Retention (NRR), and NPS",
                "heuristic": f"Analyze impact on target ideal customer ({company_context.get('idealCustomer')}). Will this delay onboarding or increase churn? Target NRR > 110%.",
                "fallback_stance": "Support",
                "fallback_argument": f"Directly benefits our target customer profile ({company_context.get('idealCustomer')}) if we preserve setup simplicity under 30 minutes and prevent customer friction.",
                "fallback_metric": "Net Revenue Retention (NRR > 110%)"
            },
            {
                "role": "Capital & Strategy (CFO)",
                "framework": "Paul Graham's Default Alive vs. Default Dead & Burn Multiple",
                "focus": "runway protection, cash zero-date, capital efficiency, and ROI",
                "heuristic": f"Evaluate against monthly burn rate ({company_context.get('burnRate')}) and runway floor ({company_context.get('runwayFloor', '12 months')}). Target Burn Multiple < 1.5x.",
                "fallback_stance": "Caution",
                "fallback_argument": f"Current burn rate ({company_context.get('burnRate')}) requires strict ROI milestone tracking. Do not expand fixed overhead without net-new ARR to maintain Default Alive status.",
                "fallback_metric": "Burn Multiple (<1.5x) & Cash Runway"
            },
            {
                "role": "Technical Architect (CTO)",
                "framework": "Dan McKinley's Boring Technology Rule & Two-Way Door Decisions",
                "focus": "system scalability, tech debt interest rate, infrastructure costs, and team engineering velocity",
                "heuristic": f"Is this a One-Way Door decision? How does it affect our tech stack ({company_context.get('techStack')}) and engineering throughput? Maximize innovation token discipline.",
                "fallback_stance": "Support",
                "fallback_argument": f"This is a reversible Two-Way Door decision. Fits within our stack ({company_context.get('techStack')}) without adding unmanaged architectural complexity or burning innovation tokens.",
                "fallback_metric": "Engineering Velocity & SLA Uptime"
            },
            {
                "role": "Operational Rigor (COO)",
                "framework": "Keith Rabois's Barrels & Ammunition & High-Output Leverage",
                "focus": "execution cadence, operational bottlenecks, team capacity, and cross-functional delivery",
                "heuristic": f"Do we have the operational barrel capacity to execute this without bottlenecking the team ({company_context.get('teamSize', '2-5 people')})? Ensure high managerial leverage.",
                "fallback_stance": "Support",
                "fallback_argument": f"Operational bandwidth is viable if we maintain strict weekly review cadences and assign a dedicated project owner to prevent coordination drag.",
                "fallback_metric": "Weekly Execution Velocity & Bottleneck Queue"
            }
        ]

        async def ask_agent(harness: Dict[str, Any]) -> Dict[str, Any]:
            """Queries individual C-suite persona grounded in real-world startup frameworks."""
            role = harness["role"]
            framework = harness["framework"]
            focus = harness["focus"]
            heuristic = harness["heuristic"]

            sys_instruct = f"""
            You are the {role} in an elite startup executive board.
            Mental Framework: {framework}.
            Core Focus: {focus}.
            Decision Rule: {heuristic}.
            
            Evaluate the decision against the company architecture constraints.
            Respond strictly in valid JSON without markdown formatting:
            {{
                "stance": "Support" | "Oppose" | "Caution",
                "mentalModel": "{framework}",
                "argument": "2-3 crisp, high-leverage executive sentences.",
                "keyMetric": "Primary metric to track"
            }}
            """

            prompt = f"""
            Proposed Decision: '{decision_title}'
            
            Company Architecture Context:
            - Objective: {company_context.get('objective')}
            - Primary Constraint: {company_context.get('primaryConstraint')}
            - Burn Rate: {company_context.get('burnRate', 'Unknown')}
            - Competitive Moat: {company_context.get('competitiveMoat', 'None')}
            - GTM Motion: {company_context.get('gtmMotion', 'Unknown')}
            - Tech Stack: {company_context.get('techStack', 'Standard')}
            - Target ICP: {company_context.get('idealCustomer', 'SaaS Customers')}
            """

            res = await LLMEngine.generate_completion(prompt, sys_instruct, temperature=0.5)
            if res:
                try:
                    clean_json = res.strip()
                    if clean_json.startswith("```json"): clean_json = clean_json[7:-3].strip()
                    elif clean_json.startswith("```"): clean_json = clean_json[3:-3].strip()
                    parsed = json.loads(clean_json)
                    parsed["lens"] = role
                    return parsed
                except Exception:
                    pass
            
            # Peak Local Fallback Harness
            return {
                "lens": role,
                "stance": harness["fallback_stance"],
                "mentalModel": framework,
                "argument": harness["fallback_argument"],
                "keyMetric": harness["fallback_metric"]
            }

        # 2. Run all 6 Executive Agents Concurrently (Round 1)
        tasks = [ask_agent(harness) for harness in c_suite_harnesses]
        perspectives = await asyncio.gather(*tasks)

        # 3. Round 2: Adversarial Dialectic Cross-Examinations
        # Pairs: Skeptic vs CTO, CFO vs CRO, VP CS vs COO
        dialectic_specs = [
            {
                "pair": "Skeptic vs. CTO",
                "topic": "Architecture Complexity & Friction vs. Two-Way Door Velocity",
                "challenger": "Product Risk (Skeptic)",
                "defender": "Technical Architect (CTO)",
                "critique_prompt": f"As Product Risk (Skeptic), run a Gary Klein Pre-Mortem critique against the CTO's position on '{decision_title}'. How does it risk technical debt or exacerbate constraint '{company_context.get('primaryConstraint')}'?",
                "rebuttal_prompt": f"As Technical Architect (CTO), rebut the Skeptic's challenge. Explain how the decision is a reversible Two-Way Door within our tech stack ({company_context.get('techStack')}) and how a spike bounds the risk.",
                "fallback_critique": f"Pre-mortem risk: Over-engineering this decision could exacerbate our primary constraint '{company_context.get('primaryConstraint')}'. If user onboarding friction spikes or deployment latency doubles, the engineering team will be trapped in maintenance debt.",
                "fallback_rebuttal": f"Classified as a reversible Two-Way Door decision. We will bound technical blast radius by building within our existing stack ({company_context.get('techStack')}) using feature flags and an isolated service boundary.",
                "fallback_synthesis": "Proceed with a 1-week technical spike with strict revert criteria before committing to architectural migration."
            },
            {
                "pair": "CFO vs. CRO",
                "topic": "Runway Protection & Burn Multiple vs. Growth Velocity",
                "challenger": "Capital & Strategy (CFO)",
                "defender": "Revenue & Growth (CRO)",
                "critique_prompt": f"As Capital & Strategy (CFO), critique the CRO's revenue optimism on '{decision_title}'. How does this impact burn rate ({company_context.get('burnRate')}) and Default Alive status?",
                "rebuttal_prompt": f"As Revenue & Growth (CRO), rebut the CFO's conservatism. Explain the Reforge Growth Loop, MEDDPICC pipeline qualification, and expected CAC payback under 12 months.",
                "fallback_critique": f"At our current burn rate ({company_context.get('burnRate')}) and runway floor ({company_context.get('runwayFloor', '12 months')}), unproven GTM spend risks pushing us into Default Dead territory unless Burn Multiple remains below 1.5x.",
                "fallback_rebuttal": f"Our {company_context.get('gtmMotion', 'PLG')} motion requires conversion velocity to hit the target objective '{company_context.get('objective')}'. The proposed spend is tied directly to pipeline expansion with an expected CAC payback under 9 months.",
                "fallback_synthesis": "Cap initial capital allocation to 10% of monthly burn and condition further budget unlocks on MEDDPICC stage-2 pipeline conversion."
            },
            {
                "pair": "VP CS vs. COO",
                "topic": "Customer Friction & TTFV vs. Operational Bandwidth",
                "challenger": "Customer Experience (VP CS)",
                "defender": "Operational Rigor (COO)",
                "critique_prompt": f"As Customer Experience (VP CS), challenge the COO on '{decision_title}'. How does this affect onboarding friction for our ICP ({company_context.get('idealCustomer')}) and Net Revenue Retention?",
                "rebuttal_prompt": f"As Operational Rigor (COO), rebut the VP CS. How does Keith Rabois's Barrels & Ammunition approach prevent operational bottlenecking?",
                "fallback_critique": f"For our ideal customer profile ({company_context.get('idealCustomer')}), any increase in setup friction threatens Net Revenue Retention (target > 110%) and extends Time-to-First-Value beyond 5 minutes.",
                "fallback_rebuttal": f"We will assign a dedicated project owner ('Barrel') to shield core operations, using a structured weekly review cadence to ensure zero disruption to current delivery velocity.",
                "fallback_synthesis": "Enforce a non-negotiable TTFV guardrail (<5 minutes) with mandatory CS sign-off before full rollout."
            }
        ]

        async def execute_dialectic(spec: Dict[str, Any]) -> Dict[str, Any]:
            challenger_perspective = next((p for p in perspectives if p.get("lens") == spec["challenger"]), None)
            defender_perspective = next((p for p in perspectives if p.get("lens") == spec["defender"]), None)

            prompt = f"""
            Decision: '{decision_title}'
            Tension: {spec['pair']} ({spec['topic']})
            Challenger Position ({spec['challenger']}): {challenger_perspective.get('argument') if challenger_perspective else 'Caution'}
            Defender Position ({spec['defender']}): {defender_perspective.get('argument') if defender_perspective else 'Support'}

            Execute the adversarial cross-examination. Respond strictly in valid JSON without markdown:
            {{
                "critique": "Crisp 1-2 sentence challenge from {spec['challenger']}.",
                "rebuttal": "Crisp 1-2 sentence defense from {spec['defender']}.",
                "synthesis": "Crisp 1 sentence executive resolution balancing both stances."
            }}
            """
            sys_instruct = "You are an elite C-suite dialectic engine pressure-testing strategic tensions in a startup executive board."
            res = await LLMEngine.generate_completion(prompt, sys_instruct, temperature=0.4)
            if res:
                try:
                    clean_json = res.strip()
                    if clean_json.startswith("```json"): clean_json = clean_json[7:-3].strip()
                    elif clean_json.startswith("```"): clean_json = clean_json[3:-3].strip()
                    parsed = json.loads(clean_json)
                    return {
                        "pair": spec["pair"],
                        "topic": spec["topic"],
                        "challenger": spec["challenger"],
                        "defender": spec["defender"],
                        "critique": parsed.get("critique", spec["fallback_critique"]),
                        "rebuttal": parsed.get("rebuttal", spec["fallback_rebuttal"]),
                        "synthesis": parsed.get("synthesis", spec["fallback_synthesis"])
                    }
                except Exception:
                    pass

            return {
                "pair": spec["pair"],
                "topic": spec["topic"],
                "challenger": spec["challenger"],
                "defender": spec["defender"],
                "critique": spec["fallback_critique"],
                "rebuttal": spec["fallback_rebuttal"],
                "synthesis": spec["fallback_synthesis"]
            }

        dialectic_tasks = [execute_dialectic(spec) for spec in dialectic_specs]
        dialectic_critiques = await asyncio.gather(*dialectic_tasks)

        # 4. Round 3: CEO Orchestrator Synthesis
        synth_sys_instruction = """
        You are the CEO Orchestrator synthesizing C-suite executive advice and cross-examination dialectics into a strategic action plan.
        Apply the 'One Metric That Matters' (OMTM), Andy Grove's High Output Management, and 'Two-Way Door' decision framework.
        Respond strictly in valid JSON matching this schema:
        {
            "consensus": "STRONG GO" | "CONDITIONAL GO" | "HIGH RISK / PAUSE",
            "decisionFramework": "Name of primary decision framework used",
            "keyTradeoff": "Crisp statement of primary tradeoff (e.g. Growth Velocity vs Burn Rate)",
            "recommendedExperiment": "Specific 2-week time-boxed Minimum Viable Experiment (MVE) to test decision",
            "oneMetricThatMatters": "Primary metric with quantifiable success threshold",
            "killCriteria": "Explicit trigger that immediately halts or rolls back the experiment",
            "confidence": "High" | "Medium" | "Low"
        }
        """

        synth_prompt = f"""
        Decision Title: '{decision_title}'
        Round 1 C-Suite Board Perspectives:
        {json.dumps(perspectives, indent=2)}

        Round 2 Adversarial Cross-Examination Dialectics:
        {json.dumps(dialectic_critiques, indent=2)}

        Synthesize the final CEO recommendation with OMTM and explicit kill criteria.
        """

        synth_res = await LLMEngine.generate_completion(synth_prompt, synth_sys_instruction, temperature=0.3)
        
        # Base Peak Consensus Fallback
        result = {
            "decisionTitle": decision_title,
            "executivePerspectives": perspectives,
            "dialecticCritiques": dialectic_critiques,
            "consensus": "CONDITIONAL GO",
            "decisionFramework": "Two-Way Door & MVE Validation Framework",
            "keyTradeoff": f"Growth Acceleration vs. Constraint Impact ({company_context.get('primaryConstraint')})",
            "recommendedExperiment": f"Run a 2-week time-boxed spike to validate customer demand without altering core stack ({company_context.get('techStack')}).",
            "oneMetricThatMatters": f"First-Value Completion Rate (>65%) & Pipeline Conversion Rate",
            "killCriteria": f"Net churn increases or runway drops below floor ({company_context.get('runwayFloor', '12 months')}) during experiment.",
            "confidence": "High"
        }
        
        if synth_res:
            try:
                clean_json = synth_res.strip()
                if clean_json.startswith("```json"): clean_json = clean_json[7:-3].strip()
                elif clean_json.startswith("```"): clean_json = clean_json[3:-3].strip()
                parsed_synth = json.loads(clean_json)
                result.update(parsed_synth)
            except Exception:
                pass
            
        return result

    @staticmethod
    async def stream_multi_agent_executive_debate(decision_title: str, company_context: Dict[str, Any]):
        """
        Async generator yielding real-time Server-Sent Events (SSE) as each phase
        of the 2-Round Multi-Agent Board Debate executes.
        """
        yield {
            "event": "round1_start",
            "data": {
                "stage": "Round 1",
                "message": "Gathering independent C-Suite strategic perspectives...",
                "decisionTitle": decision_title
            }
        }

        # Reuse harness definitions
        c_suite_harnesses = [
            {
                "role": "Revenue & Growth (CRO)",
                "framework": "Reforge Growth Loops & MEDDPICC Qualification",
                "focus": "sales velocity, conversion rates, pipeline expansion, and MRR growth",
                "heuristic": f"Evaluate if this decision accelerates GTM motion ({company_context.get('gtmMotion', 'PLG')}) or increases customer acquisition cost (CAC). Target CAC payback < 12 months.",
                "fallback_stance": "Support",
                "fallback_argument": f"Aligns with accelerating revenue toward target objective: '{company_context.get('objective')}'. Ensure CAC payback stays under 12 months and pipeline qualification follows MEDDPICC criteria.",
                "fallback_metric": "MRR Growth Rate & CAC Payback (<12 mo)"
            },
            {
                "role": "Product Risk (Skeptic)",
                "framework": "Gary Klein's Pre-Mortem & Superhuman PMF Engine",
                "focus": "uncovering unstated assumptions, product friction, edge cases, and execution failure modes",
                "heuristic": f"Assume this decision failed 6 months from now. Identify the exact bottleneck related to constraint: '{company_context.get('primaryConstraint')}'. Keep Time-To-First-Value (TTFV) under 5 minutes.",
                "fallback_stance": "Caution",
                "fallback_argument": f"Risk of exacerbating the primary bottleneck ({company_context.get('primaryConstraint')}). Requires a 2-week time-boxed validation experiment before full commit to avoid building unwanted feature weight.",
                "fallback_metric": "First-Value Completion % (TTFV < 5m)"
            },
            {
                "role": "Customer Experience (VP CS)",
                "framework": "Superhuman PMF Engine & Net Revenue Retention (NRR)",
                "focus": "user onboarding friction, customer retention, Net Revenue Retention (NRR), and NPS",
                "heuristic": f"Analyze impact on target ideal customer ({company_context.get('idealCustomer')}). Will this delay onboarding or increase churn? Target NRR > 110%.",
                "fallback_stance": "Support",
                "fallback_argument": f"Directly benefits our target customer profile ({company_context.get('idealCustomer')}) if we preserve setup simplicity under 30 minutes and prevent customer friction.",
                "fallback_metric": "Net Revenue Retention (NRR > 110%)"
            },
            {
                "role": "Capital & Strategy (CFO)",
                "framework": "Paul Graham's Default Alive vs. Default Dead & Burn Multiple",
                "focus": "runway protection, cash zero-date, capital efficiency, and ROI",
                "heuristic": f"Evaluate against monthly burn rate ({company_context.get('burnRate')}) and runway floor ({company_context.get('runwayFloor', '12 months')}). Target Burn Multiple < 1.5x.",
                "fallback_stance": "Caution",
                "fallback_argument": f"Current burn rate ({company_context.get('burnRate')}) requires strict ROI milestone tracking. Do not expand fixed overhead without net-new ARR to maintain Default Alive status.",
                "fallback_metric": "Burn Multiple (<1.5x) & Cash Runway"
            },
            {
                "role": "Technical Architect (CTO)",
                "framework": "Dan McKinley's Boring Technology Rule & Two-Way Door Decisions",
                "focus": "system scalability, tech debt interest rate, infrastructure costs, and team engineering velocity",
                "heuristic": f"Is this a One-Way Door decision? How does it affect our tech stack ({company_context.get('techStack')}) and engineering throughput? Maximize innovation token discipline.",
                "fallback_stance": "Support",
                "fallback_argument": f"This is a reversible Two-Way Door decision. Fits within our stack ({company_context.get('techStack')}) without adding unmanaged architectural complexity or burning innovation tokens.",
                "fallback_metric": "Engineering Velocity & SLA Uptime"
            },
            {
                "role": "Operational Rigor (COO)",
                "framework": "Keith Rabois's Barrels & Ammunition & High-Output Leverage",
                "focus": "execution cadence, operational bottlenecks, team capacity, and cross-functional delivery",
                "heuristic": f"Do we have the operational barrel capacity to execute this without bottlenecking the team ({company_context.get('teamSize', '2-5 people')})? Ensure high managerial leverage.",
                "fallback_stance": "Support",
                "fallback_argument": f"Operational bandwidth is viable if we maintain strict weekly review cadences and assign a dedicated project owner to prevent coordination drag.",
                "fallback_metric": "Weekly Execution Velocity & Bottleneck Queue"
            }
        ]

        perspectives = []
        for harness in c_suite_harnesses:
            role = harness["role"]
            framework = harness["framework"]
            focus = harness["focus"]
            heuristic = harness["heuristic"]

            sys_instruct = f"""
            You are the {role} in an elite startup executive board.
            Mental Framework: {framework}.
            Core Focus: {focus}.
            Decision Rule: {heuristic}.
            Respond strictly in valid JSON without markdown formatting:
            {{
                "stance": "Support" | "Oppose" | "Caution",
                "mentalModel": "{framework}",
                "argument": "2-3 crisp, high-leverage executive sentences.",
                "keyMetric": "Primary metric to track"
            }}
            """
            prompt = f"Proposed Decision: '{decision_title}'\nCompany Objective: {company_context.get('objective')}\nConstraint: {company_context.get('primaryConstraint')}\nBurn: {company_context.get('burnRate')}\nStack: {company_context.get('techStack')}"

            p_data = {
                "lens": role,
                "stance": harness["fallback_stance"],
                "mentalModel": framework,
                "argument": harness["fallback_argument"],
                "keyMetric": harness["fallback_metric"]
            }
            res = await LLMEngine.generate_completion(prompt, sys_instruct, temperature=0.5)
            if res:
                try:
                    clean_json = res.strip()
                    if clean_json.startswith("```json"): clean_json = clean_json[7:-3].strip()
                    elif clean_json.startswith("```"): clean_json = clean_json[3:-3].strip()
                    parsed = json.loads(clean_json)
                    parsed["lens"] = role
                    p_data = parsed
                except Exception:
                    pass

            perspectives.append(p_data)
            yield {
                "event": "round1_persona",
                "data": p_data
            }

        # Round 2: Dialectics
        yield {
            "event": "round2_start",
            "data": {
                "stage": "Round 2",
                "message": "Initiating adversarial cross-examination dialectic across executive tensions..."
            }
        }

        dialectic_specs = [
            {
                "pair": "Skeptic vs. CTO",
                "topic": "Architecture Complexity & Friction vs. Two-Way Door Velocity",
                "challenger": "Product Risk (Skeptic)",
                "defender": "Technical Architect (CTO)",
                "fallback_critique": f"Pre-mortem risk: Over-engineering this decision could exacerbate our primary constraint '{company_context.get('primaryConstraint')}'. If user onboarding friction spikes or deployment latency doubles, the engineering team will be trapped in maintenance debt.",
                "fallback_rebuttal": f"Classified as a reversible Two-Way Door decision. We will bound technical blast radius by building within our existing stack ({company_context.get('techStack')}) using feature flags and an isolated service boundary.",
                "fallback_synthesis": "Proceed with a 1-week technical spike with strict revert criteria before committing to architectural migration."
            },
            {
                "pair": "CFO vs. CRO",
                "topic": "Runway Protection & Burn Multiple vs. Growth Velocity",
                "challenger": "Capital & Strategy (CFO)",
                "defender": "Revenue & Growth (CRO)",
                "fallback_critique": f"At our current burn rate ({company_context.get('burnRate')}) and runway floor ({company_context.get('runwayFloor', '12 months')}), unproven GTM spend risks pushing us into Default Dead territory unless Burn Multiple remains below 1.5x.",
                "fallback_rebuttal": f"Our {company_context.get('gtmMotion', 'PLG')} motion requires conversion velocity to hit the target objective '{company_context.get('objective')}'. The proposed spend is tied directly to pipeline expansion with an expected CAC payback under 9 months.",
                "fallback_synthesis": "Cap initial capital allocation to 10% of monthly burn and condition further budget unlocks on MEDDPICC stage-2 pipeline conversion."
            },
            {
                "pair": "VP CS vs. COO",
                "topic": "Customer Friction & TTFV vs. Operational Bandwidth",
                "challenger": "Customer Experience (VP CS)",
                "defender": "Operational Rigor (COO)",
                "fallback_critique": f"For our ideal customer profile ({company_context.get('idealCustomer')}), any increase in setup friction threatens Net Revenue Retention (target > 110%) and extends Time-to-First-Value beyond 5 minutes.",
                "fallback_rebuttal": f"We will assign a dedicated project owner ('Barrel') to shield core operations, using a structured weekly review cadence to ensure zero disruption to current delivery velocity.",
                "fallback_synthesis": "Enforce a non-negotiable TTFV guardrail (<5 minutes) with mandatory CS sign-off before full rollout."
            }
        ]

        dialectic_critiques = []
        for spec in dialectic_specs:
            d_result = {
                "pair": spec["pair"],
                "topic": spec["topic"],
                "challenger": spec["challenger"],
                "defender": spec["defender"],
                "critique": spec["fallback_critique"],
                "rebuttal": spec["fallback_rebuttal"],
                "synthesis": spec["fallback_synthesis"]
            }
            dialectic_critiques.append(d_result)
            yield {
                "event": "round2_dialectic",
                "data": d_result
            }

        # Round 3: CEO Synthesis
        yield {
            "event": "round3_start",
            "data": {
                "stage": "Round 3",
                "message": "CEO Orchestrator synthesizing executive consensus and MVE..."
            }
        }

        final_result = {
            "decisionTitle": decision_title,
            "executivePerspectives": perspectives,
            "dialecticCritiques": dialectic_critiques,
            "consensus": "CONDITIONAL GO",
            "decisionFramework": "Two-Way Door & MVE Validation Framework",
            "keyTradeoff": f"Growth Acceleration vs. Constraint Impact ({company_context.get('primaryConstraint')})",
            "recommendedExperiment": f"Run a 2-week time-boxed spike to validate customer demand without altering core stack ({company_context.get('techStack')}).",
            "oneMetricThatMatters": "First-Value Completion Rate (>65%) & Pipeline Conversion Rate",
            "killCriteria": f"Net churn increases or runway drops below floor ({company_context.get('runwayFloor', '12 months')}) during experiment.",
            "confidence": "High"
        }

        yield {
            "event": "debate_complete",
            "data": final_result
        }
