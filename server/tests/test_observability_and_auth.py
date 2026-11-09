"""
Unit & Integration Tests for Enterprise Observability, Multi-Tenant Auth & Sandboxed Tool Execution

Tests:
1. PBKDF2 password hashing and verification.
2. HMAC-SHA256 JWT generation, decoding, tampering rejection, and expiration.
3. User registration, login, and `/api/auth/me` profile inspection.
4. Role-based access control (RBAC) dependency verification.
5. Real-time AI token ledger, cost calculations, and `/api/observability/usage` endpoint.
6. ExecutionSandbox environment scrubbing, command policy blocking, and timeout termination.
7. Redis pub/sub broadcast backend graceful fallback.
"""

import os
import unittest
import asyncio
from datetime import timedelta
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db import get_async_session, engine, init_db
from app.config import settings
from app.models import (
    User,
    UserRole,
    Workspace,
    TokenUsageLedger,
    CompanyProfile,
    Connector,
    AuditLog,
)
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    require_role
)
from app.policy.action_policy import ExecutionSandbox
from app.services.telemetry import estimate_cost, record_token_usage
from app.services.events import RedisBroadcastBackend, InMemoryBroadcastBackend
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession


class TestObservabilityAndAuth(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        await init_db()
        self.transport = ASGITransport(app=app)
        self.client = AsyncClient(transport=self.transport, base_url="http://test")

    async def asyncTearDown(self):
        await self.client.aclose()

    # ==========================================
    # 1. Password Hashing & JWT Tests
    # ==========================================

    def test_pbkdf2_password_hashing(self):
        password = "super-secret-founder-pass"
        hashed = hash_password(password)

        self.assertTrue(hashed.startswith("pbkdf2_sha256$100000$"))
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("wrong-password", hashed))
        self.assertFalse(verify_password("", hashed))

    def test_jwt_token_lifecycle(self):
        token = create_access_token(
            user_id=42,
            workspace_id=7,
            role=UserRole.OWNER,
            email="founder@unicorn.ai",
            expires_delta=timedelta(minutes=15)
        )
        self.assertIsInstance(token, str)
        self.assertEqual(len(token.split(".")), 3)

        payload = decode_access_token(token)
        self.assertEqual(payload["user_id"], 42)
        self.assertEqual(payload["workspace_id"], 7)
        self.assertEqual(payload["role"], UserRole.OWNER.value)
        self.assertEqual(payload["email"], "founder@unicorn.ai")

    def test_jwt_tamper_resistance(self):
        token = create_access_token(user_id=1, workspace_id=1, role=UserRole.MEMBER)
        parts = token.split(".")
        # Tamper with the signature
        tampered = f"{parts[0]}.{parts[1]}.tampered_sig"
        with self.assertRaises(Exception):
            decode_access_token(tampered)

    def test_jwt_expiration(self):
        # Create an already expired token (-10 seconds)
        expired_token = create_access_token(
            user_id=1,
            workspace_id=1,
            role=UserRole.OWNER,
            expires_delta=timedelta(seconds=-10)
        )
        with self.assertRaises(Exception):
            decode_access_token(expired_token)

    # ==========================================
    # 2. Auth Endpoints: Register, Login, Me
    # ==========================================

    async def test_user_registration_and_login_flow(self):
        test_email = f"test_{os.urandom(4).hex()}@founderos.io"
        test_pass = "secure_founder_pass_123"

        # 1. Register new tenant
        reg_res = await self.client.post("/api/auth/register", json={
            "email": test_email,
            "password": test_pass,
            "full_name": "Test Principal",
            "company_name": "Apex Quantum Labs"
        })
        self.assertEqual(reg_res.status_code, 201)
        reg_data = reg_res.json()
        self.assertIn("accessToken", reg_data)
        token = reg_data["accessToken"]
        self.assertEqual(reg_data["user"]["email"], test_email)
        self.assertEqual(reg_data["user"]["role"], UserRole.OWNER.value)
        workspace_id = reg_data["user"]["workspaceId"]

        # 2. Duplicate registration should fail
        dup_res = await self.client.post("/api/auth/register", json={
            "email": test_email,
            "password": "another_pass"
        })
        self.assertEqual(dup_res.status_code, 400)

        # 3. Login with credentials
        login_res = await self.client.post("/api/auth/login", json={
            "email": test_email,
            "password": test_pass
        })
        self.assertEqual(login_res.status_code, 200)
        login_data = login_res.json()
        self.assertIn("accessToken", login_data)

        # 4. Wrong password login fails
        bad_login = await self.client.post("/api/auth/login", json={
            "email": test_email,
            "password": "wrong_password"
        })
        self.assertEqual(bad_login.status_code, 401)

        # 5. Access /api/auth/me with Bearer token
        me_res = await self.client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(me_res.status_code, 200)
        me_data = me_res.json()
        self.assertEqual(me_data["email"], test_email)
        self.assertEqual(me_data["workspaceId"], workspace_id)

        # 6. Teardown test tenant to keep database pristine
        async with AsyncSession(engine) as cleanup_session:
            for model_cls in [User, CompanyProfile, Connector, AuditLog]:
                res = await cleanup_session.execute(
                    select(model_cls).where(model_cls.workspace_id == workspace_id)
                )
                for item in res.scalars().all():
                    await cleanup_session.delete(item)
            ws_to_del = await cleanup_session.get(Workspace, workspace_id)
            if ws_to_del:
                await cleanup_session.delete(ws_to_del)
            await cleanup_session.commit()

    # ==========================================
    # 3. RBAC Permission Guards
    # ==========================================

    async def test_rbac_role_guard(self):
        guard_owner_only = require_role([UserRole.OWNER])
        guard_admin_or_owner = require_role([UserRole.OWNER, UserRole.ADMIN])

        owner_user = User(
            id=10,
            workspace_id=1,
            email="owner@co.io",
            role=UserRole.OWNER.value,
            hashed_password=""
        )
        member_user = User(
            id=11,
            workspace_id=1,
            email="member@co.io",
            role=UserRole.MEMBER.value,
            hashed_password=""
        )

        # Owner passes owner-only guard
        res = await guard_owner_only(current_user=owner_user)
        self.assertEqual(res.id, 10)

        # Member fails owner-only guard with 403
        with self.assertRaises(Exception) as ctx:
            await guard_owner_only(current_user=member_user)
        self.assertIn("403", str(ctx.exception))

        # Member fails admin/owner guard
        with self.assertRaises(Exception):
            await guard_admin_or_owner(current_user=member_user)

    # ==========================================
    # 4. AI Telemetry & Observability
    # ==========================================

    def test_cost_estimation_catalog(self):
        # Anthropic Claude 3.5 Sonnet: $3 / MTok in, $15 / MTok out
        cost = estimate_cost("anthropic", "claude-3-5-sonnet", prompt_tokens=1_000_000, completion_tokens=1_000_000)
        self.assertAlmostEqual(cost, 18.0, places=2)

        # Groq llama-3.1-8b: $0.05 / MTok in, $0.08 / MTok out
        groq_cost = estimate_cost("groq", "llama-3.1-8b-instant", prompt_tokens=1_000_000, completion_tokens=1_000_000)
        self.assertAlmostEqual(groq_cost, 0.13, places=2)

    async def test_telemetry_recording_and_endpoint(self):
        async with AsyncSession(engine) as session:
            ws_res = await session.execute(select(Workspace))
            ws = ws_res.scalars().first()
            if not ws:
                ws = Workspace(is_onboarded=False)
                session.add(ws)
                await session.commit()
                await session.refresh(ws)
            ws_id = ws.id

        # Record telemetry events
        await record_token_usage(
            workspace_id=ws_id,
            provider="anthropic",
            model="claude-3-5-sonnet",
            call_type="debate_synthesis",
            prompt_tokens=500,
            completion_tokens=200,
            latency_ms=450.0
        )
        await record_token_usage(
            workspace_id=ws_id,
            provider="gemini",
            model="gemini-1.5-pro",
            call_type="briefing",
            prompt_tokens=800,
            completion_tokens=150,
            latency_ms=320.0
        )

        # Query GET /api/observability/usage
        usage_res = await self.client.get("/api/observability/usage?days=7")
        self.assertEqual(usage_res.status_code, 200)
        data = usage_res.json()
        self.assertGreaterEqual(data["totalTokens"], 1650)
        self.assertGreaterEqual(data["totalInferences"], 2)
        self.assertGreater(data["totalCostUsd"], 0.0)
        self.assertIn("anthropic", data["providerBreakdown"])
        self.assertIn("gemini", data["providerBreakdown"])

        # Query GET /api/observability/recent
        recent_res = await self.client.get("/api/observability/recent?limit=5")
        self.assertEqual(recent_res.status_code, 200)
        recent_list = recent_res.json()
        self.assertIsInstance(recent_list, list)
        self.assertGreaterEqual(len(recent_list), 2)

    # ==========================================
    # 5. Sandboxed Tool Execution Guard (SEC-07)
    # ==========================================

    def test_execution_sandbox_environment_scrubbing(self):
        # Set dummy secret environment variables in test process
        os.environ["AWS_SECRET_ACCESS_KEY"] = "AKIA_FAKE_SECRET_12345"
        os.environ["VAULT_MASTER_KEY"] = "super-secret-vault-key"
        os.environ["FOUNDEROS_API_KEY"] = "founder_test_key_abc"
        os.environ["DATABASE_URL"] = "postgres://root:password@db/founderos"

        scrubbed = ExecutionSandbox.sanitize_environment()

        # Secrets must NOT leak into scrubbed environment
        self.assertNotIn("AWS_SECRET_ACCESS_KEY", scrubbed)
        self.assertNotIn("VAULT_MASTER_KEY", scrubbed)
        self.assertNotIn("FOUNDEROS_API_KEY", scrubbed)
        self.assertNotIn("DATABASE_URL", scrubbed)

        # Safe environment variables must remain
        self.assertIn("PATH", scrubbed)

    async def test_execution_sandbox_command_run(self):
        res = await ExecutionSandbox.run_sandboxed_command(["echo", "founder_sandbox_alive"])
        self.assertTrue(res["success"])
        self.assertEqual(res["returncode"], 0)
        self.assertIn("founder_sandbox_alive", res["stdout"])
        self.assertFalse(res["timed_out"])

    async def test_execution_sandbox_policy_blocking(self):
        # Prohibited destructive command
        res = await ExecutionSandbox.run_sandboxed_command("dd if=/dev/zero of=/tmp/bomb")
        self.assertFalse(res["success"])
        self.assertEqual(res["policy_decision"], "deny")
        self.assertIn("denied by security policy", res["stderr"])

    async def test_execution_sandbox_timeout_enforcement(self):
        # Command sleeps 3 seconds with a 0.2 second timeout
        res = await ExecutionSandbox.run_sandboxed_command(["sleep", "3"], timeout=0.2)
        self.assertFalse(res["success"])
        self.assertTrue(res["timed_out"])
        self.assertIn("timed out", res["stderr"])

    # ==========================================
    # 6. Redis Pub/Sub Broadcast Fallback
    # ==========================================

    async def test_redis_broadcast_fallback(self):
        backend = RedisBroadcastBackend(redis_url="redis://localhost:9999/0")
        # Redis is not running on 9999, so it should gracefully fall back to in-memory
        received = []

        async def listener(msg):
            received.append(msg)

        await backend.subscribe("test-ch", listener)
        await backend.publish("test-ch", {"event": "TEST_BROADCAST"})
        await asyncio.sleep(0.05)

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]["event"], "TEST_BROADCAST")


if __name__ == "__main__":
    unittest.main()
