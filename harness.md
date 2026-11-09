# FounderOS Agent Harness Specification & Reference (`harness.md`)

This document records the design, implementation, and reference specification of the **FounderOS Peak 6-Agent C-Suite Harness System**.

The FounderOS Agent Harness is designed around a core principle:
> **"Great agent performance comes from great harness constraints, domain playbooks, security postures, and mental frameworks—not just relying on larger LLM parameter sizes."**

---

## 1. System Architecture of the Agent Harness

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              1. CONTEXT INPUTS                                  │
│ • Company Harness: Stage, Burn Rate, GTM Motion, Competitive Moat, Tech Stack   │
│ • Founder DNA: Superpower, Primary Gap, Energy State, Voice Profile             │
│ • Operational Task & Strategic Decision Payloads                                │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          2. HARNESS PROCESSING LAYER                            │
│ • 6-Domain Playbook Selector (Sales, Tech, Ops, PMF, Finance, Hiring)          │
│ • 2-Round Dialectic Board Debate (Round 1: Stances -> Round 2: Rebuttals)       │
│ • CEO Orchestration Synthesis (OMTM, High-Output Leverage, 2-Week MVE)          │
│ • Tri-Modal Security Posture (Strict, Auto, Dangerous)                          │
│ • Action Safety Policy Engine (AST / Regex Safety Denylist)                     │
│ • Sandboxed Tool Execution Guard (ExecutionSandbox, Env Scrubbing, 5s Timeout)  │
│ • Goal Completion Audit (Evidence Verification & Multi-Round Impasse Check)     │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        3. LLM REASONING & LOCAL FALLBACK                        │
│ • Unified Cloud LLMEngine (OpenAI, Google Gemini, Anthropic Claude, Ollama)     │
│ • Real-Time Server-Sent Events (SSE) Streaming Gateway (/api/debate/stream)     │
│ • Peak Local Fallback Structured Reasoning Engine (100% Offline Heuristics)    │
│ • AI Observability & Cost Accounting Engine (TokenUsageLedger, Pricing Catalog) │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         4. STRUCTURED EXECUTIVE OUTPUTS                         │
│ • CEO Morning Briefing         • 2-Week Minimum Viable Experiment (MVE)         │
│ • Key Executive Tradeoff       • Explicit Pre-Mortem Failure Kill Criteria      │
│ • Approval-Gated Action Draft  • Immutable Audit Log Record                     │
│ • Scoped Notebook Fact Update  • Live Token Burn & Latency Telemetry            │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Implemented Harness Profiles

### A. Company Harness Architecture (`CompanyProfile`)

Grounds all agent reasoning in the company's financial and operational boundaries:

| Harness Parameter | Field | Purpose & Reasoning Impact |
|---|---|---|
| **Stage & Size** | `stage`, `teamSize` | Constrains execution scale (e.g. 2-5 dev limit prevents enterprise over-engineering). |
| **Business Model & GTM** | `businessModel`, `gtmMotion` | Aligns growth suggestions with motion (Product-Led Growth vs. Enterprise Sales). |
| **Burn Rate & Runway** | `burnRate`, `runwayMonths` | Evaluates financial impact on cash zero-date before proposing expenditure. |
| **Primary Constraint** | `primaryConstraint` | Focuses all recommendations on removing the single active company bottleneck. |
| **Competitive Moat** | `competitiveMoat` | Ensures strategic decisions reinforce long-term defensibility. |
| **Tech Stack** | `techStack` | Keeps engineering actions within existing technological boundaries. |

---

### B. Founder DNA Harness (`FounderProfile`)

Adapts agent tone, depth, and domain focus to the founder's personal capabilities:

| Harness Parameter | Field | Purpose & Reasoning Impact |
|---|---|---|
| **Superpower** | `superpower` | Agent steps back and defers to founder expertise in their strongest domain. |
| **Primary Gap** | `primaryGap` | Agent actively steps up as a domain specialist in the founder's weakest area. |
| **Energy State** | `energyState` | If founder energy is low/burned out, agent proposes maximum end-to-end automation. |
| **Communication Style**| `communicationStyle` | Agent mirrors preferred tone and authentic sentence rhythm. |
| **Voice Profile** | `VoiceProfileEngine` | Injects hard rules and forbids corporate jargon anti-patterns in drafts. |
| **Core Values** | `coreValues` | Aligns draft outputs with founder priorities (e.g. "Speed, Customer Obsession"). |

---

## 3. Authentic 2-Round Multi-Agent Board Debate Dialectic

FounderOS implements a multi-agent dialectic debate protocol (`server/app/services/llm.py`):

```
ROUND 1: Independent Stances
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│   CRO    │ │ Skeptic  │ │  VP CS   │ │   CFO    │ │   CTO    │ │   COO    │
│ Reforge  │ │Pre-Mortem│ │Superhuman│ │ Default  │ │  Boring  │ │Barrels & │
│ MEDDPICC │ │ Friction │ │PMF Engine│ │Alive/Burn│ │Technology│ │Ammunition│
└────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
     │            │            │            │            │            │
     ▼            ▼            ▼            ▼            ▼            ▼
ROUND 2: Dialectic Cross-Examination (Organizational Tensions)
┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐
│     Skeptic vs. CTO     │  │       CFO vs. CRO       │  │     VP CS vs. COO       │
│ Pre-Mortem Fragility vs.│  │ Runway & Burn Mult. vs.│  │ TTFV & NRR vs. Barrel   │
│ Two-Way Door Reversibility││ Pipeline Growth Loops   │  │ Execution Bandwidth     │
└────────────┬────────────┘  └────────────┬────────────┘  └────────────┬────────────┘
             │                            │                            │
             └────────────────────────────┼────────────────────────────┘
                                          ▼
ROUND 3: CEO Orchestrator Synthesis
┌────────────────────────────────────────────────────────────────────────────────────┐
│ • Consensus Rating: STRONG GO | CONDITIONAL GO | HIGH RISK / PAUSE                │
│ • One Metric That Matters (OMTM) Traction Impact                                  │
│ • 2-Week Minimum Viable Experiment (MVE)                                          │
│ • Explicit Failure Kill Criteria (Pre-Mortem Trigger)                             │
└────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 The Three Dialectic Tension Pairs (Round 2)
1. **Skeptic vs. CTO (Operational Fragility vs. Engineering Velocity)**:
   - *Skeptic*: Probes Gary Klein pre-mortem failure modes 6 months into the future.
   - *CTO*: Defends reversible two-way doors and Dan McKinley innovation token discipline.
2. **CFO vs. CRO (Capital Preservation vs. Growth Acceleration)**:
   - *CFO*: Guards Paul Graham default alive status and keeps burn multiple under 1.5x.
   - *CRO*: Defends ARR velocity, Reforge compounding growth loops, and MEDDPICC qualification.
3. **VP CS vs. COO (Customer Retention vs. Operational Bandwidth)**:
   - *VP CS*: Evaluates Rahul Vohra Superhuman PMF engine thresholds, TTFV (< 5m), and NRR (> 110%).
   - *COO*: Evaluates Keith Rabois Barrels & Ammunition leadership bandwidth and cross-functional drag.

### 3.2 Real-Time Server-Sent Events (SSE) Streaming Protocol
- **Endpoint**: `GET /api/debate/stream?decisionTitle={title}&decisionDetail={detail}`
- **Response Format**: `text/event-stream` with strict SSE framing:
  - `event: round1_start` -> Initiates independent position formulation.
  - `event: round1_persona` (x6) -> Streams each C-suite executive stance (`cro`, `skeptic`, `vp_cs`, `cfo`, `cto`, `coo`).
  - `event: round2_start` -> Initiates cross-examination dialectic.
  - `event: round2_dialectic` (x3) -> Streams dialectic tension critiques.
  - `event: round3_start` -> Initiates CEO orchestrator synthesis.
  - `event: debate_complete` -> Full structured payload delivered.

### 3.3 Personas & Framework Matrix

| Persona | Framework & Mental Model | Core Evaluation Question | Tracked Metric / Heuristic |
|---|---|---|---|
| **CRO (Revenue & Growth)** | **Reforge Growth Loops & MEDDPICC** | *Does this accelerate ARR velocity or shorten sales cycles without raising CAC?* | CAC Payback (< 12 mo) & Pipeline Velocity |
| **Skeptic (Product Risk / CPO)** | **Gary Klein's Pre-Mortem & Superhuman PMF** | *Assume this decision failed 6 months from now. What unstated assumption broke it?* | Time-to-First-Value (TTFV < 5m) & PMF Score |
| **VP CS (Customer Success)** | **Net Revenue Retention (NRR) & Friction Logs** | *Will this increase onboarding friction or cause churn for our target ICP?* | Net Revenue Retention (NRR > 110%) |
| **CFO (Capital & Strategy)**| **Paul Graham's Default Alive & Burn Multiple**| *Is the startup default alive? How does this shift cash zero-date and burn rate?* | Burn Multiple (< 1.5x) & Cash Runway |
| **CTO (Technical Architect)**| **Dan McKinley's Boring Tech & Two-Way Doors**| *Is this a reversible Two-Way Door? Does it spend unnecessary innovation tokens?* | Engineering Velocity & SLA Uptime |
| **COO (Operational Rigor)** | **Keith Rabois's Barrels/Ammo & Andy Grove LNO**| *Do we have the barrel capacity to execute without creating cross-functional drag?* | Operational Velocity & Bottleneck Queue |
| **CEO (Orchestrator)** | **One Metric That Matters (OMTM) & MVE** | *What is the Minimum Viable Experiment (MVE) to test this safely in 2 weeks?* | CEO Consensus Rating & Kill Criteria |

---

## 4. YC QM-Inspired Security Postures & Sandboxed Execution

FounderOS adopts Y Combinator's tri-modal security model with subprocess isolation:

1. **Tri-Modal Security Postures (`server/app/policy/action_policy.py`)**:
   - **`Strict`**: Every single tool action and draft item pauses for explicit human-in-the-loop sign-off.
   - **`Auto` (Default)**: Inbound signals are screened for adversarial prompt injection directives; safe actions are auto-staged into draft items.
   - **`Dangerous`**: Autonomous execution mode without human confirmation (for sandbox testing).

2. **Action Safety Policy Engine**:
   - Scans actions, payloads, and queries to intercept dangerous operations:
     - **Hard Deny**: Fork bombs (`:(){ :|:& };:`), destructive filesystem formats (`mkfs`), destructive block devices (`dd if=`).
     - **Approval Required**: Recursive file deletion (`rm -rf`), remote force pushes (`git push -f`), destructive table drops (`DROP TABLE`), pipe-to-shell (`curl | sh`), and raw API credential exposure.

3. **Sandboxed Tool Execution Guard (`ExecutionSandbox` - SEC-07)**:
   - **Subprocess Isolation**: Runs tool commands via isolated asynchronous subprocesses (`asyncio.create_subprocess_exec` / `create_subprocess_shell`).
   - **Environment Variable Scrubbing**: Strips all sensitive credentials (`AWS_*`, `VAULT_*`, `FOUNDEROS_*`, `*_SECRET`, `*_KEY`, `*_TOKEN`, `DATABASE_URL`) from the execution environment.
   - **Strict Execution Timeout**: Enforces a 5.0-second execution deadline with automatic process termination (`kill`) upon timeout.
   - **Memory & Output Bounds**: Caps stdout and stderr capture at 64KB (`MAX_OUTPUT_BYTES = 65536`) to protect system memory.

4. **Goal Completion & Impasse Verification Discipline (`server/app/workers/execution.py`)**:
   - Treats completion as unproven until concrete requirements are derived and output artifacts are generated.
   - Requires 3 consecutive rounds of the same roadblock before declaring an autonomous task `FAILED`.

---

## 5. Daily Rhythms & Scoped Notebook Memory

1. **Executive Morning Briefing Synthesizer (`server/app/services/briefing.py`)**:
   - Answers: *"What changed overnight that the founder must know about?"*
   - Groups overnight signals across Gmail, Stripe, Linear, and Slack by business impact.
   - Evaluates One Metric That Matters (OMTM) traction and prescribes the single highest-leverage decision for today.

2. **Scoped Notebook Memory & Fact Indexing (`server/app/services/notebook.py`)**:
   - Human-readable line-oriented bullet memory format.
   - Computes SHA-256 revision hashes for optimistic concurrency locking.
   - Enforces a 300-fact sliding window cap with provenance tags `[logged_by: ...]`.

---

## 6. Local Fallback Heuristics Master Harness

FounderOS functions 100% offline out-of-the-box without requiring paid API keys.

When no LLM API key is present:
1. `LLMEngine` detects missing credentials and activates the **Peak Local Structured Reasoning Harness**.
2. The harness pulls live company context from the database (`CompanyProfile` & `FounderProfile`).
3. It constructs structured, framework-grounded executive debate responses (Round 1, Round 2 Dialectic, Round 3 CEO Synthesis) and draft action items tailored specifically to the company's real metrics (`burnRate`, `gtmMotion`, `techStack`, `competitiveMoat`, `objective`, `primaryConstraint`).

---

## 7. C-Suite Daily Executive Operating Services & Playbooks

FounderOS provides specialized domain playbooks and calculation engines for daily executive operations:

| Executive Role | Service Module | Startup Mental Framework | Key Deliverable |
|---|---|---|---|
| **👑 CEO / Founder** | `InvestorUpdateService` (`server/app/services/investor_update.py`) | Gold-standard YC/Sequoia Monthly Letter | 1-page update letter + 1-click staging to `ActionItem` |
| **⚡ Solo / COO** | `LNOClassificationService` (`server/app/services/lno_prioritizer.py`) | Andy Grove's LNO Task Matrix | 10x Leverage vs <0.1x Overhead segmentation |
| **💰 CFO** | `RunwayScenarioService` (`server/app/services/runway_lab.py`) | Paul Graham's Default Alive & Burn Multiple | What-if hiring/spending simulations & runway deltas |
| **💻 CTO** | `TechnicalRfcService` (`server/app/services/technical_rfc.py`) | Gary Klein Pre-Mortem & Dan McKinley Boring Tech | 6-month prospective failure modes & ADR records |
| **📈 CRO** | `DealInspectionService` (`server/app/services/deal_radar.py`) | 8-Dimension MEDDPICC Enterprise Qualification | Pipeline deal health score (0-100) & objection scripts |
| **🎯 VP CS** | `PMFEngineService` (`server/app/services/pmf_engine.py`) | Rahul Vohra's Superhuman 40% PMF Engine | % 'Very Disappointed' score & High-Expectation Customer segmentation |
