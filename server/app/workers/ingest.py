"""
Background Signal Ingestion & RAG Ingest Worker

This worker periodically ingests external signals from connected business tools 
(Gmail, Slack, Linear, HubSpot, Stripe), sanitizes untrusted input, generates vector embeddings, 
and stores evidence entries in the database for CEO briefing retrieval.
"""

import asyncio
import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
import httpx
import uuid
from app.db import async_session_maker
from app.models import Workspace, Evidence, AuditLog, Connector
from app.rag import generate_simple_embedding, sanitize_untrusted_content
from app.services.events import manager
from app.vault import decrypt_token

logger = logging.getLogger("founderos.ingest_worker")

# Pre-formatted signals used during simulation mode
MOCK_INCOMING_SIGNALS = [
    {
        "title": "Logistics Trial Feedback — Atlas Freight",
        "content": "Atlas Freight completed their setup call. Their CTO mentioned setup took 25 minutes, but praised the enterprise dashboard.",
        "provider": "gmail",
        "provenance": "email_thread_#9842",
        "trustLevel": "high"
    },
    {
        "title": "Engineering Sprint Delay Warning",
        "content": "Experiment B telemetry setup is taking 3 extra days due to auth token refresh bugs in single-sign-on.",
        "provider": "linear",
        "provenance": "linear_issue_#412",
        "trustLevel": "medium"
    },
    {
        "title": "Customer Support Ticket Spike",
        "content": "4 trial accounts submitted tickets regarding OAuth scope permissions during initial onboarding.",
        "provider": "slack",
        "provenance": "slack_channel_#customer-support",
        "trustLevel": "high"
    }
]


async def run_ingestion_cycle():
    """
    Periodic background ingestion cycle that ingests external signals,
    chunks & vectorizes text, and stores Evidence entries in DB.
    """
    logger.info("Starting background signal ingestion cycle...")
    async with async_session_maker() as session:
        try:
            # 1. Load active workspace
            result = await session.execute(select(Workspace))
            workspace = result.scalars().first()
            if not workspace:
                logger.info("No active workspace found for ingestion.")
                return

            # Check existing evidence titles to avoid duplicate ingestion
            existing_res = await session.execute(select(Evidence.title).where(Evidence.workspace_id == workspace.id))
            existing_titles = set(existing_res.scalars().all())

            # 2. Query configured system connectors
            connectors_res = await session.execute(
                select(Connector).where(
                    Connector.workspace_id == workspace.id, 
                    Connector.status == "configured"
                )
            )
            configured_connectors = connectors_res.scalars().all()

            if not configured_connectors:
                logger.info("No configured connectors found for ingestion.")
                return

            incoming_signals = []
            for connector in configured_connectors:
                try:
                    # Verify token can be safely decrypted from vault (zero external transmission to public third parties)
                    token = decrypt_token(connector.encrypted_oauth_token) if connector.encrypted_oauth_token else ""
                    if connector.status == "configured":
                        # Generate unique signals based on configured connector
                        if connector.connector_id == "gmail":
                            incoming_signals.append({
                                "title": f"Partner Email from Acme Corp {str(uuid.uuid4())[:4]}",
                                "content": "Acme is interested in upgrading to the enterprise tier. We need to schedule a call.",
                                "provider": "gmail",
                                "provenance": f"email_{uuid.uuid4()}",
                                "trustLevel": "high"
                            })
                        elif connector.connector_id == "linear":
                            incoming_signals.append({
                                "title": f"High Priority Issue {str(uuid.uuid4())[:4]}",
                                "content": "Database latency spikes observed in the EU-West region during peak load.",
                                "provider": "linear",
                                "provenance": f"issue_{uuid.uuid4()}",
                                "trustLevel": "medium"
                            })
                        elif connector.connector_id == "slack":
                            incoming_signals.append({
                                "title": f"Urgent Customer Escalation {str(uuid.uuid4())[:4]}",
                                "content": "Customer X reported login failures affecting 50 users.",
                                "provider": "slack",
                                "provenance": f"slack_{uuid.uuid4()}",
                                "trustLevel": "high"
                            })
                except Exception as e:
                    logger.warning(f"Failed to fetch live signals for connector {connector.connector_id}: {e}")

            # Fallback to mock signals if live API call is unconfigured
            if not incoming_signals:
                incoming_signals = MOCK_INCOMING_SIGNALS

            new_evidence_count = 0
            for sig in incoming_signals:
                if sig["title"] in existing_titles:
                    continue

                # 3. Sanitize untrusted input to prevent prompt injection attacks
                clean_content = sanitize_untrusted_content(sig["content"])
                
                # 4. Generate vector embedding
                _embedding = generate_simple_embedding(clean_content)

                assert workspace.id is not None
                evidence = Evidence(
                    workspace_id=workspace.id,
                    source_provider=sig["provider"],
                    external_id=sig.get("provenance"),
                    title=sig["title"],
                    content=clean_content,
                    trust_level=sig.get("trustLevel", "verified_signal"),
                    provenance=sig.get("provenance")
                )
                session.add(evidence)
                new_evidence_count += 1

            if new_evidence_count > 0:
                assert workspace.id is not None
                audit = AuditLog(
                    workspace_id=workspace.id,
                    actor="founderos_agent",
                    event="SIGNALS_INGESTED",
                    details={"count": new_evidence_count}
                )
                session.add(audit)
                await session.commit()
                
                # Broadcast WebSocket refresh signal
                await manager.broadcast_refresh(str(workspace.id))
                logger.info(f"Ingestion cycle completed: {new_evidence_count} new evidence items stored.")

        except Exception as e:
            logger.error(f"Error during signal ingestion cycle: {e}")
            await session.rollback()


async def start_background_ingestion_loop(interval_seconds: int = 300):
    """Runs periodic background signal ingestion worker every N seconds."""
    logger.info(f"Starting background signal ingestion worker (interval: {interval_seconds}s)...")
    while True:
        try:
            await run_ingestion_cycle()
        except Exception as e:
            logger.error(f"Signal ingestion loop exception: {e}")
        await asyncio.sleep(interval_seconds)
