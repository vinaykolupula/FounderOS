# Security Policy

## 🔒 Supported Versions

FounderOS actively maintains and patches the latest major release:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

---

## 🛡️ Security Architecture Highlights

FounderOS stores sensitive startup data, business metrics, and third-party credentials. It employs enterprise-grade security controls:

### 1. AES-256-GCM Credential Vault
- Sensitive tokens (OAuth refresh tokens, AI provider API keys) are symmetrically encrypted at rest using AES-256-GCM with 96-bit random nonces (`server/app/vault.py`).
- **Production Enforcement**: Fails fast with a fatal `RuntimeError` if `VAULT_SECRET_KEY` is missing or invalid in production environments.
- **Local Development Guard**: Automatically generates a cryptographically secure 32-byte key stored in a local `.vault_key` file with strict `0600` POSIX file permissions.

### 2. Multi-Tenant Authentication & Role-Based Access Control (RBAC)
- **PBKDF2 Password Hashing**: Passwords are hashed using standard-library PBKDF2-HMAC-SHA256 with 100,000 iterations and unique 16-byte cryptographic salts (`server/app/auth.py`).
- **HMAC-SHA256 JWT Engine**: Issues cryptographically signed access tokens with 7-day expiration.
- **Granular RBAC (`require_role`)**: Enforces strict permissions across `OWNER`, `ADMIN`, `MEMBER`, and `VIEWER` roles.
- **Tenant Workspace Scoping**: All workspace endpoints resolve the tenant scope (`workspace_id`) from the authenticated JWT token, preventing cross-tenant access.

### 3. Sandboxed Tool Execution Guard (`ExecutionSandbox`)
- Subprocess execution boundary enforcing strict 5.0-second timeout limits with automatic process termination (`kill`) upon timeout.
- **Environment Variable Scrubbing**: Strips all high-privilege credentials (`AWS_*`, `VAULT_*`, `FOUNDEROS_*`, `*_SECRET`, `*_KEY`, `*_TOKEN`, `DATABASE_URL`) from child process environments.
- **Destructive Command Deny**: Intercepts destructive shell commands (`dd if=`, `mkfs`, fork bombs `:(){ :|:& };:`) before subprocess spawning.
- **Memory Protection**: Output truncation at 64KB (`MAX_OUTPUT_BYTES = 65536`) to prevent memory exhaustion.

### 4. Multi-Layer Prompt Injection Shield
- Unified screening gate (`ActionPolicyEngine` in `server/app/policy/action_policy.py`) protecting RAG context and external signal ingestion.
- Normalizes Unicode via NFKC, decodes URL percent-encodings, strips zero-width/formatting characters, and recursively inspects base64-encoded strings for adversarial instructions.

### 5. Approval-Gated Architecture
- Automated tasks executed by background workers never dispatch external API actions directly.
- All automated outputs are generated as draft `ActionItem` objects set to status `'Ready'`, awaiting explicit founder sign-off in the UI.

### 6. OAuth 2.0 CSRF Protection & Header Transport
- All third-party OAuth flows utilize HMAC-SHA256 authenticated state nonces with 10-minute validity (`server/app/routers/auth.py`).
- Gemini and frontier LLM connectors transmit API keys strictly via HTTP headers (`x-goog-api-key`, `Authorization`) rather than URL query parameters.
- Offline mock adapters eliminate external credential exposure to public echo services.

---

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability within FounderOS, please report it responsibly:
1. **Do NOT open a public GitHub issue.**
2. Send a detailed report describing the vulnerability, affected components, and proof of concept to the maintainers via private security disclosure or email.
3. We will acknowledge receipt within 48 hours and work with you on a fix and coordinated release.
