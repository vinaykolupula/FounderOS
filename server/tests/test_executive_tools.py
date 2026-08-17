import unittest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db import init_db, async_session_maker
from app.models import (
    Workspace,
    CompanyProfile,
    FounderProfile,
    Task,
    StageEnum,
    TeamSizeEnum,
    FounderRole,
    FounderBackground,
    ExperienceLevel,
    FounderSuperpower
)
from app.services.investor_update import InvestorUpdateService
from app.services.lno_prioritizer import LNOClassificationService
from app.services.runway_lab import RunwayScenarioService
from app.services.technical_rfc import TechnicalRfcService
from app.services.deal_radar import DealInspectionService
from app.services.pmf_engine import PMFEngineService


class TestExecutiveTools(unittest.IsolatedAsyncioTestCase):
    """Function-to-function tests for C-Suite Daily Executive Operating Tools."""

    async def asyncSetUp(self):
        await init_db()
        self.transport = ASGITransport(app=app)
        self.client = AsyncClient(transport=self.transport, base_url="http://testserver")

    async def asyncTearDown(self):
        await self.client.aclose()

    def test_lno_prioritizer_heuristics(self):
        lev = LNOClassificationService.classify_task_heuristics("Close Enterprise Pilot with Datadog")
        self.assertEqual(lev["category"], "LEVERAGE")
        self.assertEqual(lev["multiplier"], "10x")
        self.assertFalse(lev["shouldDelegate"])

        over = LNOClassificationService.classify_task_heuristics("Schedule calendar meeting and file expense receipt")
        self.assertEqual(over["category"], "OVERHEAD")
        self.assertEqual(over["multiplier"], "<0.1x")
        self.assertTrue(over["shouldDelegate"])

        neut = LNOClassificationService.classify_task_heuristics("Update weekly telemetry dashboard query")
        self.assertEqual(neut["category"], "NEUTRAL")
        self.assertEqual(neut["multiplier"], "1x")

    def test_runway_default_alive_calculator(self):
        # 1. Default Alive scenario
        res_alive = RunwayScenarioService.calculate_default_alive_status(
            cash_balance=500000.0,
            monthly_burn=30000.0,
            monthly_revenue=20000.0,
            mom_growth_rate=0.10
        )
        self.assertEqual(res_alive["status"], "DEFAULT_ALIVE")
        self.assertTrue(res_alive["isDefaultAlive"])
        self.assertIsNotNone(res_alive["monthsToBreakEven"])

        # 2. Default Dead scenario (low growth, high burn)
        res_dead = RunwayScenarioService.calculate_default_alive_status(
            cash_balance=100000.0,
            monthly_burn=50000.0,
            monthly_revenue=2000.0,
            mom_growth_rate=0.01
        )
        self.assertEqual(res_dead["status"], "DEFAULT_DEAD")
        self.assertFalse(res_dead["isDefaultAlive"])
        self.assertGreater(res_dead["requiredMonthlyGrowthPct"], 0.0)

    def test_runway_what_if_scenario_simulation(self):
        sim = RunwayScenarioService.simulate_scenario(
            base_cash=500000.0,
            base_monthly_burn=30000.0,
            base_monthly_rev=10000.0,
            base_growth_rate=0.05,
            headcount_delta=2,
            avg_annual_salary=120000.0
        )
        self.assertIn("baseline", sim)
        self.assertIn("scenario", sim)
        self.assertIn("impact", sim)
        self.assertLess(sim["scenario"]["runwayMonths"], sim["baseline"]["runwayMonths"])

    def test_meddpicc_deal_health_radar(self):
        strong_deal = DealInspectionService.calculate_meddpicc_scorecard(
            metrics_defined=True,
            has_economic_buyer=True,
            decision_criteria_known=True,
            decision_process_mapped=True,
            paper_process_mapped=True,
            pain_implicated=True,
            has_champion=True,
            competition_identified=True
        )
        self.assertEqual(strong_deal["healthScore"], 100)
        self.assertIn("HIGH CLOSE", strong_deal["verdict"])
        self.assertEqual(len(strong_deal["identifiedGaps"]), 0)

        stalled_deal = DealInspectionService.calculate_meddpicc_scorecard(
            metrics_defined=True,
            has_economic_buyer=False,  # Missing EB (-20)
            decision_criteria_known=True,
            decision_process_mapped=False, # Missing DP (-10)
            paper_process_mapped=False,   # Missing PP (-15)
            pain_implicated=True,
            has_champion=False,           # Missing C (-15)
            competition_identified=True
        )
        self.assertLess(stalled_deal["healthScore"], 50)
        self.assertIn("CRITICAL STALL", stalled_deal["verdict"])
        self.assertGreaterEqual(len(stalled_deal["identifiedGaps"]), 3)

    def test_superhuman_pmf_score_calculator(self):
        # 50 very disappointed, 30 somewhat, 20 not => 50% PMF (>40%)
        res_strong = PMFEngineService.calculate_pmf_score(50, 30, 20)
        self.assertEqual(res_strong["pmfScorePct"], 50.0)
        self.assertTrue(res_strong["hasPmf"])

        # 10 very disappointed, 50 somewhat, 40 not => 10% PMF (<40%)
        res_weak = PMFEngineService.calculate_pmf_score(10, 50, 40)
        self.assertEqual(res_weak["pmfScorePct"], 10.0)
        self.assertFalse(res_weak["hasPmf"])

    async def test_investor_update_generator_service(self):
        async with async_session_maker() as session:
            ws = Workspace(is_onboarded=True)
            session.add(ws)
            await session.commit()
            await session.refresh(ws)
            assert ws.id is not None

            company = CompanyProfile(
                workspace_id=ws.id,
                name="AeroDynamics",
                stage=StageEnum.EARLY_REVENUE,
                team_size=TeamSizeEnum.TWO_TO_FIVE,
                ideal_customer="Drone delivery operators",
                objective="Deploy 50 active routes",
                primary_metric="Completed Routes",
                primary_constraint="Battery turnaround cycle",
                burn_rate="$30k/mo"
            )
            session.add(company)

            founder = FounderProfile(
                workspace_id=ws.id,
                name="Ravi",
                role=FounderRole.CEO,
                background=FounderBackground.TECHNICAL,
                experience_level=ExperienceLevel.FIRST_TIME,
                domain_expertise="Robotics",
                superpower=FounderSuperpower.ENGINEERING,
                primary_gap=FounderSuperpower.SALES,
                learning_focus="Enterprise Procurement",
                communication_style="Direct and brief"
            )
            session.add(founder)

            task = Task(
                workspace_id=ws.id,
                title="Completed 50-mile flight range battery telemetry test",
                status="COMPLETED"
            )
            session.add(task)
            await session.commit()

            update = await InvestorUpdateService.generate_investor_update(session, ws.id)
            self.assertIn("subjectLine", update)
            self.assertIn("highlights", update)
            self.assertIn("fullMarkdown", update)
            self.assertIn("AeroDynamics", update["fullMarkdown"])

    async def test_executive_tools_api_endpoints(self):
        # 1. Test Runway Analysis API
        runway_res = await self.client.post("/api/executive-tools/finance/runway-analysis", json={
            "cashBalance": 400000.0,
            "monthlyBurn": 25000.0,
            "monthlyRevenue": 15000.0,
            "momGrowthRate": 0.08
        })
        self.assertEqual(runway_res.status_code, 200)
        self.assertIn("runwayMonths", runway_res.json())

        # 2. Test Scenario Simulation API
        sim_res = await self.client.post("/api/executive-tools/finance/simulate-scenario", json={
            "cashBalance": 400000.0,
            "monthlyBurn": 25000.0,
            "monthlyRevenue": 15000.0,
            "momGrowthRate": 0.08,
            "headcountDelta": 1,
            "avgAnnualSalary": 130000.0,
            "revGrowthDeltaPct": 2.0,
            "monthlyToolingSpendDelta": 500.0
        })
        self.assertEqual(sim_res.status_code, 200)
        self.assertIn("impact", sim_res.json())

        # 3. Test Gary Klein Pre-Mortem API
        pm_res = await self.client.post("/api/executive-tools/technical/pre-mortem", json={
            "proposalTitle": "Migrate from monolithic SQLite to distributed Spanner",
            "technicalScope": "Replace local state with multi-region Spanner cluster",
            "techStack": "FastAPI + React",
            "primaryConstraint": "2-person engineering team"
        })
        self.assertEqual(pm_res.status_code, 200)
        pm_data = pm_res.json()
        self.assertIn("topFailureModes", pm_data)
        self.assertIn("reversibilityAssessment", pm_data)

        # 4. Test MEDDPICC Deal Audit API
        deal_res = await self.client.post("/api/executive-tools/sales/meddpicc-audit", json={
            "metricsDefined": True,
            "hasEconomicBuyer": True,
            "decisionCriteriaKnown": True,
            "decisionProcessMapped": True,
            "paperProcessMapped": False,
            "painImplicated": True,
            "hasChampion": True,
            "competitionIdentified": True
        })
        self.assertEqual(deal_res.status_code, 200)
        deal_data = deal_res.json()
        self.assertEqual(deal_data["healthScore"], 85)

        # 5. Test Superhuman PMF Score API
        pmf_res = await self.client.post("/api/executive-tools/product/pmf-score", json={
            "veryDisappointedCount": 42,
            "somewhatDisappointedCount": 38,
            "notDisappointedCount": 20
        })
        self.assertEqual(pmf_res.status_code, 200)
        pmf_data = pmf_res.json()
        self.assertEqual(pmf_data["pmfScorePct"], 42.0)
        self.assertTrue(pmf_data["hasPmf"])


if __name__ == "__main__":
    unittest.main()
