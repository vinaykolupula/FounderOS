---
trigger: always_on
---

# FounderOS Agent Instructions & Coding Rules

This document provides essential context, architectural rules, and operational guidelines for AI coding assistants working on the **FounderOS** codebase.

---

## 🛑 Critical Rules & Guardrails

1. **Read-Only Sources Directory**:
   - **NEVER** edit, rename, move, or delete any files inside the `sources/` directory.
   - All files under `sources/` are synced reference materials from the ChatGPT project mirror.

2. **Approval-Gated Execution Architecture**:
   - Autonomous tasks executed by `server/app/workers/execution.py` must **NEVER** dispatch external actions directly without human intervention.
   - All automated outputs must be generated as draft `ActionItem` objects set to status `'Ready'` or `'Draft'`, awaiting explicit founder sign-off in the UI.

3. **Vault Encryption Security**:
   - Never write plain text OAuth refresh tokens or AI Provider API keys directly to database fields.
   - Always use `encrypt_token()` and `decrypt_token()` from `server/app/vault.py` (AES-256-GCM authenticated encryption).

4. **Production Error Handling & Recovery**:
   - **No Silent Failures**: Never swallow exceptions with empty `except:` blocks or return dummy fallback nulls silently.
   - Backend API endpoints must raise `HTTPException` with clear `detail` strings.
   - Frontend API client (`src/api.ts`) must throw errors so React components can trigger `setErrorNotice()` toasts.
   - Failed background tasks in `execution.py` must update task status to `'FAILED'`, set `agent_note`, write an `AuditLog` entry, and expose a retry button in the UI.

5. **Agent Harness & Mental Framework Alignment**:
   - When modifying `LLMEngine` board member personas in `server/app/services/llm.py`, preserve real-world startup frameworks:
     - **CRO**: Reforge Growth Loops, MEDDPICC, CAC Payback.
     - **Skeptic**: Gary Klein's Pre-Mortem, 5-Whys Friction Audit.
     - **VP CS**: Superhuman PMF Engine (Rahul Vohra), TTFV, NRR.
     - **CFO**: Default Alive vs. Default Dead (Paul Graham), Burn Multiple.
     - **CTO**: Boring Technology Rule (Dan McKinley), Two-Way Door Decisions.
     - **CEO**: One Metric That Matters (OMTM), Minimum Viable Experiment (MVE).

---

## ⚡ Command Cheat Sheet

```bash
# Start React Frontend (Vite)
npm run dev

# Start FastAPI Backend (Server)
cd server && uvicorn app.main:app --reload --port 8000
```
