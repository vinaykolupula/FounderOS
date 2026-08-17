"""
Runway & Scenario Lab Service (CFO / Finance Lead / Paul Graham Framework)

Implements Paul Graham's 'Default Alive vs Default Dead' framework and capital efficiency metrics:
1. Calculates dynamic runway months, net burn, and Default Alive trajectory.
2. Computes the minimum monthly revenue growth rate ($g$) required to reach cash-flow break-even before running out of money.
3. Provides interactive What-If scenario simulations (new hires, pricing changes, vendor spend adjustments).
"""

import math
from typing import Dict, Any, List, Optional


class RunwayScenarioService:
    """
    Financial runway modeling and scenario forecasting engine.
    """

    @staticmethod
    def calculate_default_alive_status(
        cash_balance: float,
        monthly_burn: float,
        monthly_revenue: float,
        mom_growth_rate: float = 0.05
    ) -> Dict[str, Any]:
        """
        Calculates Default Alive vs. Default Dead status and growth curve.
        """
        if cash_balance <= 0:
            return {
                "status": "DEFAULT_DEAD",
                "runwayMonths": 0.0,
                "monthsToBreakEven": None,
                "requiredMonthlyGrowth": None,
                "isDefaultAlive": False,
                "verdict": "Critical: Company has exhausted immediate cash reserves."
            }

        net_burn = max(0.0, monthly_burn - monthly_revenue)
        if net_burn <= 0:
            return {
                "status": "PROFITABLE",
                "runwayMonths": 999.0,
                "monthsToBreakEven": 0,
                "requiredMonthlyGrowth": 0.0,
                "isDefaultAlive": True,
                "verdict": "Default Alive: The company is already cash flow positive / self-sustaining."
            }

        simple_runway = cash_balance / net_burn

        # Simulate month-by-month trajectory with revenue growth
        simulated_cash = cash_balance
        simulated_rev = monthly_revenue
        break_even_month = None
        is_alive = False

        for month in range(1, 121):  # 10-year max projection
            simulated_rev *= (1 + mom_growth_rate)
            month_burn = max(0.0, monthly_burn - simulated_rev)
            simulated_cash -= month_burn

            if simulated_rev >= monthly_burn and break_even_month is None:
                break_even_month = month
                is_alive = True

            if simulated_cash <= 0:
                break

        # Calculate required growth rate for default alive if currently dead
        required_growth = 0.0
        if not is_alive:
            # Binary search for minimum required MoM growth
            low = 0.0
            high = 2.0
            for _ in range(30):
                mid = (low + high) / 2
                test_cash = cash_balance
                test_rev = monthly_revenue
                survived = False
                for m in range(1, 121):
                    test_rev *= (1 + mid)
                    b = max(0.0, monthly_burn - test_rev)
                    test_cash -= b
                    if test_rev >= monthly_burn:
                        survived = True
                        break
                    if test_cash <= 0:
                        break
                if survived:
                    high = mid
                    required_growth = mid
                else:
                    low = mid

        status = "DEFAULT_ALIVE" if is_alive else "DEFAULT_DEAD"
        verdict = (
            f"Default Alive: At {mom_growth_rate*100:.1f}% MoM growth, you reach profitability in {break_even_month} months with cash remaining."
            if is_alive else
            f"Default Dead: At current {mom_growth_rate*100:.1f}% growth, cash runs out in {simple_runway:.1f} months before reaching profitability. Required MoM growth is {required_growth*100:.1f}%."
        )

        return {
            "status": status,
            "runwayMonths": round(simple_runway, 1),
            "monthsToBreakEven": break_even_month,
            "currentMomGrowthPct": round(mom_growth_rate * 100, 1),
            "requiredMonthlyGrowthPct": round(required_growth * 100, 1) if not is_alive else 0.0,
            "isDefaultAlive": is_alive,
            "verdict": verdict
        }

    @staticmethod
    def simulate_scenario(
        base_cash: float,
        base_monthly_burn: float,
        base_monthly_rev: float,
        base_growth_rate: float,
        headcount_delta: int = 0,
        avg_annual_salary: float = 140000.0,
        rev_growth_delta_pct: float = 0.0,
        monthly_tooling_spend_delta: float = 0.0
    ) -> Dict[str, Any]:
        """
        Runs an interactive What-If scenario adjusting headcount, growth rate, and SaaS spend.
        """
        new_monthly_burn = base_monthly_burn + (headcount_delta * (avg_annual_salary / 12.0)) + monthly_tooling_spend_delta
        new_growth_rate = max(0.0, base_growth_rate + (rev_growth_delta_pct / 100.0))

        base_res = RunwayScenarioService.calculate_default_alive_status(
            base_cash, base_monthly_burn, base_monthly_rev, base_growth_rate
        )

        scenario_res = RunwayScenarioService.calculate_default_alive_status(
            base_cash, new_monthly_burn, base_monthly_rev, new_growth_rate
        )

        runway_diff = round(scenario_res["runwayMonths"] - base_res["runwayMonths"], 1)

        return {
            "baseline": base_res,
            "scenario": scenario_res,
            "impact": {
                "runwayMonthsDelta": runway_diff,
                "burnDelta": round(new_monthly_burn - base_monthly_burn, 2),
                "growthRateDeltaPct": round(rev_growth_delta_pct, 1),
                "summary": f"{'Gained' if runway_diff > 0 else 'Lost'} {abs(runway_diff)} months of runway in this scenario."
            }
        }
