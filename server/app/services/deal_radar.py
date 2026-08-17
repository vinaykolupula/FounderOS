"""
MEDDPICC Deal Health Radar & Sales Objection Coach (CRO / Head of Sales)

Based on Reforge Growth Loops and the MEDDPICC Enterprise Sales Methodology:
1. Audits deal health across 8 enterprise dimensions.
2. Identifies stalling risks (missing Economic Buyer, unclear Paper Process, weak Champion).
3. Generates high-conversion talk tracks and battlecards.
"""

from typing import Dict, Any, List, Optional
from app.services.llm import LLMEngine


class DealInspectionService:
    """
    Enterprise sales deal health audit and MEDDPICC scorecard engine.
    """

    @staticmethod
    def calculate_meddpicc_scorecard(
        metrics_defined: bool = True,
        has_economic_buyer: bool = False,
        decision_criteria_known: bool = True,
        decision_process_mapped: bool = False,
        paper_process_mapped: bool = False,
        pain_implicated: bool = True,
        has_champion: bool = True,
        competition_identified: bool = True
    ) -> Dict[str, Any]:
        """
        Calculates deterministic MEDDPICC health score and surfaces top risk flags.
        """
        criteria = [
            ("Metrics (ROI/Value)", metrics_defined, 15, "Quantify economic benefit (e.g. $ savings or hours saved) with the customer."),
            ("Economic Buyer", has_economic_buyer, 20, "Secure direct meeting with the budget holder before drafting proposal."),
            ("Decision Criteria", decision_criteria_known, 10, "Confirm technical and commercial evaluation checklist."),
            ("Decision Process", decision_process_mapped, 10, "Map every sign-off required between demo and signature."),
            ("Paper Process (Legal/Sec)", paper_process_mapped, 15, "Initiate infosec/procurement review early to prevent deal stalling."),
            ("Implicated Pain", pain_implicated, 10, "Tie product solution directly to active business pain."),
            ("Internal Champion", has_champion, 15, "Test champion strength: will they share internal deck/budget info?"),
            ("Competition", competition_identified, 5, "Define competitive differentiator vs status quo / in-house build.")
        ]

        total_score = sum(weight for _, status, weight, _ in criteria if status)
        gaps = [
            {"dimension": name, "risk": risk}
            for name, status, _, risk in criteria
            if not status
        ]

        verdict = (
            "HIGH CLOSE PROBABILITY (Strong MEDDPICC alignment)"
            if total_score >= 80 else
            "MODERATE RISK (Key decision makers or procurement unmapped)"
            if total_score >= 50 else
            "CRITICAL STALL RISK (Missing Economic Buyer or Champion)"
        )

        return {
            "healthScore": total_score,
            "maxScore": 100,
            "verdict": verdict,
            "identifiedGaps": gaps,
            "recommendedNextAction": gaps[0]["risk"] if gaps else "Proceed to contract draft and closing timeline."
        }

    @staticmethod
    async def generate_objection_response(
        objection: str,
        prospect_role: str = "VP of Engineering",
        product_value_prop: str = "Faster autonomous execution with security guardrails"
    ) -> Dict[str, Any]:
        """
        Generates tactical empathy and pivot responses (Chris Voss / MEDDPICC style).
        """
        system_prompt = """
        You are an elite enterprise sales mentor coaching a startup founder on handling tough objections.
        Use tactical empathy, calibrate questions, and pivot to business value without sounding defensive.
        
        Respond in JSON:
        {
            "objection": "String",
            "tacticalEmpathyOpening": "String validating their perspective",
            "probingQuestion": "Calibrated open-ended question to uncover underlying concern",
            "valuePivot": "Crisp talk track reframing around ROI or de-risking",
            "followUpEmailSnippet": "Short 3-sentence email draft to send prospect"
        }
        """
        prompt = f"Objection: '{objection}' from {prospect_role}. Our value prop: {product_value_prop}."

        try:
            llm_res = await LLMEngine.generate_completion(prompt, system_instruction=system_prompt, temperature=0.3)
            if llm_res:
                import json
                clean_json = llm_res.strip()
                if clean_json.startswith("```json"):
                    clean_json = clean_json[7:-3].strip()
                elif clean_json.startswith("```"):
                    clean_json = clean_json[3:-3].strip()
                return json.loads(clean_json)
        except Exception:
            pass

        return {
            "objection": objection,
            "tacticalEmpathyOpening": f"I completely understand why {objection.lower()} is top of mind for your team right now.",
            "probingQuestion": "What would a successful trial outcome need to demonstrate for this to be a clear win?",
            "valuePivot": f"Most leaders we work with felt the same initially, but found that {product_value_prop.lower()} removed this roadblock within the first 2 weeks.",
            "followUpEmailSnippet": f"Hi,\n\nThanks for sharing your thoughts on {objection.lower()}. We've seen similar teams address this by running a lightweight 2-week pilot. Would you be open to a 15-minute review of the benchmark results?\n\nBest,"
        }
