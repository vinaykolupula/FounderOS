import logging
import httpx
from typing import Dict, Any
from app.services.adapters import ActionPolicyEngine, LinearAdapter, GmailAdapter

logger = logging.getLogger("founderos.dispatchers")


from sqlalchemy.ext.asyncio import AsyncSession

class ActionDispatcher:
    @staticmethod
    async def dispatch_approved_action(action_id: int, title: str, detail: str, source: str, session: AsyncSession) -> Dict[str, Any]:
        """
        Executes an approved action by dispatching verified draft payloads
        to destination platforms (Linear, Gmail, Calendar).
        """
        logger.info(f"Dispatching approved action #{action_id}: {title}")

        # Check policy
        policy = await ActionPolicyEngine.evaluate_action_policy(source, {"title": title, "detail": detail, "action_id": action_id}, session)
        if not policy.get("allowed"):
            return {
                "success": False,
                "reason": policy.get("reason", "Action blocked by policy")
            }

        # Dispatch based on action type / source platform
        if "linear" in source.lower() or "engineering" in detail.lower() or "product" in detail.lower():
            payload = await LinearAdapter.create_draft_issue(title, detail)
            # Simulated Linear GraphQL dispatch
            dispatch_result = {
                "platform": "Linear",
                "status": "DISPATCHED",
                "issueId": f"ENG-{action_id + 100}",
                "issueUrl": payload["draftUrl"],
                "policyCheck": policy["policyCheck"]
            }
        elif "email" in source.lower() or "gmail" in source.lower() or "outreach" in detail.lower():
            payload = await GmailAdapter.create_draft_email("founderos-outreach@company.com", title, detail)
            dispatch_result = {
                "platform": "Gmail",
                "status": "DRAFT_CREATED",
                "draftId": payload["draftId"],
                "policyCheck": policy["policyCheck"]
            }
        else:
            dispatch_result = {
                "platform": "FounderOS Engine",
                "status": "QUEUED_FOR_EXECUTION",
                "actionId": action_id,
                "policyCheck": policy["policyCheck"]
            }

        logger.info(f"Action #{action_id} successfully dispatched: {dispatch_result}")
        return {
            "success": True,
            "receipt": dispatch_result
        }
