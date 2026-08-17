import unittest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db import init_db


class TestRoutersAndApi(unittest.IsolatedAsyncioTestCase):
    """Function-to-function API integration tests for all FastAPI endpoints."""

    async def asyncSetUp(self):
        await init_db()
        self.transport = ASGITransport(app=app)
        self.client = AsyncClient(transport=self.transport, base_url="http://testserver")

    async def asyncTearDown(self):
        await self.client.aclose()

    async def test_health_check_endpoint(self):
        res = await self.client.get("/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("status"), "healthy")

    async def test_workspace_onboarding_and_fetch(self):
        onboarding_payload = {
            "company": {
                "name": "CloudFleet",
                "stage": "Early revenue",
                "teamSize": "2-5 people",
                "idealCustomer": "DevOps Engineers",
                "objective": "Scale to 100 enterprise clusters",
                "primaryMetric": "Active Nodes",
                "primaryConstraint": "Sales cycle",
                "burnRate": "$25,000/mo",
                "gtmMotion": "Product-Led Growth",
                "techStack": "Go, React, Kubernetes",
                "competitiveMoat": "Kernel-level optimization",
                "runwayMonths": 18
            },
            "founder": {
                "name": "David",
                "role": "CEO",
                "background": "Engineering / Technical",
                "experienceLevel": "Second-time Founder",
                "domainExpertise": "Cloud Infrastructure",
                "superpower": "Building & Engineering",
                "primaryGap": "Sales & Closing Deals",
                "learningFocus": "Enterprise Sales",
                "communicationStyle": "Direct and brief",
                "energyState": "Steady pace",
                "coreValues": "Reliability, Speed"
            },
            "selectedConnectors": ["gmail", "linear"]
        }

        # 1. Submit Onboarding
        post_res = await self.client.post("/api/onboarding", json=onboarding_payload)
        self.assertEqual(post_res.status_code, 200)

        # 2. Fetch Workspace
        get_res = await self.client.get("/api/workspace")
        self.assertEqual(get_res.status_code, 200)
        ws_data = get_res.json()
        self.assertTrue(ws_data.get("isOnboarded"))
        self.assertEqual(ws_data.get("company", {}).get("name"), "CloudFleet")
        self.assertEqual(ws_data.get("founder", {}).get("name"), "David")

    async def test_tasks_crud_and_delegation(self):
        # 1. Create task
        task_payload = {
            "title": "Evaluate SOC2 Type II auditor proposals",
            "priority": "P1_HIGH",
            "category": "TODAY",
            "source": "FOUNDER_MANUAL"
        }
        create_res = await self.client.post("/api/tasks", json=task_payload)
        self.assertEqual(create_res.status_code, 200)
        task_data = create_res.json()
        task_id = task_data.get("id")
        self.assertIsNotNone(task_id)

        # 2. Fetch tasks list
        list_res = await self.client.get("/api/tasks")
        self.assertEqual(list_res.status_code, 200)
        tasks = list_res.json()
        self.assertTrue(any(t["id"] == task_id for t in tasks))

        # 3. Delegate task to AI agent
        del_res = await self.client.post(f"/api/tasks/{task_id}/delegate")
        self.assertEqual(del_res.status_code, 200)
        del_data = del_res.json()
        self.assertEqual(del_data.get("status"), "DELEGATED")

    async def test_decisions_and_debate_endpoint(self):
        # 1. Create Decision
        dec_payload = {
            "title": "Hire VP of Sales vs. Fractional CRO",
            "detail": "Need to accelerate enterprise outbound to hit $1M ARR milestone.",
            "decisionCode": "#099"
        }
        create_res = await self.client.post("/api/decisions", json=dec_payload)
        self.assertEqual(create_res.status_code, 200)
        saved_decision = create_res.json()
        self.assertIn("message", saved_decision)

        # 2. Trigger C-Suite Executive Debate
        debate_payload = {
            "decisionTitle": "Hire VP of Sales vs. Fractional CRO"
        }
        debate_res = await self.client.post("/api/debate", json=debate_payload)
        self.assertEqual(debate_res.status_code, 200)
        debate_data = debate_res.json()
        self.assertIn("executivePerspectives", debate_data)
        self.assertEqual(len(debate_data["executivePerspectives"]), 6)
        self.assertIn("consensus", debate_data)

    async def test_ai_model_settings_and_discovery(self):
        # 1. Fetch AI Model settings & catalog
        get_res = await self.client.get("/api/settings/models")
        self.assertEqual(get_res.status_code, 200)
        models_data = get_res.json()
        self.assertIn("supportedProviders", models_data)
        self.assertGreaterEqual(len(models_data["supportedProviders"]), 12)

        # 2. Save Anthropic model settings
        save_payload = {
            "providerName": "anthropic",
            "selectedModel": "claude-opus-5",
            "apiKey": "sk-ant-api03-test-mock-key-12345",
            "customBaseUrl": "https://api.anthropic.com/v1",
            "reasoningEffort": "max",
            "isActive": True
        }
        save_res = await self.client.post("/api/settings/models", json=save_payload)
        self.assertEqual(save_res.status_code, 200)

        # 3. Discover models endpoint
        disc_payload = {
            "providerName": "anthropic",
            "apiKey": "",
            "customBaseUrl": "https://api.anthropic.com/v1"
        }
        disc_res = await self.client.post("/api/settings/models/discover", json=disc_payload)
        self.assertEqual(disc_res.status_code, 200)
        disc_data = disc_res.json()
        self.assertIn("models", disc_data)
        self.assertIn("claude-opus-5", disc_data["models"])

    async def test_executive_morning_briefing_endpoint(self):
        res = await self.client.get("/api/briefing")
        self.assertEqual(res.status_code, 200)
        brief_data = res.json()
        self.assertIn("executiveSummary", brief_data)
        self.assertIn("omtmStatus", brief_data)
        self.assertIn("topPriorityFocus", brief_data)


if __name__ == "__main__":
    unittest.main()
