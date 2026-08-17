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

import re
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("founderos.policy")

SECURITY_POSTURES = ["strict", "auto", "dangerous"]
DEFAULT_SECURITY_POSTURE = "auto"

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
        "pattern": r"\b(mkfs|dd\s+if=)\b|:\(\)\s*\{",
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
    Evaluates actions, shell commands, and API payloads against organizational safety floors.
    """

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

        # 2. Check safety rules against payload
        for rule in SAFETY_RULES:
            match = re.search(rule["pattern"], payload_text, re.IGNORECASE)
            if match:
                logger.warning(f"Safety rule matched ({rule['decision']}): {rule['reason']}")
                return rule["decision"], rule["reason"]

        # 3. Default decision based on posture
        if posture == "dangerous":
            return "allow", None
            
        return "allow", None

    @staticmethod
    def screen_external_signal(signal_text: str) -> Dict[str, Any]:
        """
        Security classifier screening external text (emails, Slack messages, tickets)
        for prompt injection and data exfiltration directives.
        """
        injection_patterns = [
            r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
            r"disregard\s+(system\s+)?prompt",
            r"you\s+are\s+now\s+in\s+developer\s+mode",
            r"send\s+(me\s+)?(all\s+)?(api|keys|passwords|secrets|vault)",
            r"curl\s+https?://[^\s]+\s+-d",
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, signal_text, re.IGNORECASE):
                return {
                    "is_safe": False,
                    "action": "sanitize_and_flag",
                    "reason": "Detected adversarial prompt injection directive"
                }

        return {"is_safe": True, "action": "pass", "reason": None}
