# Security Policy

## 🔒 Supported Versions

FounderOS actively maintains and patches the latest major release:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

---

## 🛡️ Security Architecture Highlights

FounderOS stores sensitive startup data and third-party credentials:
- **AES-256-GCM Vault**: Sensitive tokens (OAuth refresh tokens, OpenAI/Gemini/Anthropic API keys) are symmetrically encrypted at rest using AES-256-GCM with 96-bit random nonces (`server/app/vault.py`).
- **Approval-Gated Architecture**: Automated tasks generate draft `ActionItem` objects and require explicit founder sign-off before dispatching external calls.
- **Prompt Injection Defense**: Ingested external signals (emails, Slack messages, tickets) pass through `sanitize_untrusted_content()` in `server/app/rag.py` to strip adversarial prompt override directives.

---

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability within FounderOS, please report it responsibly:
1. **Do NOT open a public GitHub issue.**
2. Send a detailed report describing the vulnerability, affected components, and proof of concept to the maintainers via private security disclosure or email.
3. We will acknowledge receipt within 48 hours and work with you on a fix and coordinated release.
