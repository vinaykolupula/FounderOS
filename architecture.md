# FounderOS Architecture — Technical Specification & System Design

## Purpose of this Document

This is the authoritative technical specification for **FounderOS**, the open-source founder command center. It documents the full-stack system architecture, data models, security vault primitives, multi-agent AI execution engine, multi-tenant authentication, telemetry observability, and verification standards.

**Status Key**
- **Implemented** — Fully implemented, tested, and runnable in this repository.
- **Prototype / Simulated** — Functional end-to-end interface backed by representative API fixtures or mock provider connectors.
- **Planned** — Roadmap items scheduled for future iterations.

---

## 1. Product Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│              FOUNDER EXPERIENCE LAYER (React 18 + TypeScript + Vite)            │
│  • Modular Views (src/views/): Overview, Tasks, Executive, Decisions, Models... │
│  • Interactive Modals (src/modals/): Debate, Briefing, Decision, Task, Signals  │
│  • Real-Time SSE Stream Reader   • Security Posture Controls   • Toast Notices  │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │  HTTP REST / SSE Streams / WebSockets
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     BACKEND API LAYER (FastAPI + Pydantic v2)                   │
│  • /api/auth (Register, Login, Me, OAuth)  • /api/observability (Usage, Recent)│
│  • /api/debate & /api/debate/stream (SSE)  • /api/workspace & /api/tasks        │
│  • /api/briefing & /api/executive-tools    • /ws/{workspace_id} (Pub/Sub Sync)  │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         FOUNDER INTELLIGENCE & AI CORE                          │
│  • Universal LLM Connector Registry (Hermes / OpenClaw polymorphic transport)   │
│  • Dynamic Live Model Auto-Discovery (/v1/models query engine)                  │
│  • 2-Round Dialectic Debate Matrix (Round 1: Stances -> Round 2: Rebuttals)     │
│  • CEO Orchestrator (Synthesis, One Metric That Matters & 2-Week MVE)           │
│  • AI Observability & Cost Telemetry Engine (Pricing catalog, token ledger)     │
│  • Multi-Layer Prompt Injection Shield & Sandboxed Execution Guard (SEC-07)     │
│  • 384-Dimensional Subword Morphological Semantic Vectorizer (RAG Pipeline)     │
│  • Autonomous Execution Worker & Goal Completion Audit                          │
└───────────────────┬─────────────────────────────────────────┬───────────────────┘
                    │                                         │
                    ▼                                         ▼
┌───────────────────────────────────────┐ ┌───────────────────────────────────────┐
│     SECURITY & DATA PERSISTENCE       │ │    2026 FRONTIER AI CONNECTORS (12)   │
│ • SQLModel DB (SQLite WAL / PostgreSQL│ │ • Claude Opus 5 / Fable 5 / Sonnet 5  │
│ • Alembic Schema Migration Ledger     │ │ • GPT-5.6 Sol (max) & Luna / o3-mini  │
│ • AES-256-GCM Vault (0600 key guard)  │ │ • Grok 4.6 (high) & Grok 4.5          │
│ • Distributed Redis Broadcast Backend │ │ • Kimi K3 (max 2.8T) & K2.7 Code      │
│ • PBKDF2 Password & HMAC-SHA256 JWT   │ │ • Gemini 3.7 Flash & 3.1 Pro (high)   │
│ • Role-Based Access Control (RBAC)    │ │ • DeepSeek V4 Pro 0813 (max) & R1     │
│ • Scoped Notebook Memory (MEMORY.md)  │ │ • GLM-5.2 (max), Nemotron 3, Muse 1.2 │
└───────────────────────────────────────┘ └───────────────────────────────────────┘
```

---

## 2. Core Backend Modules & Services

### 2.1 Universal LLM Connector & Dynamic Provider Registry (`server/app/services/llm_connectors.py` & `llm.py`)
- **Hermes / OpenClaw Architecture**: Decouples agent orchestration from vendor implementations via polymorphic connector adapters (`OpenAICompatibleConnector`, `AnthropicConnector`, `GeminiConnector`, `OllamaConnector`).
- **Connection Pooling & Persistent Keepalive (PERF-03)**: Persistent, loop-bound `httpx.AsyncClient` pool eliminates TLS renegotiation overhead across concurrent persona queries.
- **Header-Based Gemini Authentication (SEC-04)**: Transmits API keys via standard `x-goog-api-key` HTTP headers rather than URL query strings.
- **2026 Intelligence Leaderboard Integration**: Direct support for Claude Opus/Fable 5 (max), GPT-5.6 Sol/Luna (max), Grok 4.6 (high), Kimi K3 (max), Gemini 3.7 Flash (high), DeepSeek V4 Pro (max), GLM-5.2 (max), Nemotron 3 Ultra, and Muse Spark 1.2 (xhigh).
- **Cognitive Depth & Reasoning Effort Controls**: Injects multi-level thinking budgets (`max`, `xhigh`, `high`, `medium`, `off`) dynamically across Anthropic thinking tokens, OpenAI reasoning effort, Gemini thinkingConfig, and DeepSeek reasoner.
- **Live Auto-Discovery (`POST /api/settings/models/discover`)**: Dynamically queries the provider's `/v1/models` and `/models` endpoints in real time, auto-populating active models directly from the founder's account without code stagnation.
- **Custom Base URL & Endpoint Flexibility**: Supports user-defined custom base URLs (e.g. self-hosted vLLM, LM Studio, Azure OpenAI, local inference).

### 2.2 Authentic 2-Round Board Debate Dialectic (`server/app/services/llm.py` & `debate.py`)
- **Round 1 (Stance Formulation)**: 6 C-suite personas (**CRO**, **Skeptic / CPO**, **VP CS**, **CFO**, **CTO**, **COO**) independently formulate strategic perspectives grounded in proven startup frameworks.
- **Round 2 (Cross-Examination Dialectic)**: Evaluates organizational tensions in peer-to-peer rebuttals:
  - *Skeptic vs. CTO*: Gary Klein Pre-Mortem vs. Dan McKinley Boring Tech and Two-Way Door reversibility.
  - *CFO vs. CRO*: Paul Graham Default Alive & Burn Multiple vs. Reforge Growth Loops and MEDDPICC velocity.
  - *VP CS vs. COO*: TTFV & NRR retention vs. Keith Rabois Barrels & Ammunition execution capacity.
- **Round 3 (CEO Orchestrator Synthesis)**: Synthesizes consensus (`STRONG GO`, `CONDITIONAL GO`, `HIGH RISK / PAUSE`), One Metric That Matters (OMTM), a 2-Week Minimum Viable Experiment (MVE), and explicit failure kill criteria.
- **Server-Sent Events (SSE) Streaming Gateway (HARNESS-02)**: `GET /api/debate/stream` sequentially streams events (`round1_start`, `round1_persona`, `round2_start`, `round2_dialectic`, `round3_start`, `debate_complete`) to avoid static loading spinners during reasoning.
- **Local Fallback Heuristics**: Deterministically computes full 2-round dialectic debates and CEO syntheses offline grounded in company profile data.

### 2.3 Multi-Tenant JWT Authentication & RBAC Engine (`server/app/auth.py` & `routers/auth.py`)
- **PBKDF2 Password Hashing**: Standards-compliant PBKDF2-HMAC-SHA256 password hashing with unique 16-byte cryptographic salts and 100,000 iterations (standard library, zero external compiled dependencies).
- **HMAC-SHA256 JWT Engine**: Cryptographically signed access tokens with 7-day expiration derived from the vault key or `JWT_SECRET_KEY`.
- **Role-Based Access Control (RBAC)**: `require_role([UserRole.OWNER, UserRole.ADMIN, UserRole.MEMBER, UserRole.VIEWER])` dependency factory enforcing granular permission checks across API endpoints.
- **Tenant Workspace Scoping**: `get_current_workspace` extracts the tenant scope from the authenticated user, enforcing complete multi-tenant isolation.
- **Backward Compatibility**: Permissive local development mode when `AUTH_ENABLED=False` cleanly resolves the root workspace for single-user cockpits.

### 2.4 AI Observability & Token Cost Accounting Service (`server/app/services/telemetry.py` & `routers/observability.py`)
- **Standardized Pricing Catalog**: Comprehensive per-million-token cost models for OpenAI, Anthropic, Gemini, DeepSeek, Groq, and Ollama (local free).
- **Asynchronous Telemetry Recording**: Non-blocking token and latency logging (`TokenUsageLedger`) on every model completion.
- **Observability REST Endpoints**:
  - `GET /api/observability/usage`: Total AI spend ($ USD), total tokens, average latency, provider breakdown, model breakdown, and 7-day daily burn trend.
  - `GET /api/observability/recent`: Chronological audit log of recent model inference events.

### 2.5 Sandboxed Tool Execution Guard (`server/app/policy/action_policy.py`)
- **Process Isolation (`ExecutionSandbox`)**: Subprocess execution boundary enforcing strict 5.0-second timeout limits with automated process tree termination.
- **Environment Scrubbing**: Automatically strips all high-privilege credentials (`AWS_*`, `VAULT_*`, `FOUNDEROS_*`, `*_SECRET`, `*_KEY`, `*_TOKEN`, `DATABASE_URL`) from child process environments.
- **Policy Enforcement**: Pre-execution AST/regex inspection denying destructive commands (`dd if=`, `mkfs`, fork bombs `:(){ :|:& };:`) before subprocess spawning.
- **Memory Protection**: Output truncation at 64KB (`MAX_OUTPUT_BYTES = 65536`) preventing denial-of-service memory exhaustion.

### 2.6 Distributed Broadcast Event Bus (`server/app/services/events.py`)
- **Redis Pub/Sub Backend (`RedisBroadcastBackend`)**: Disseminates UI synchronization signals across distributed FastAPI worker processes in multi-pod or multi-worker deployments.
- **Graceful Offline Fallback**: Automatically falls back to `InMemoryBroadcastBackend` if `REDIS_URL` is omitted or Redis is unreachable, ensuring frictionless single-node development.

### 2.7 Subword Morphological Semantic Vectorizer in RAG (`server/app/rag.py`)
- **384-Dimensional Vectorizer**: Uses subword character 3-grams and 4-grams (`<word>`), term frequency logarithmic weighting ($1 + \ln(1 + \text{count})$), and dual Murmur/CRC32 sign dispersion with L2 Euclidean normalization.
- **High-Precision Retrieval**: Eliminates orthogonal hash collisions, enabling semantic ranking of business synonyms ("churn", "cancellation", "attrition").

### 2.8 Database Migration Ledger (`server/alembic/`)
- Complete Alembic migration environment tracking relational schema evolution across deployments:
  - `8391b5884c22_baseline_schema.py`: Baseline tables, foreign keys, and B-tree indexes.
  - `a68853e21928_observability_and_auth.py`: `User` and `TokenUsageLedger` tables and indexes.

---

## 3. Database Schema (`server/app/models.py`)

- **`Workspace`**: Root tenant container isolating company data, settings, and agent history.
- **`User`**: Tenant user account with `email`, `hashed_password`, `role` (`UserRole`), `is_active`, and `workspace_id`.
- **`TokenUsageLedger`**: Chronological record of AI inference requests, token counts (prompt, completion, reasoning), latency (ms), and estimated cost ($ USD).
- **`CompanyProfile`**: Stage, team size, business model, burn rate, runway, primary constraint, competitive moat, and tech stack.
- **`FounderProfile`**: Superpowers, primary gaps, energy states, and communication style preferences.
- **`Task`**: Prioritized founder tasks (`P0_CRITICAL` through `P3_LOW`) with delegation status (`PENDING`, `DELEGATED`, `COMPLETED`, `FAILED`).
- **`ActionItem`**: Approval-gated draft outputs awaiting founder sign-off (`Ready` / `Draft`).
- **`Evidence`**: Ingested signal items with vector embeddings and provenance links.
- **`Decision`**: Institutional memory capturing strategic decisions, tradeoffs, and dynamic `review_date`.
- **`AuditLog`**: Immutable event history tracking all agent and human actions (indexed on `event` and `created_at`).
- **`AIProviderSetting`**: AES-256-GCM encrypted provider credentials, active model selection, custom base URL, and cognitive depth settings.
- **`Connector`**: Integration configurations and vault-encrypted OAuth tokens for Gmail, Slack, Linear, HubSpot, and Stripe.

---

## 4. Verification, Testing & Operations

### 4.1 Running the Full Stack Locally
```bash
# Terminal 1: Start React Frontend (Vite)
npm run dev

# Terminal 2: Start FastAPI Backend
cd server
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### 4.2 Automated Test Suite (100% Offline, Fast)
```bash
PYTHONPATH=server ./server/venv/bin/python -m unittest discover -s server/tests -p "test_*.py" -v
```

### 4.3 Database Migrations
```bash
cd server
# Inspect current revision head
PYTHONPATH=. ./venv/bin/alembic current

# Apply pending migrations
PYTHONPATH=. ./venv/bin/alembic upgrade head
```

### 4.4 Frontend Production Build
```bash
npm run build
```
