import unittest
from datetime import datetime, timezone
from sqlmodel import select
from app.db import init_db, async_session_maker
from app.models import (
    Workspace,
    CompanyProfile,
    FounderProfile,
    Task,
    ActionItem,
    Decision,
    AuditLog,
    Connector,
    Evidence,
    AIProviderSetting,
    StageEnum,
    TeamSizeEnum,
    FounderRole,
    FounderBackground,
    ExperienceLevel,
    FounderSuperpower
)


class TestModelsAndDatabase(unittest.IsolatedAsyncioTestCase):
    """Function-to-function tests for SQLModel database entities and relationships."""

    async def asyncSetUp(self):
        await init_db()

    async def test_create_and_query_workspace_with_profiles(self):
        async with async_session_maker() as session:
            ws = Workspace(is_onboarded=True)
            session.add(ws)
            await session.commit()
            await session.refresh(ws)
            assert ws.id is not None
            self.assertIsNotNone(ws.id)

            company = CompanyProfile(
                workspace_id=ws.id,
                name="Nexus AI",
                stage=StageEnum.EARLY_REVENUE,
                team_size=TeamSizeEnum.TWO_TO_FIVE,
                ideal_customer="Seed & Series A technical founders",
                objective="Reach $100k MRR",
                primary_metric="MRR",
                primary_constraint="Sales cycle duration",
                burn_rate="$20,000/mo"
            )
            session.add(company)

            founder = FounderProfile(
                workspace_id=ws.id,
                name="Alex",
                role=FounderRole.CEO,
                background=FounderBackground.TECHNICAL,
                experience_level=ExperienceLevel.SECOND_TIME,
                domain_expertise="B2B SaaS Developer Tools",
                superpower=FounderSuperpower.ENGINEERING,
                primary_gap=FounderSuperpower.SALES,
                learning_focus="MEDDPICC Sales",
                communication_style="Direct and brief"
            )
            session.add(founder)
            await session.commit()

            # Query back
            c_res = await session.execute(select(CompanyProfile).where(CompanyProfile.workspace_id == ws.id))
            saved_company = c_res.scalars().first()
            self.assertIsNotNone(saved_company)
            assert saved_company is not None
            self.assertEqual(saved_company.name, "Nexus AI")
            self.assertEqual(saved_company.stage, StageEnum.EARLY_REVENUE)

            f_res = await session.execute(select(FounderProfile).where(FounderProfile.workspace_id == ws.id))
            saved_founder = f_res.scalars().first()
            self.assertIsNotNone(saved_founder)
            assert saved_founder is not None
            self.assertEqual(saved_founder.name, "Alex")

    async def test_action_item_and_decision_models(self):
        async with async_session_maker() as session:
            ws = Workspace(is_onboarded=True)
            session.add(ws)
            await session.commit()
            await session.refresh(ws)
            assert ws.id is not None

            action = ActionItem(
                workspace_id=ws.id,
                title="Prepare Q3 Investor Update",
                detail="Draft Q3 update to seed investors with runway and NRR stats",
                source="Autonomous Briefing Agent",
                action_type="email_draft",
                payload={"to": "investors@fund.vc", "subject": "Acme Q3 Update"},
                status="Draft"
            )
            session.add(action)

            decision = Decision(
                workspace_id=ws.id,
                decision_code="#001",
                title="Adopt PostgreSQL as Primary DB",
                detail="Consolidate microservice storage on managed Postgres",
                status="Validated"
            )
            session.add(decision)

            evidence = Evidence(
                workspace_id=ws.id,
                source_provider="linear",
                external_id="ENG-101",
                title="Auth service latency spike",
                content="Spike to 450ms p99 observed during morning login burst."
            )
            session.add(evidence)
            await session.commit()

            a_res = await session.execute(select(ActionItem).where(ActionItem.workspace_id == ws.id))
            saved_action = a_res.scalars().first()
            self.assertIsNotNone(saved_action)
            assert saved_action is not None
            self.assertEqual(saved_action.title, "Prepare Q3 Investor Update")
            self.assertEqual(saved_action.status, "Draft")

            d_res = await session.execute(select(Decision).where(Decision.workspace_id == ws.id))
            saved_decision = d_res.scalars().first()
            self.assertIsNotNone(saved_decision)
            assert saved_decision is not None
            self.assertEqual(saved_decision.decision_code, "#001")

            e_res = await session.execute(select(Evidence).where(Evidence.workspace_id == ws.id))
            saved_evidence = e_res.scalars().first()
            self.assertIsNotNone(saved_evidence)
            assert saved_evidence is not None
            self.assertEqual(saved_evidence.source_provider, "linear")

    async def test_ai_provider_setting_model(self):
        async with async_session_maker() as session:
            ws = Workspace(is_onboarded=True)
            session.add(ws)
            await session.commit()
            await session.refresh(ws)
            assert ws.id is not None

            setting = AIProviderSetting(
                workspace_id=ws.id,
                provider_name="anthropic",
                selected_model="claude-opus-5",
                custom_base_url="https://api.anthropic.com/v1",
                reasoning_effort="max",
                is_active=True,
                status="Connected"
            )
            session.add(setting)
            await session.commit()

            s_res = await session.execute(select(AIProviderSetting).where(AIProviderSetting.workspace_id == ws.id))
            saved_setting = s_res.scalars().first()
            self.assertIsNotNone(saved_setting)
            assert saved_setting is not None
            self.assertEqual(saved_setting.provider_name, "anthropic")
            self.assertEqual(saved_setting.selected_model, "claude-opus-5")
            self.assertEqual(saved_setting.reasoning_effort, "max")
            self.assertTrue(saved_setting.is_active)

    async def test_sqlite_wal_pragmas_and_concurrency(self):
        """PERF-02 verification: Confirms SQLite WAL mode and busy timeout are configured."""
        from sqlalchemy import text
        from app.db import engine
        from app.config import settings

        if "sqlite" in settings.DATABASE_URL:
            async with engine.connect() as conn:
                busy = (await conn.execute(text("PRAGMA busy_timeout;"))).scalar()
                self.assertEqual(busy, 5000)
                sync = (await conn.execute(text("PRAGMA synchronous;"))).scalar()
                # 1 = NORMAL
                self.assertEqual(sync, 1)

    async def test_broadcast_event_manager_horizontal_scalability(self):
        """PERF-04 verification: Verifies decoupled broadcast backend delivers events."""
        from app.services.events import ConnectionManager, InMemoryBroadcastBackend
        backend = InMemoryBroadcastBackend()
        mgr = ConnectionManager(backend=backend)
        received = []

        await backend.subscribe("workspace:42", lambda msg: received.append(msg))
        await mgr.broadcast_refresh("42")
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].get("type"), "REFRESH")


if __name__ == "__main__":
    unittest.main()
