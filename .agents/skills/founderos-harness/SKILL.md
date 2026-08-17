---
name: founderos-harness
description: Guidelines and workflows for engineering, testing, and modifying FounderOS AI Agent Harnesses, executive board personas, and domain playbooks.
---

# FounderOS Agent Harness Development Skill

Use this skill when extending, debugging, or testing AI agent harnesses, board member personas, or background task execution playbooks in FounderOS.

# FounderOS Agent Harness Development Skill

Use this skill when extending, debugging, or testing AI agent harnesses, executive board personas, or background task execution playbooks in FounderOS.

## 🏛️ C-Suite Harness Architecture & Executive Services

The FounderOS AI Agent Harness operates as a unified executive proxy grounded in real-world startup frameworks:

1. **👑 CEO / Solo Founder Harness**:
   - **Frameworks**: One Metric That Matters (OMTM), Andy Grove's LNO Task Matrix (10x Leverage vs <0.1x Overhead).
   - **Service**: `InvestorUpdateService` (`server/app/services/investor_update.py`) & `LNOClassificationService` (`server/app/services/lno_prioritizer.py`).
   - **Mandate**: Protect 10x deep-work focus time; autonomously absorb and draft <0.1x overhead tasks into the approval queue.

2. **💰 CFO / Capital & Strategy Harness**:
   - **Frameworks**: Paul Graham's Default Alive vs Default Dead, Burn Multiple (< 1.5x), Zero-Date Runway Floor.
   - **Service**: `RunwayScenarioService` (`server/app/services/runway_lab.py`).
   - **Mandate**: Continuous runway surveillance; models required MoM growth rates ($g$) to achieve cash-flow profitability.

3. **💻 CTO / Technical Architect Harness**:
   - **Frameworks**: Dan McKinley's Boring Technology Rule (0-1 Innovation Tokens), Amazon's Two-Way Door Decisions, Gary Klein's Pre-Mortem.
   - **Service**: `TechnicalRfcService` (`server/app/services/technical_rfc.py`).
   - **Mandate**: Simulates catastrophic failure modes 6 months into the future before major migrations; enforces reversible rollback runbooks.

4. **📈 CRO / Revenue & Growth Harness**:
   - **Frameworks**: Reforge Growth Loops, MEDDPICC Enterprise Qualification, CAC Payback (< 12 mo).
   - **Service**: `DealInspectionService` (`server/app/services/deal_radar.py`).
   - **Mandate**: Audits deal health across 8 enterprise dimensions to eliminate stalling risks (missing Economic Buyer, unmapped Paper Process).

5. **🎯 VP CS / Customer Success Harness**:
   - **Frameworks**: Rahul Vohra's Superhuman PMF Engine (40% 'Very Disappointed' benchmark), Time-To-First-Value (TTFV < 5 min), Net Revenue Retention (NRR > 110%).
   - **Service**: `PMFEngineService` (`server/app/services/pmf_engine.py`).
   - **Mandate**: Identifies the High-Expectation Customer (HXC) persona; isolates core love vectors to guide the product roadmap.

6. **⚙️ COO / Operational Rigor Harness**:
   - **Frameworks**: Keith Rabois's Barrels & Ammunition, Andy Grove's High Output Management, Weekly Cadence.
   - **Mandate**: Ensures projects have dedicated autonomous owners without cross-functional coordination drag.

---

## 🛡️ Core Directives & Guardrails

1. **Context & Memory Ingestion**:
   - All worker prompts in `server/app/workers/execution.py` and `server/app/services/briefing.py` must dynamically inject:
     - Founder DNA (superpower, primary gap, comms voice, energy state).
     - Company Architecture (stage, objective, constraint, burn rate, tech stack, GTM motion).
     - Scoped Institutional Memory (`Decision` history and `Evidence` signals).
     - Andy Grove LNO Classification tags.

2. **Approval-Gated Action Queue**:
   - Autonomous background tasks must NEVER execute destructive or external actions directly.
   - All deliverables must be staged as draft `ActionItem` records (`status: 'Ready'` or `'Draft'`) for explicit founder sign-off.

3. **Strict JSON Output Schemas**:
   - All completion prompts in `server/app/services/llm.py`, `execution.py`, and `briefing.py` must enforce strict JSON responses without markdown backticks.

4. **Offline Local Heuristic Fallbacks**:
   - Every agent harness persona and executive tool must contain a robust offline fallback that computes deterministic scores and structured deliverables using live database context when external LLM APIs are unreachable.

5. **Vault Encryption Security**:
   - Never write plain text API keys or OAuth tokens to database columns. Always use `encrypt_token()` and `decrypt_token()` from `server/app/vault.py` (AES-256-GCM authenticated encryption).

