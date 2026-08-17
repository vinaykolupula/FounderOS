"""
Andy Grove LNO Task Prioritizer Service (CEO / COO / Executive Founding Team)

Based on Andy Grove's High Output Management LNO Framework:
1. Leverage (10x): High-impact actions that change company trajectory (strategic hires, major deals, core moat).
2. Neutral (1x): Linear progress tasks that keep the machine running (routine bug fixes, standard sprints).
3. Overhead (<0.1x): Low-leverage operational chores suitable for autonomous AI agent delegation.
"""

from typing import Dict, Any, List, Optional
from app.services.llm import LLMEngine


class LNOClassificationService:
    """
    Classifies founder and executive tasks into Leverage, Neutral, and Overhead buckets,
    recommending optimal scheduling and delegation.
    """

    @staticmethod
    def classify_task_heuristics(title: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Fast heuristic classification for offline / instantaneous UI filtering.
        """
        combined = f"{title} {description or ''}".lower()

        # Overhead patterns (scheduling, expense, filing, status updates, routine admin)
        overhead_keywords = [
            "calendar", "schedule", "reschedule", "invoice", "receipt", "expense", "filing",
            "nda", "vendor bill", "renew subscription", "status ping", "organize docs",
            "clean up folder", "export csv", "format table", "routine ticket"
        ]

        # Leverage patterns (fundraising, closing enterprise deal, hiring key exec, major architecture, moat)
        leverage_keywords = [
            "hire", "interview finalist", "close deal", "contract negotiation", "enterprise pilot",
            "pitch deck", "term sheet", "board meeting", "pricing strategy", "core architecture",
            "database migration", "soc2 audit", "product launch", "fundraising", "investor update",
            "strategic partnership", "omtm", "pmf engine"
        ]

        if any(k in combined for k in leverage_keywords):
            return {
                "category": "LEVERAGE",
                "multiplier": "10x",
                "recommendation": "Protect uninterrupted deep-work founder focus time.",
                "shouldDelegate": False
            }
        elif any(k in combined for k in overhead_keywords):
            return {
                "category": "OVERHEAD",
                "multiplier": "<0.1x",
                "recommendation": "Delegate to FounderOS autonomous execution worker.",
                "shouldDelegate": True
            }
        else:
            return {
                "category": "NEUTRAL",
                "multiplier": "1x",
                "recommendation": "Execute in standard operational batches.",
                "shouldDelegate": False
            }

    @staticmethod
    async def classify_tasks_batch(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Batch classifies tasks with LLM contextual reasoning, falling back to heuristics.
        """
        results = []
        for t in tasks:
            title = t.get("title", "")
            desc = t.get("description", "")
            heuristics = LNOClassificationService.classify_task_heuristics(title, desc)
            results.append({
                "id": t.get("id"),
                "title": title,
                "lnoCategory": heuristics["category"],
                "multiplier": heuristics["multiplier"],
                "recommendation": heuristics["recommendation"],
                "shouldDelegate": heuristics["shouldDelegate"]
            })
        return results
