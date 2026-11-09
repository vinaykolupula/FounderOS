"""
Database Engine & Async Session Management

This module manages the asynchronous database connection pool, engine lifecycle, 
FastAPI session dependency injections, and default workspace seeding.
"""

from typing import AsyncGenerator
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel, select
from app.config import settings
from app.models import Workspace, CompanyProfile, FounderProfile, Connector, ActionItem, Decision

# 1. Create Async SQLAlchemy Engine with Concurrency Optimizations
if "sqlite" in settings.DATABASE_URL:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True,
        connect_args={"timeout": 30.0},
    )

    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=-64000")
        cursor.close()
else:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

# 2. Asynchronous Session Factory
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI Dependency Injector yielding an async database session per request.
    Automatically closes session upon request completion.
    """
    async with async_session_maker() as session:
        yield session


async def init_db():
    """
    Initializes database tables on application startup and seeds default workspace data 
    if the database is brand new.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Seed initial default workspace if database is empty
    async with async_session_maker() as session:
        result = await session.execute(select(Workspace))
        workspace = result.scalars().first()
        if not workspace:
            default_ws = Workspace(is_onboarded=False)
            session.add(default_ws)
            await session.commit()
            await session.refresh(default_ws)
            assert default_ws.id is not None

            # Initial default company profile
            company = CompanyProfile(
                workspace_id=default_ws.id,
                name="FounderOS",
                stage="Early revenue",
                team_size="2-5 people",
                ideal_customer="Mid-market logistics teams",
                objective="Reach $60k MRR with sustainable activation",
                primary_metric="Weekly activated accounts",
                primary_constraint="First-value completion",
                runway_months=12,
            )
            session.add(company)

            # Initial default founder profile
            founder = FounderProfile(
                workspace_id=default_ws.id,
                name="Vishwa",
                role="Solo Founder",
                background="Engineering / Technical",
                experience_level="First-time Founder",
                domain_expertise="SaaS",
                superpower="Building & Engineering",
                primary_gap="Sales & Closing Deals",
                learning_focus="GTM strategies",
            )
            session.add(founder)

            # Initial default system connectors
            connectors = [
                Connector(workspace_id=default_ws.id, connector_id="gmail", name="Google Workspace", description="Email and calendar signals", category="Communication"),
                Connector(workspace_id=default_ws.id, connector_id="slack", name="Slack", description="Team decisions and delivery context", category="Communication"),
                Connector(workspace_id=default_ws.id, connector_id="linear", name="Linear", description="Product and engineering execution", category="Product"),
                Connector(workspace_id=default_ws.id, connector_id="hubspot", name="HubSpot", description="Deals, pipeline, and customer history", category="Revenue"),
                Connector(workspace_id=default_ws.id, connector_id="stripe", name="Stripe", description="Revenue, subscriptions, and churn", category="Finance"),
            ]
            for c in connectors:
                session.add(c)

            await session.commit()
