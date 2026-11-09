"""
Unit & Integration Tests for Phase 2: Agent Harness & Dialectic Upgrade

Tests:
1. Round 1 Independent C-Suite Stances (6 Personas with Startup Frameworks).
2. Round 2 Cross-Examination Dialectic Tension Pairs (Skeptic vs CTO, CFO vs CRO, VP CS vs COO).
3. Round 3 CEO Executive Synthesis (Consensus, OMTM, 2-Week MVE, Kill Criteria).
4. Real-Time Server-Sent Events (SSE) Streaming Generator and Endpoint.
5. High-Dimensional Subword Morphological Semantic Vectorizer in RAG.
"""

import unittest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlmodel import select
from app.main import app
from app.db import init_db, async_session_maker
from app.models import Workspace, CompanyProfile
from app.services.llm import LLMEngine
from app.rag import generate_semantic_embedding, cosine_similarity, rank_evidence_by_query


class TestDialecticDebateAndHarness(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        await init_db()
        async with async_session_maker() as session:
            # Clean up any leftover test data
            existing = await session.get(Workspace, 999)
            if existing:
                res = await session.execute(
                    select(CompanyProfile).where(CompanyProfile.workspace_id == 999)
                )
                for c in res.scalars().all():
                    await session.delete(c)
                await session.delete(existing)
                await session.commit()

            # Create fresh test workspace and company profile
            ws = Workspace(id=999, is_onboarded=True)
            session.add(ws)
            await session.commit()

            company = CompanyProfile(
                workspace_id=ws.id,
                name="SaaS Metrics Inc",
                stage="Early revenue",
                team_size="2-5 people",
                primary_metric="MRR Growth",
                objective="Accelerate enterprise expansion to $2M ARR",
                primary_constraint="Customer onboarding churn rate",
                runway_months=16,
                burn_rate="$35k/mo",
                gtm_motion="Sales-Led Growth",
                tech_stack="Python, React, PostgreSQL",
                competitive_moat="Proprietary analytics engine",
                ideal_customer="Mid-market B2B finance leaders"
            )
            session.add(company)
            await session.commit()

        self.workspace_id = 999
        self.company_context = {
            "objective": "Accelerate enterprise expansion to $2M ARR",
            "primaryConstraint": "Customer onboarding churn rate",
            "runwayFloor": "16 months",
            "burnRate": "$35k/mo",
            "gtmMotion": "Sales-Led Growth",
            "techStack": "Python, React, PostgreSQL",
            "competitiveMoat": "Proprietary analytics engine",
            "idealCustomer": "Mid-market B2B finance leaders"
        }

    async def test_2_round_dialectic_debate_structure(self):
        """HARNESS-01: Verifies 2-round dialectic generates stances, tension pairs, and CEO synthesis."""
        result = await LLMEngine.run_multi_agent_executive_debate(
            decision_title="Hire 3 Enterprise Account Executives",
            company_context=self.company_context
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["decisionTitle"], "Hire 3 Enterprise Account Executives")

        # Round 1: 6 Perspectives
        self.assertIn("executivePerspectives", result)
        perspectives = result["executivePerspectives"]
        self.assertEqual(len(perspectives), 6)
        lenses = [p["lens"] for p in perspectives]
        self.assertIn("Revenue & Growth (CRO)", lenses)
        self.assertIn("Product Risk (Skeptic)", lenses)
        self.assertIn("Customer Experience (VP CS)", lenses)
        self.assertIn("Capital & Strategy (CFO)", lenses)
        self.assertIn("Technical Architect (CTO)", lenses)
        self.assertIn("Operational Rigor (COO)", lenses)

        # Round 2: Dialectic Tension Critiques
        self.assertIn("dialecticCritiques", result)
        dialectics = result["dialecticCritiques"]
        self.assertEqual(len(dialectics), 3)

        pairs = [d["pair"] for d in dialectics]
        self.assertIn("Skeptic vs. CTO", pairs)
        self.assertIn("CFO vs. CRO", pairs)
        self.assertIn("VP CS vs. COO", pairs)

        for d in dialectics:
            self.assertIn("challenger", d)
            self.assertIn("defender", d)
            self.assertIn("critique", d)
            self.assertIn("rebuttal", d)
            self.assertIn("synthesis", d)
            self.assertTrue(len(d["critique"]) > 10)
            self.assertTrue(len(d["rebuttal"]) > 10)

        # Round 3: CEO Executive Synthesis
        self.assertIn("consensus", result)
        self.assertIn("decisionFramework", result)
        self.assertIn("keyTradeoff", result)
        self.assertIn("recommendedExperiment", result)
        self.assertIn("oneMetricThatMatters", result)
        self.assertIn("killCriteria", result)
        self.assertIn("confidence", result)

    async def test_stream_multi_agent_executive_debate_generator(self):
        """HARNESS-02: Verifies SSE async generator emits all debate phases in sequence."""
        events = []
        async for chunk in LLMEngine.stream_multi_agent_executive_debate(
            decision_title="Migrate database to Distributed Spanner",
            company_context=self.company_context
        ):
            events.append(chunk)

        event_names = [e["event"] for e in events]

        # Verify sequential event progression
        self.assertIn("round1_start", event_names)
        self.assertEqual(event_names.count("round1_persona"), 6)
        self.assertIn("round2_start", event_names)
        self.assertEqual(event_names.count("round2_dialectic"), 3)
        self.assertIn("round3_start", event_names)
        self.assertIn("debate_complete", event_names)

        # Verify complete payload in final event
        complete_event = next(e for e in events if e["event"] == "debate_complete")
        data = complete_event["data"]
        self.assertEqual(data["decisionTitle"], "Migrate database to Distributed Spanner")
        self.assertEqual(len(data["executivePerspectives"]), 6)
        self.assertEqual(len(data["dialecticCritiques"]), 3)
        self.assertTrue(bool(data["oneMetricThatMatters"]))
        self.assertTrue(bool(data["killCriteria"]))

    async def test_sse_debate_stream_api_endpoint(self):
        """HARNESS-02: Tests GET /api/debate/stream HTTP endpoint returning text/event-stream."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get(
                "/api/debate/stream",
                params={"decisionTitle": "Launch Self-Serve Developer Tier"},
                headers={"X-FounderOS-Key": "test-key"}
            )
            self.assertEqual(res.status_code, 200)
            self.assertIn("text/event-stream", res.headers.get("content-type", ""))
            
            body_text = res.text
            self.assertIn("event: round1_start", body_text)
            self.assertIn("event: round1_persona", body_text)
            self.assertIn("event: round2_start", body_text)
            self.assertIn("event: round2_dialectic", body_text)
            self.assertIn("event: round3_start", body_text)
            self.assertIn("event: debate_complete", body_text)

    def test_rag_semantic_subword_morphological_vectorizer(self):
        """HARNESS-03: Verifies 384-dimensional semantic subword embedding & cosine ranking."""
        vec1 = generate_semantic_embedding("Customer cancellation and churn rate in enterprise deals", dim=384)
        vec2 = generate_semantic_embedding("Reducing churn and customer attrition for B2B accounts", dim=384)
        vec3 = generate_semantic_embedding("Provisioning Kubernetes worker nodes in Frankfurt region", dim=384)

        self.assertEqual(len(vec1), 384)
        self.assertEqual(len(vec2), 384)
        self.assertEqual(len(vec3), 384)

        sim_related = cosine_similarity(vec1, vec2)
        sim_unrelated = cosine_similarity(vec1, vec3)

        # Morphologically related documents must have significantly higher similarity
        self.assertGreater(sim_related, sim_unrelated)
        self.assertGreater(sim_related, 0.25)
        self.assertLess(sim_unrelated, 0.15)

    def test_rank_evidence_by_query_semantic_ordering(self):
        """HARNESS-03: Verifies evidence items are ranked accurately by semantic query context."""
        evidence_items = [
            {"id": 1, "title": "Database maintenance", "content": "PostgreSQL vacuuming and WAL archiving."},
            {"id": 2, "title": "Customer churn feedback", "content": "Clients complaining about onboarding drop-off and attrition."},
            {"id": 3, "title": "Hiring plan", "content": "Interviewing candidates for marketing lead role."}
        ]

        ranked = rank_evidence_by_query("How can we reduce churn and retain customers?", evidence_items, top_k=2)
        self.assertEqual(len(ranked), 2)
        # Top result must be the customer churn feedback
        self.assertEqual(ranked[0]["id"], 2)


if __name__ == "__main__":
    unittest.main()
