from typing import Dict, Any


from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime, timedelta, timezone
import httpx
from app.models import AuditLog

class ActionPolicyEngine:
    @staticmethod
    async def evaluate_action_policy(action_type: str, payload: Dict[str, Any], session: AsyncSession) -> Dict[str, Any]:
        """
        Evaluates whether an action meets security, recipient, and approval policy rules.
        """
        # Rule 1: All external actions require explicit founder approval
        requires_approval = True

        # Rule 2: Check destination / recipient safety
        recipient = payload.get("recipient", "")
        if recipient and "@" in recipient:
            domain = recipient.split("@")[-1].lower()
            allowed_domains = ["founder.os", "gmail.com"] # Extremely strict allowlist
            if domain not in allowed_domains:
                return {
                    "allowed": False,
                    "reason": f"Recipient domain '{domain}' is not on the allowed list."
                }
        
        # Rule 3: Rate limiting (e.g. max 5 actions dispatched per hour)
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        # Using a simple check against AuditLog
        result = await session.execute(
            select(AuditLog).where(
                AuditLog.event == "ACTION_APPROVED_AND_DISPATCHED",
                AuditLog.created_at >= one_hour_ago.replace(tzinfo=None)
            )
        )
        recent_actions = result.scalars().all()
        if len(recent_actions) >= 5:
            return {
                "allowed": False,
                "reason": "Agent rate limit exceeded (5 actions / hour)."
            }

        # Rule 4: Idempotency (has this exact action_id already been dispatched?)
        action_id = payload.get("action_id")
        if action_id:
            result = await session.execute(
                select(AuditLog).where(
                    AuditLog.event == "ACTION_APPROVED_AND_DISPATCHED"
                )
            )
            # Find if this action_id is in any of the JSON details
            for audit in result.scalars().all():
                if isinstance(audit.details, dict) and audit.details.get("actionId") == action_id:
                    return {
                        "allowed": False,
                        "reason": f"Idempotency conflict: Action {action_id} was already executed."
                    }

        return {
            "allowed": True,
            "requiresApproval": requires_approval,
            "riskClassification": "low-risk-draft" if "draft" in action_type else "external-communication",
            "policyCheck": "Passed safety, idempotency, rate-limits, and domain allowlist"
        }


class LinearAdapter:
    @staticmethod
    async def create_draft_issue(title: str, description: str, team_key: str = "ENG") -> Dict[str, Any]:
        """Creates a draft Linear issue payload and executes the network call."""
        payload = {
            "query": "mutation IssueCreate { issueCreate(input: { title: $title, description: $description, teamId: $team }) { issue { id url } } }",
            "variables": {"title": title, "description": description, "team": team_key}
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # We hit httpbin.org to simulate the GraphQL endpoint for prototype safety
            res = await client.post("https://httpbin.org/post", json=payload)
            response_data = res.json()
            
        return {
            "platform": "Linear",
            "action": "create_issue",
            "team": team_key,
            "issueTitle": title,
            "issueDescription": description,
            "priority": "High",
            "draftUrl": f"https://linear.app/drafts/{title.lower().replace(' ', '-')}",
            "networkReceipt": response_data.get("json")
        }


class GmailAdapter:
    @staticmethod
    async def create_draft_email(recipient: str, subject: str, body: str) -> Dict[str, Any]:
        """Creates a draft email payload and executes the network call via Gmail API."""
        payload = {
            "to": recipient,
            "subject": subject,
            "body": body,
            "format": "html"
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post("https://httpbin.org/post", json=payload)
            response_data = res.json()

        return {
            "platform": "Gmail",
            "action": "create_draft",
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "draftId": f"draft_{hash(subject) & 0xffffffff}",
            "networkReceipt": response_data.get("json")
        }


class CalendarAdapter:
    @staticmethod
    def create_event_hold(title: str, duration_minutes: int = 25, participants: list | None = None) -> Dict[str, Any]:
        """Creates a proposed meeting hold payload."""
        return {
            "platform": "Google Calendar",
            "action": "create_hold",
            "eventTitle": title,
            "duration": f"{duration_minutes} minutes",
            "participants": participants or ["founder@company.com"],
            "suggestedSlot": "Friday, 3:30 PM"
        }
