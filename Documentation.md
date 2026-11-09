# FounderOS documentation

## What FounderOS is

FounderOS is a founder command center: a product foundation for an AI operating system that helps a founder see important company changes, make better decisions, and prepare follow-through without giving up control.

It is designed around a simple belief:

> Founders do not need another chat window. They need an informed operating partner that understands the company’s goals, constraints, decisions, and signals.

FounderOS is currently an interactive frontend prototype. It demonstrates the core product experience—company setup, a daily executive brief, company intelligence, a decision ledger, an approval queue, and connector setup—using representative example data.

## What it aims to become

The long-term product is an evidence-backed AI chief of staff and executive operating system. It should:

- build a structured model of a company;
- collect signals from trusted business systems;
- notice changes that matter without waiting for a founder to ask;
- connect evidence to goals and constraints;
- challenge assumptions and show a skeptic view;
- record decisions, assumptions, and outcomes;
- draft follow-up work across business functions;
- require approval for external actions by default.

## Who it is for

The first intended user is an early-revenue B2B SaaS founder or a small founding team. This audience has many high-context responsibilities—product, customer discovery, sales, hiring, finances, and delivery—but lacks a chief of staff or a dedicated operations team.

The foundation can later support different founder contexts, including agencies, developer tools, marketplaces, and more mature startups.

## Current product experience

### 1. Founder onboarding

The first time the app opens, FounderOS asks for the context needed to make future recommendations useful:

- company name;
- founder name;
- company stage and team size;
- current strategic objective;
- ideal customer;
- primary metric;
- current constraint/bottleneck;
- minimum runway;
- initial business systems the founder wants to connect.

This becomes the **Company Model**. The founder can edit it later from the Company page.

### 2. Command center / daily CEO brief

The Overview page is the founder’s landing page. It shows:

- a high-level company-health snapshot;
- runway, critical alerts, and momentum;
- one CEO recommendation;
- evidence, confidence classification, and a skeptic view;
- today’s focus list;
- a ranked “What changed” signal feed;
- work that is ready for founder approval.

The current visual brief is representative. In a production version it will be generated from connected sources and will include source citations.

### 3. Decision ledger

The Decision Ledger is the beginning of institutional memory. It is intended to store:

- the decision made or proposed;
- its owner and decision date;
- evidence and assumptions;
- alternatives and counterarguments;
- review date;
- outcome and lessons learned.

The current app displays example decision records. Creating, editing, connecting evidence, and tracking outcomes are planned next-phase features.

### 4. Company intelligence

The Intelligence page is where FounderOS will surface meaningful change and opportunity across the company. It currently contains an example opportunity radar and watchlist.

Future intelligence may include:

- customer pain-point clusters;
- churn and support-risk signals;
- pipeline changes;
- product-activation changes;
- competitor launches and pricing changes;
- hiring or capacity risks;
- runway and spending thresholds;
- founder-defined market and regulation watchlists.

### 5. Company Model

The Company page makes the working context visible and editable. It includes strategic goal, target customer, primary metric, current constraint, and runway floor.

This prevents the system from offering generic advice that ignores what the founder is currently trying to achieve.

### 6. Connections

FounderOS has a connection setup surface for:

- Google Workspace;
- Slack;
- Linear;
- HubSpot;
- Stripe.

At present, selecting “Set up” only stores a local setup intent. It does not sign into these services, read data, store credentials, or make external changes.

## Example workflows

### Example: a morning founder brief

In the intended product, FounderOS might combine product analytics, recent customer emails, and CRM activity:

```text
Top recommendation: Pause Feature B and investigate activation.

What changed
• First-value completion fell 12% after Experiment B launched.
• Three recently inactive trials mentioned setup complexity.
• Enterprise pipeline is stable, so conversion—not demand—is the current constraint.

Skeptic view
The drop may be seasonal or limited to one segment. Interview five affected trials before drawing a permanent conclusion.

Actions prepared for approval
• Create a Linear investigation ticket.
• Draft five customer-interview emails.
• Add a decision review to Friday’s leadership meeting.
```

The founder can approve, reject, edit, or defer the proposed actions.

### Example: decision memory

A founder decides not to pursue enterprise customers because the team is too small. FounderOS stores the decision, rationale, and review date. Months later, when several enterprise prospects emerge, it can say:

```text
This resembles Decision #42: “Do not sell to enterprise yet.”

The original constraint was implementation capacity. That assumption may have changed:
• onboarding automation is now live;
• two prospects have similar requirements;
• current pipeline is 18% enterprise-led.

Recommendation: do not reverse the decision blindly. Run a five-account
enterprise discovery sprint and revisit the decision on the evidence.
```

### Example: controlled execution

FounderOS should never silently send a customer email or alter company records. Instead it prepares an action with context:

```text
Action: Send five customer-interview invitations
Source: Recent inactive trial cohort
Reason: Validate the suspected onboarding problem
Recipient list: [shown to founder]
Draft message: [shown to founder]
External effect: Emails will be sent
Required approval: Founder
```

Only after approval should a production system execute it and store a receipt in the audit log.

## How FounderOS helps a founder

| Founder problem | How FounderOS is intended to help |
|---|---|
| Important signals are scattered across tools | Gather trusted signals into one founder-relevant operating view |
| The founder is too busy to ask the right question | Surface changes and decisions proactively through daily/weekly cadences |
| Strategy gets disconnected from daily work | Rank recommendations against company goals, constraints, and metrics |
| Decisions are forgotten or repeatedly debated | Preserve decision rationale, assumptions, and outcomes |
| Too much work is administrative | Prepare drafts, tasks, reports, agendas, and follow-ups for approval |
| AI answers can be overconfident | Show evidence, alternatives, uncertainty, and a skeptic view |
| Autonomy feels unsafe | Require explicit approvals and provide traceability for external actions |

## What is implemented today

## Implemented Full-Stack Architecture

FounderOS is a complete full-stack software application with a FastAPI async backend, SQLModel database persistence, AES-256-GCM credential vault, and an interactive React 18 TypeScript frontend command cockpit with modular views and modals.

### 1. 👑 C-Suite Daily Executive Operating Suite
- **CEO Investor Update Synthesizer**: Automatically digests company stage, monthly milestones, MRR growth, and constraints into gold-standard YC/Sequoia monthly investor updates. Can be copied or staged to the draft action queue with 1 click.
- **⚡ Andy Grove LNO Task Prioritizer**: Automatically segments tasks into **10x Leverage** (deep founder focus), **1x Neutral**, and **<0.1x Overhead** (delegated to background AI workers).
- **💰 CFO Default Alive Runway Scenario Lab**: Interactive Paul Graham capital efficiency simulator with live sliders for cash balance, monthly burn, MRR, growth rates, headcount changes, and tooling spend.
- **💻 CTO Gary Klein Pre-Mortem & ADR Lab**: Simulates outage and scaling failure modes 6 months into the future before committing code; enforces Dan McKinley Boring Technology innovation token discipline.
- **📈 CRO MEDDPICC Deal Health Radar**: Audits enterprise pipeline deals across 8 qualification vectors (Metrics, Economic Buyer, Decision Criteria/Process, Paper Process, Pain, Champion, Competition) with objection talk tracks.
- **🎯 VP CS Superhuman PMF Engine**: Ingests user survey responses, calculates PMF score against Rahul Vohra's 40% "Very Disappointed" threshold, and segments High-Expectation Customers (HXC).

### 2. 🏛️ Authentic 2-Round Multi-Agent Board Debate Matrix & Live Streaming
- **Round 1 (Stance Formulation)**: 6 C-suite executive personas (**CRO**, **Skeptic / CPO**, **VP CS**, **CFO**, **CTO**, **COO**) independently formulate strategic perspectives grounded in startup frameworks.
- **Round 2 (Dialectic Cross-Examination)**: Personas engage in direct rebuttals across 3 organizational tension pairs (Skeptic vs. CTO, CFO vs. CRO, VP CS vs. COO).
- **Round 3 (CEO Synthesis)**: Synthesizes consensus (`STRONG GO`, `CONDITIONAL GO`, `HIGH RISK / PAUSE`), One Metric That Matters (OMTM), a 2-Week Minimum Viable Experiment (MVE), and explicit failure kill criteria.
- **Real-Time SSE Streaming (`GET /api/debate/stream`)**: Streams perspectives live as they materialize via Server-Sent Events, eliminating static waiting spinners.
- **Universal Provider Gateway**: Operates across 12 Frontier LLM connectors with live `/v1/models` discovery, connection pooling, and 100% offline local structured reasoning fallback.

### 3. 📊 AI Observability, Token Ledger & Cost Accounting
- **Live AI Token Burn & Cost Ledger**: Chronologically tracks token consumption (prompt, completion, reasoning), execution latency (ms), and estimated financial costs ($ USD) across OpenAI, Anthropic, Gemini, DeepSeek, Groq, and Ollama.
- **Cockpit Observability Dashboard**: Live stat cards in the UI displaying total spend, total tokens, total inferences, average latency, and provider breakdowns (`GET /api/observability/usage`).

### 4. 🔐 Multi-Tenant Authentication & Role-Based Access Control (RBAC)
- **PBKDF2 Password Hashing**: Standards-compliant PBKDF2-HMAC-SHA256 password hashing (100,000 iterations, 16-byte cryptographic salt).
- **HMAC-SHA256 JWT Engine**: Cryptographically signed access tokens with 7-day expiration.
- **RBAC Guard (`require_role`)**: Granular authorization supporting `OWNER`, `ADMIN`, `MEMBER`, and `VIEWER` roles.
- **Tenant Workspace Scoping**: Automatic tenant isolation (`get_current_workspace`) mapping authenticated users to their isolated workspace.

### 5. 🛡️ Security, Governance & Sandboxed Execution
- **Tri-Modal Security Postures**: `Strict` (100% human-in-the-loop), `Auto` (default, prompt injection screening with auto-staging), and `Dangerous` (autonomous execution).
- **Sandboxed Tool Execution Guard (`ExecutionSandbox`)**: Enforces subprocess isolation, automatic environment variable scrubbing (`AWS_*`, `VAULT_*`, `*_SECRET`, `*_KEY`), strict 5-second execution timeouts, and 64KB memory caps.
- **Action Safety Policy Filter**: Intercepts destructive shell, SQL, git force push, and secret exposure attempts.
- **AES-256-GCM Vault**: Encrypted credential storage with 0600 file permission enforcement for `.vault_key`.
- **OAuth 2.0 CSRF Protection**: HMAC-SHA256 signed state nonces with 10-minute TTL.
- **Approval-Gated Execution**: All autonomous task outputs are created as draft `ActionItem` objects awaiting founder sign-off before dispatch.

### 6. ⚡ Infrastructure, Concurrency & Data Persistence
- **SQLite WAL Mode**: Configured with `PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000;` to eliminate database locking under concurrent background worker execution.
- **Distributed Broadcast Bus**: `RedisBroadcastBackend` for horizontal multi-worker cluster scaling with automatic graceful fallback to `InMemoryBroadcastBackend`.
- **384-Dimensional Subword Semantic Vectorizer**: RAG embedding pipeline using subword character 3/4-grams and logarithmic TF weighting for high-precision business synonym retrieval.
- **Alembic Migration Pipeline**: Relational schema evolution tracked via versioned migration ledgers (`server/alembic/versions/`).

---

## Run the project locally

### Prerequisites
- **Node.js**: v18 or higher
- **Python**: v3.10 or higher

### 1. Start Frontend
```bash
npm install
npm run dev
```

### 2. Start Backend
```bash
cd server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. ./venv/bin/alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 3. Run Automated Test Suite (100% Offline)
```bash
PYTHONPATH=server ./server/venv/bin/python -m unittest discover -s server/tests -p "test_*.py" -v
```

---

## Safety Promise

FounderOS operates under strict execution guardrails:

> **Autonomous tasks may observe, synthesize, analyze, and draft. They must always stage external actions for founder review and approval before execution.**
