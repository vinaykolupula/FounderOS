import unittest
import asyncio
from app.db import init_db
from app.services.llm import LLMEngine


class TestLLMEngineAndHarness(unittest.IsolatedAsyncioTestCase):
    """Function-to-function tests for LLMEngine and the Peak 6-Agent C-Suite Executive Harness."""

    async def asyncSetUp(self):
        await init_db()

    async def test_get_active_provider_config_returns_dict(self):
        cfg = await LLMEngine.get_active_provider_config()
        self.assertIsInstance(cfg, dict)
        self.assertIn("provider", cfg)
        self.assertIn("model", cfg)
        self.assertIn("apiKey", cfg)

    async def test_generate_completion_without_api_key_returns_empty_or_local(self):
        res = await LLMEngine.generate_completion(
            prompt="Test prompt",
            provider="openai",
            api_key=""
        )
        self.assertEqual(res, "")

    async def test_run_multi_agent_executive_debate_offline_harness(self):
        company_context = {
            "name": "Acme AI",
            "objective": "Reach $1M ARR",
            "primaryConstraint": "Founder engineering bandwidth",
            "burnRate": "$15k/mo",
            "techStack": "FastAPI + React + PostgreSQL",
            "idealCustomer": "Seed & Series A technical founders",
            "gtmMotion": "Product-Led Growth (PLG)"
        }

        debate_result = await LLMEngine.run_multi_agent_executive_debate(
            decision_title="Migrate infrastructure to Kubernetes",
            company_context=company_context
        )

        self.assertIsInstance(debate_result, dict)
        self.assertIn("executivePerspectives", debate_result)
        self.assertIn("consensus", debate_result)
        self.assertIn("keyTradeoff", debate_result)
        self.assertIn("recommendedExperiment", debate_result)

        perspectives = debate_result["executivePerspectives"]
        self.assertEqual(len(perspectives), 6)

        lenses = [p["lens"] for p in perspectives]
        self.assertIn("Revenue & Growth (CRO)", lenses)
        self.assertIn("Product Risk (Skeptic)", lenses)
        self.assertIn("Customer Experience (VP CS)", lenses)
        self.assertIn("Capital & Strategy (CFO)", lenses)
        self.assertIn("Technical Architect (CTO)", lenses)
        self.assertIn("Operational Rigor (COO)", lenses)

        for p in perspectives:
            self.assertIn("stance", p)
            self.assertIn("argument", p)
            self.assertIn("keyMetric", p)
            self.assertIn("mentalModel", p)
            self.assertTrue(len(p["argument"]) > 10)

        self.assertIn(debate_result["consensus"], ["GO", "CONDITIONAL GO", "NO-GO", "PIVOT EXPERIMENT"])


if __name__ == "__main__":
    unittest.main()
