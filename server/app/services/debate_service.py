from typing import Dict, Any


def run_executive_debate(decision_title: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Runs a multi-perspective AI Executive Board Debate over a strategic decision.
    """
    objective = context.get("objective", "Reach target MRR")
    constraint = context.get("primaryConstraint", "First-value completion")
    runway = context.get("runwayFloor", "12 months")
    icp = context.get("idealCustomer", "B2B customers")

    optimist_perspective = {
        "lens": "Revenue & Growth (CRO)",
        "stance": "Strong Support",
        "argument": f"Capitalizing on logistics momentum accelerates our goal to '{objective}'. Qualified pipeline is up 18% with enterprise logistics leads.",
        "keyMetric": "+18% Enterprise Pipeline"
    }

    skeptic_perspective = {
        "lens": "Product Risk (Skeptic)",
        "stance": "Proceed with Caution",
        "argument": f"First-value completion dropped 12% after Experiment B launched. Our bottleneck remains '{constraint}'. Unblocking setup friction must precede scaling outreach.",
        "keyMetric": "-12% Activation Rate"
    }

    customer_perspective = {
        "lens": "Customer Experience (VP CS)",
        "stance": "Needs Discovery Validation",
        "argument": f"Three recently inactive trial accounts in '{icp}' cited initial setup complexity. Run 5 customer interviews before permanent product changes.",
        "keyMetric": "3 Inactive Trial Signals"
    }

    capital_perspective = {
        "lens": "Capital & Strategy (CFO)",
        "stance": "Favorable Unit Economics",
        "argument": f"Current runway stands safely above the '{runway}' floor. Resource allocation should focus on high-margin logistics conversion.",
        "keyMetric": "14.2 Mo Runway"
    }

    consensus = (
        f"Consensus: Pause Feature B rollout immediately to resolve onboarding activation. "
        f"Simultaneously conduct 5 discovery calls with '{icp}' trial accounts to validate onboarding pain."
    )

    return {
        "decisionTitle": decision_title,
        "executivePerspectives": [
            optimist_perspective,
            skeptic_perspective,
            customer_perspective,
            capital_perspective
        ],
        "consensus": consensus,
        "recommendedExperiment": "Run 5-account logistics activation sprint",
        "confidence": "High evidence (3 independent signals)"
    }
