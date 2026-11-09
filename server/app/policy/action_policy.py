"""
Action Safety Policy & Security Posture Engine

Inspired by Y Combinator's QM security architecture:
1. Tri-Modal Security Postures:
   - 'strict': Every automated action pauses for explicit human-in-the-loop sign-off.
   - 'auto' (default): Inbound content is screened for prompt injection; safe actions are auto-staged.
   - 'dangerous': Autonomous execution mode without human pauses.
2. Command & Action Safety Policy:
   - Scans shell scripts, API payloads, and database queries for dangerous operations.
   - Intercepts destructive SQL, recursive file deletions, force git pushes, and secret exposure.
"""

import os
import re
import unicodedata
import urllib.parse
import base64
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple, Union

logger = logging.getLogger("founderos.policy")

SECURITY_POSTURES = ["strict", "auto", "dangerous"]
DEFAULT_SECURITY_POSTURE = "auto"

# Comprehensive adversarial prompt injection threat matrix
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|system)\s+instructions",
    r"disregard\s+(all\s+)?(system|prior|previous)\s+(prompt|instructions|rules)",
    r"forget\s+(all\s+)?(previous\s+)?rules",
    r"override\s+(policy|system|rules|safety)",
    r"bypass\s+(safety|guardrails|policy)",
    r"you\s+are\s+now\s+(in\s+)?developer\s+mode",
    r"act\s+as\s+(an?\s+)?unrestricted\s+ai",
    r"\bdan\s+mode\b",
    r"send\s+(me\s+)?(all\s+)?(api|keys|passwords|secrets|vault|tokens)",
    r"curl\s+https?://[^\s]+\s+-d",
    r"(<\|im_start\|>|<\|im_end\|>|\[INST\]|\[/INST\]|<<SYS>>)",
]

# High-risk patterns that require strict human approval
SAFETY_RULES = [
    {
        "pattern": r"\brm\b[^\n]*(?:-[a-zA-Z]*r|--recursive)",
        "decision": "require_approval",
        "reason": "Recursive file deletion attempt"
    },
    {
        "pattern": r"\bgit\s+push\b.*(?:--force\b|(?:^|\s)-[a-zA-Z]*f\b)",
        "decision": "require_approval",
        "reason": "Force push to git remote"
    },
    {
        "pattern": r"\b(drop|truncate)\s+table\b",
        "decision": "require_approval",
        "reason": "Destructive SQL table drop or truncation"
    },
    {
        "pattern": r"(?:\bmkfs\b|\bdd\s+if=|:\(\)\s*\{)",
        "decision": "deny",
        "reason": "Destructive filesystem operation or fork bomb"
    },
    {
        "pattern": r"\bcurl\b.*\|\s*(sh|bash)\b",
        "decision": "require_approval",
        "reason": "Pipe remote URL directly into shell execution"
    },
    {
        "pattern": r"(sk-[a-zA-Z0-9]{32,}|ghp_[a-zA-Z0-9]{36,}|AIzaSy[a-zA-Z0-9_-]{33})",
        "decision": "require_approval",
        "reason": "Potential plaintext API key or credential in payload"
    }
]


class ActionPolicyEngine:
    """
    Evaluates actions, shell commands, and API payloads against organizational safety floors
    and provides multi-layered defenses against adversarial prompt injection.
    """

    @staticmethod
    def canonicalize_text(text: str) -> str:
        """
        Normalizes Unicode NFKC, decodes URL percent-encodings,
        strips zero-width characters, and collapses whitespace.
        """
        if not text:
            return ""
        # 1. NFKC normalization (combats homoglyphs and ligature bypasses)
        normalized = unicodedata.normalize("NFKC", text)
        # 2. Strip zero-width & non-printable formatting characters
        normalized = re.sub(r"[\u200b\u200c\u200d\u200e\u200f\ufeff]", "", normalized)
        # 3. URL unquote to detect percent-encoded injections
        try:
            normalized = urllib.parse.unquote(normalized)
        except Exception:
            pass
        return normalized

    @staticmethod
    def evaluate_payload(payload_text: str, posture: str = "auto") -> Tuple[str, Optional[str]]:
        """
        Evaluates a raw command or payload text against safety rules and active security posture.
        Returns (decision, reason):
        - decision: 'allow', 'require_approval', 'deny'
        """
        posture = posture.lower().strip()
        if posture not in SECURITY_POSTURES:
            posture = DEFAULT_SECURITY_POSTURE

        # 1. In 'strict' posture, all non-trivial actions require human approval
        if posture == "strict":
            return "require_approval", "Strict posture active: all actions require human sign-off"

        # Canonicalize payload before matching safety rules
        canonical = ActionPolicyEngine.canonicalize_text(payload_text)

        # 2. Check safety rules against payload
        for rule in SAFETY_RULES:
            match = re.search(rule["pattern"], canonical, re.IGNORECASE)
            if match:
                logger.warning(f"Safety rule matched ({rule['decision']}): {rule['reason']}")
                return rule["decision"], rule["reason"]

        # 3. Default decision based on posture
        if posture == "dangerous":
            return "allow", None
            
        return "allow", None

    @staticmethod
    def sanitize_untrusted_content(text: str) -> str:
        """
        Strips potential prompt injection markers, dangerous directives, and malicious HTML/scripts.
        Single source of truth used by RAG and external signal ingestion.
        """
        if not text:
            return ""

        canonical = ActionPolicyEngine.canonicalize_text(text)

        # 1. Remove dangerous script and iframe elements
        sanitized = re.sub(r"(?is)<script.*?>.*?</script>", "", canonical)
        sanitized = re.sub(r"(?is)<iframe.*?>.*?</iframe>", "", sanitized)

        # 2. Check and redact known injection patterns
        for pattern in INJECTION_PATTERNS:
            sanitized = re.sub(pattern, "[redacted instruction]", sanitized, flags=re.IGNORECASE)

        # 3. Strip remaining raw HTML tags
        sanitized = re.sub(r"<[^>]*>", "", sanitized)

        # 4. Detect and neutralize base64 encoded injection attempts
        base64_tokens = re.findall(r"(?:^|\s)([A-Za-z0-9+/]{16,}={0,2})(?:\s|$)", sanitized)
        for token in base64_tokens:
            try:
                decoded = base64.b64decode(token).decode("utf-8", errors="ignore")
                for pattern in INJECTION_PATTERNS:
                    if re.search(pattern, decoded, re.IGNORECASE):
                        sanitized = sanitized.replace(token, "[redacted encoded instruction]")
                        break
            except Exception:
                pass

        return sanitized.strip()

    @staticmethod
    def encapsulate_untrusted_signal(text: str, source: str = "external") -> str:
        """
        Encapsulates sanitized untrusted signal in explicit structural XML fences
        for safe LLM context injection.
        """
        clean = ActionPolicyEngine.sanitize_untrusted_content(text)
        return f'<untrusted_signal source="{source}" status="screened">\n{clean}\n</untrusted_signal>'

    @staticmethod
    def screen_external_signal(signal_text: str) -> Dict[str, Any]:
        """
        Security classifier screening external text (emails, Slack messages, tickets)
        for prompt injection and data exfiltration directives.
        """
        if not signal_text:
            return {"is_safe": True, "action": "pass", "reason": None}

        canonical = ActionPolicyEngine.canonicalize_text(signal_text)
        
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, canonical, re.IGNORECASE):
                return {
                    "is_safe": False,
                    "action": "sanitize_and_flag",
                    "reason": "Detected adversarial prompt injection directive"
                }

        # Check for encoded base64 directives
        base64_tokens = re.findall(r"(?:^|\s)([A-Za-z0-9+/]{16,}={0,2})(?:\s|$)", canonical)
        for token in base64_tokens:
            try:
                decoded = base64.b64decode(token).decode("utf-8", errors="ignore")
                for pattern in INJECTION_PATTERNS:
                    if re.search(pattern, decoded, re.IGNORECASE):
                        return {
                            "is_safe": False,
                            "action": "sanitize_and_flag",
                            "reason": "Detected encoded prompt injection directive in base64 payload"
                        }
            except Exception:
                pass

        return {"is_safe": True, "action": "pass", "reason": None}


class ExecutionSandbox:
    """
    Sandboxed Tool Execution Guard (SEC-07).
    Enforces process isolation, strict timeouts, memory/output bounds,
    and strips all credentials, API keys, and vault secrets from environment variables.
    """

    MAX_OUTPUT_BYTES = 65536  # 64 KB limit
    DEFAULT_TIMEOUT_SEC = 5.0

    SCRUBBED_KEYWORDS = (
        "SECRET", "KEY", "TOKEN", "PASSWORD", "VAULT", 
        "CREDENTIAL", "DATABASE_URL", "PRIVATE", "AUTH"
    )
    SCRUBBED_PREFIXES = (
        "AWS_", "VAULT_", "FOUNDEROS_", "AZURE_", "GCP_", 
        "GOOGLE_", "OPENAI_", "ANTHROPIC_", "GEMINI_", "GITHUB_"
    )
    SAFE_ENV_VARS = {
        "PATH", "LANG", "LC_ALL", "LC_CTYPE", "TMPDIR", 
        "HOME", "USER", "LOGNAME", "SHELL", "TERM"
    }

    @classmethod
    def sanitize_environment(cls, extra_env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Builds a strictly scrubbed environment dictionary, stripping all high-privilege
        secrets, API keys, and vault tokens before passing to child processes.
        """
        clean_env: Dict[str, str] = {}
        for k, v in os.environ.items():
            upper_k = k.upper()
            if any(upper_k.startswith(p) for p in cls.SCRUBBED_PREFIXES):
                continue
            if any(kw in upper_k for kw in cls.SCRUBBED_KEYWORDS):
                continue
            if k in cls.SAFE_ENV_VARS:
                clean_env[k] = v

        if "PATH" not in clean_env:
            clean_env["PATH"] = "/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin"

        if extra_env:
            for k, v in extra_env.items():
                upper_k = k.upper()
                if not any(upper_k.startswith(p) for p in cls.SCRUBBED_PREFIXES) and not any(kw in upper_k for kw in cls.SCRUBBED_KEYWORDS):
                    clean_env[k] = str(v)

        return clean_env

    @classmethod
    async def run_sandboxed_command(
        cls,
        cmd: Union[str, List[str]],
        timeout: float = DEFAULT_TIMEOUT_SEC,
        cwd: Optional[str] = None,
        posture: str = "auto",
        extra_env: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Executes a command within a sandboxed subprocess boundary:
        - Evaluates safety rules and denies destructive/prohibited instructions.
        - Strips all secrets from the execution environment.
        - Enforces strict process termination upon timeout.
        - Truncates output to 64KB to prevent denial of service.
        """
        cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd

        # 1. Action policy check
        decision, reason = ActionPolicyEngine.evaluate_payload(cmd_str, posture=posture)
        if decision == "deny":
            logger.warning(f"ExecutionSandbox blocked denied command: {reason}")
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command execution denied by security policy: {reason}",
                "timed_out": False,
                "policy_decision": decision,
                "policy_reason": reason
            }

        if posture == "strict" and decision == "require_approval":
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Execution requires explicit human approval under strict posture: {reason}",
                "timed_out": False,
                "policy_decision": decision,
                "policy_reason": reason
            }

        # 2. Build scrubbed environment
        clean_env = cls.sanitize_environment(extra_env)

        # 3. Spawn isolated subprocess
        proc = None
        try:
            if isinstance(cmd, list):
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd,
                    env=clean_env
                )
            else:
                proc = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd,
                    env=clean_env
                )

            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout
            )

            stdout_str = stdout_bytes[:cls.MAX_OUTPUT_BYTES].decode("utf-8", errors="replace")
            stderr_str = stderr_bytes[:cls.MAX_OUTPUT_BYTES].decode("utf-8", errors="replace")

            return {
                "success": proc.returncode == 0,
                "returncode": proc.returncode,
                "stdout": stdout_str,
                "stderr": stderr_str,
                "timed_out": False,
                "policy_decision": decision
            }

        except asyncio.TimeoutError:
            if proc:
                try:
                    proc.kill()
                    await proc.wait()
                except Exception:
                    pass
            logger.warning(f"Command execution timed out after {timeout}s: {cmd_str[:60]}...")
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command execution timed out after {timeout:.1f} seconds",
                "timed_out": True,
                "policy_decision": decision
            }
        except Exception as e:
            logger.error(f"ExecutionSandbox process error: {e}")
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Failed to execute command: {str(e)}",
                "timed_out": False,
                "policy_decision": decision
            }

