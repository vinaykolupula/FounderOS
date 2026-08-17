# FounderOS Architecture — Technical Specification & System Design

## Purpose of this Document

This is the authoritative technical specification for **FounderOS**, the open-source founder command center. It documents the full-stack system architecture, data models, security vault primitives, multi-agent AI execution engine, and current implementation status.

**Status Key**
- **Implemented** — Fully implemented, tested, and runnable in this repository.
- **Prototype / Simulated** — Functional end-to-end interface backed by representative API fixtures or mock provider connectors.
- **Planned** — Roadmap items scheduled for future iterations.

---

## 1. Product Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│              FOUNDER EXPERIENCE LAYER (React 18 + TypeScript + Vite)            │
│  • Web Command Center   • CEO Morning Briefing Modal   • 6-Agent Debate Matrix  │
│  • Task Delegation UI   • Security Posture Controls    • Global Toast Notices   │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │  HTTP REST / WebSockets (Push Events)
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     BACKEND API LAYER (FastAPI + Pydantic v2)                   │
│  • /api/workspace       • /api/briefing                • /api/debate            │
│  • /api/tasks           • /api/settings (Vault)        • /ws/{workspace_id}     │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         FOUNDER INTELLIGENCE & AI CORE                          │
│  • Universal LLM Connector Registry (Hermes / OpenClaw polymorphic transport)   │
│  • Dynamic Live Model Auto-Discovery (/v1/models query engine)                  │
│  • 6-Persona C-Suite Debate Matrix (CRO, Skeptic, VP CS, CFO, CTO, COO, CEO)    │
│  • Executive Morning Briefing Synthesizer                                       │
│  • Action Safety Policy AST/Regex Engine                                        │
│  • Autonomous Execution Worker & Goal Completion Audit                          │
│  • Signal Ingestion & Vector RAG Pipeline                                       │
└───────────────────┬─────────────────────────────────────────┬───────────────────┘
                    │                                         │
                    ▼                                         ▼
┌───────────────────────────────────────┐ ┌───────────────────────────────────────┐
│     SECURITY & DATA PERSISTENCE       │ │    2026 FRONTIER AI CONNECTORS (12)   │
│ • SQLModel DB (SQLite / PostgreSQL)   │ │ • Claude Opus 5 / Fable 5 / Sonnet 5  │
│ • AES-256-GCM Credential Vault        │ │ • GPT-5.6 Sol (max) & Luna / o3-mini  │
│ • Cognitive Depth Tiers (Max / X-High)│ │ • Grok 4.6 (high) & Grok 4.5          │
│ • Immutable Audit Log Ledger          │ │ • Kimi K3 (max 2.8T) & K2.7 Code      │
│ • Scoped Fact Memory (MEMORY.md)      │ │ • Gemini 3.7 Flash & 3.1 Pro (high)   │
│ • Custom Base URL & Token Overrides   │ │ • DeepSeek V4 Pro 0813 (max) & R1     │
│                                       │ │ • GLM-5.2 (max), Nemotron 3, Muse 1.2 │
└───────────────────────────────────────┘ └───────────────────────────────────────┘
```

---

## 2. Core Backend Modules & Services

### 2.1 Universal LLM Connector & Dynamic Provider Registry (`server/app/services/llm_connectors.py` & `llm.py`)
- **Hermes / OpenClaw Architecture**: Decouples agent orchestration from vendor implementations via polymorphic connector adapters (`OpenAICompatibleConnector`, `AnthropicConnector`, `GeminiConnector`, `OllamaConnector`).
- **2026 Intelligence Leaderboard Integration**: Direct support for Claude Opus/Fable 5 (max), GPT-5.6 Sol/Luna (max), Grok 4.6 (high), Kimi K3 (max), Gemini 3.7 Flash (high), DeepSeek V4 Pro (max), GLM-5.2 (max), Nemotron 3 Ultra, and Muse Spark 1.2 (xhigh).
- **Cognitive Depth & Reasoning Effort Controls**: Injects multi-level thinking budgets (`max`, `xhigh`, `high`, `medium`, `off`) dynamically across Anthropic thinking tokens, OpenAI reasoning effort, Gemini thinkingConfig, and DeepSeek reasoner.
- **Automatic Fallback Resiliency**: Multi-tier failover routing (e.g. `Claude Fable 5 with fallback` or automatic fallback to local heuristic engine) preventing execution interruptions.
- **Live Auto-Discovery (`POST /api/settings/models/discover`)**: Dynamically queries the provider's `/v1/models` and `/models` endpoints in real time, auto-populating active models directly from the founder's account without code stagnation.
- **Custom Base URL & Endpoint Flexibility**: Supports user-defined custom base URLs (e.g. self-hosted vLLM, LM Studio, Azure OpenAI, local inference).
- **Peak 6-Agent C-Suite Harness**: Concurrently queries CRO, Skeptic (CPO), VP CS, CFO, CTO, and COO personas with role-specific mental models.
- **CEO Orchestrator**: Synthesizes board debate into a single consensus, identifying the primary tradeoff and a 2-Week Minimum Viable Experiment (MVE).
- **Local Fallback Heuristics**: Generates rich, framework-grounded strategic advice completely offline when no API key is provided.

### 2.2 Action Safety Policy & Security Postures (`server/app/policy/action_policy.py`)
- **Tri-Modal Security Postures**:
  - `Strict`: 100% human-in-the-loop sign-off on every drafted action.
  - `Auto` (Default): Adversarial prompt injection screening on inbound signals with auto-staging of safe drafts.
  - `Dangerous`: Autonomous tool execution mode.
- **Safety Policy Filter**: Intercepts destructive SQL (`DROP TABLE`), recursive file deletions (`rm -rf`), remote force pushes (`git push -f`), pipe-to-shell (`curl | sh`), and raw API key exposure.

### 2.3 Executive Morning Briefing Synthesizer (`server/app/services/briefing.py`)
- Ingests overnight signals from Gmail, Stripe, Linear, and Slack.
- Groups changes by business impact rather than isolated tool silos.
- Checks One Metric That Matters (OMTM) status and recommends the single highest-leverage founder priority today.

### 2.4 Scoped Notebook Memory (`server/app/services/notebook.py`)
- Line-oriented Markdown bullet memory format.
- Computes SHA-256 revision hashes (`compute_revision_token`) for optimistic concurrency control.
- Enforces a 300-fact sliding window cap with provenance tags.

### 2.5 Founder Voice Profiling Engine (`server/app/services/voice.py`)
- Synthesizes authentic writing rules (sentence rhythm, hard constraints, and forbidden corporate jargon anti-patterns) to format autonomous draft communications.

### 2.6 C-Suite Daily Executive Operating Services (`server/app/services/` & `server/app/routers/executive_tools.py`)
- **👑 Investor Update Synthesizer (`investor_update.py`)**: Ingests monthly growth milestones, MRR traction, and constraints to generate standard YC-style letters with 1-click staging to `ActionItem`.
- **⚡ Andy Grove LNO Prioritizer (`lno_prioritizer.py`)**: Classifies task streams into 10x Leverage (deep work), 1x Neutral, and <0.1x Overhead (auto-delegated to AI workers).
- **💰 Default Alive Runway Lab (`runway_lab.py`)**: Models cash runway, burn delta, and minimum MoM revenue growth rate required for Paul Graham Default Alive sustainability.
- **💻 Technical Pre-Mortem & ADR Lab (`technical_rfc.py`)**: Runs Gary Klein prospective failure simulations and generates Dan McKinley Architecture Decision Records (ADRs).
- **📈 MEDDPICC Deal Health Radar (`deal_radar.py`)**: Evaluates enterprise deals across 8 qualification vectors to highlight stalling risks and synthesize objection talk tracks.
- **🎯 Superhuman PMF Engine (`pmf_engine.py`)**: Calculates PMF scores against Rahul Vohra's 40% "Very Disappointed" threshold and identifies High-Expectation Customer (HXC) personas.

---

## 3. Database Schema (`server/app/models.py`)

- **`Workspace`**: Root tenant container.
- **`CompanyProfile`**: Stage, team size, business model, burn rate, runway, primary constraint, competitive moat, and tech stack.
- **`FounderProfile`**: Superpowers, primary gaps, energy states, and communication style.
- **`Task`**: Prioritized tasks (`P0_CRITICAL` through `P3_LOW`) with delegation status (`PENDING`, `DELEGATED`, `COMPLETED`, `FAILED`).
- **`ActionItem`**: Approval-gated draft outputs awaiting founder sign-off (`Ready` / `Draft`).
- **`Evidence`**: Ingested signal items with vector embeddings and provenance links.
- **`DecisionRecord`**: Institutional memory capturing strategic decisions, tradeoffs, and review dates.
- **`AuditLog`**: Immutable event history tracking all agent and human actions.
- **`AIProviderSetting`**: AES-256 encrypted provider credentials and active model selection.
- **`Connector`**: Integration configurations for Gmail, Slack, Linear, HubSpot, and Stripe.

---

## 4. Verification & Testing

To run the full stack locally:
```bash
# Frontend
npm run dev

# Backend
cd server
uvicorn app.main:app --reload --port 8000
```
