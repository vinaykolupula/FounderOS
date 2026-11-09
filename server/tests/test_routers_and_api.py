import unittest
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport
from sqlmodel import select
from app.main import app
from app.db import init_db, async_session_maker
from app.models import Connector, AIProviderSetting, Workspace


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

        # 2. Trigger C-Suite Executive Debate (deterministic mock to avoid unmocked external egress)
        debate_payload = {
            "decisionTitle": "Hire VP of Sales vs. Fractional CRO"
        }
        with patch("app.services.llm.LLMEngine.generate_completion", return_value="Dialectic synthesis: Hire Fractional CRO first."):
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
        with patch("app.services.llm.LLMEngine.generate_completion", return_value="Morning Briefing Executive Summary"):
            res = await self.client.get("/api/briefing")
        self.assertEqual(res.status_code, 200)
        brief_data = res.json()
        self.assertIn("executiveSummary", brief_data)
        self.assertIn("omtmStatus", brief_data)
        self.assertIn("topPriorityFocus", brief_data)

    async def test_oauth_google_csrf_state_protection(self):
        # 1. Get Login URL and extract state
        login_res = await self.client.get("/api/auth/google/login")
        self.assertEqual(login_res.status_code, 200)
        login_data = login_res.json()
        self.assertIn("state", login_data)
        self.assertIn("authUrl", login_data)
        valid_state = login_data["state"]

        # 2. Callback with missing or tampered state should fail with 400
        fail_res = await self.client.get("/api/auth/google/callback?code=mock_code_123&state=tampered_state")
        self.assertEqual(fail_res.status_code, 400)

        # 3. Callback with valid state should succeed and store token
        success_res = await self.client.get(f"/api/auth/google/callback?code=mock_code_123&state={valid_state}")
        self.assertEqual(success_res.status_code, 200)
        self.assertEqual(success_res.json().get("status"), "configured")

        # 4. BUG-01 Verification: Confirm encrypted_oauth_token was persisted in database
        async with async_session_maker() as session:
            ws_res = await session.execute(select(Workspace).order_by(Workspace.id.asc()))
            ws = ws_res.scalars().first()
            ws_id = ws.id if ws else 1
            conn_res = await session.execute(
                select(Connector).where(Connector.workspace_id == ws_id, Connector.connector_id == "gmail")
            )
            connector = conn_res.scalars().first()
            self.assertIsNotNone(connector)
            self.assertIsNotNone(connector.encrypted_oauth_token)
            self.assertTrue(len(connector.encrypted_oauth_token) > 20)

    async def test_reset_workspace_purges_all_credentials_and_providers(self):
        # 1. Ensure an AIProviderSetting exists (BUG-06 verification)
        async with async_session_maker() as session:
            ws_res = await session.execute(select(Workspace))
            ws = ws_res.scalars().first()
            if not ws:
                ws = Workspace(is_onboarded=True)
                session.add(ws)
                await session.commit()
                await session.refresh(ws)
            
            provider = AIProviderSetting(
                workspace_id=ws.id,
                provider_name="test_anthropic",
                selected_model="claude-3-5-sonnet",
                encrypted_api_key="mock_enc_key"
            )
            session.add(provider)
            await session.commit()

        # 2. Trigger DELETE /api/workspace
        res = await self.client.delete("/api/workspace")
        self.assertEqual(res.status_code, 200)

        # 3. Verify AIProviderSetting for this workspace is purged
        async with async_session_maker() as session:
            p_res = await session.execute(select(AIProviderSetting).where(AIProviderSetting.workspace_id == ws.id))
            providers = p_res.scalars().all()
            self.assertEqual(len(providers), 0)

    async def test_api_key_authentication_enforcement(self):
        from app.config import settings
        old_auth = settings.AUTH_ENABLED
        old_key = settings.FOUNDEROS_API_KEY
        try:
            settings.AUTH_ENABLED = True
            settings.FOUNDEROS_API_KEY = "faang-principal-test-key-999"

            # 1. Unauthenticated request should be rejected with 401
            unauth_res = await self.client.get("/api/workspace")
            self.assertEqual(unauth_res.status_code, 401)

            # 2. Authenticated request with X-FounderOS-Key should succeed
            auth_res = await self.client.get("/api/workspace", headers={"X-FounderOS-Key": "faang-principal-test-key-999"})
            self.assertEqual(auth_res.status_code, 200)

            # 3. Authenticated request with Bearer authorization should succeed
            bearer_res = await self.client.get("/api/workspace", headers={"Authorization": "Bearer faang-principal-test-key-999"})
            self.assertEqual(bearer_res.status_code, 200)
        finally:
            settings.AUTH_ENABLED = old_auth
            settings.FOUNDEROS_API_KEY = old_key


if __name__ == "__main__":
    unittest.main()
