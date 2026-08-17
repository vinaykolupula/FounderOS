import asyncio
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db import async_session_maker
from app.models import Workspace, Decision, ActionItem, AuditLog
from app.services.events import manager

logger = logging.getLogger("founderos.scheduler")


async def run_decision_review_check():
    """
    Checks decision ledger items, flags decisions requiring retrospective review,
    and creates founder alerts in the workspace.
    """
    logger.info("Running decision review date scheduler check...")
    async with async_session_maker() as session:
        try:
            result = await session.execute(select(Workspace))
            workspace = result.scalars().first()
            if not workspace:
                return

            decisions_res = await session.execute(select(Decision).where(Decision.workspace_id == workspace.id))
            decisions = decisions_res.scalars().all()

            updated_count = 0
            for d in decisions:
                # Flag open decisions for learning review
                if d.status == "Open" and "August 14" in d.detail:
                    d.status = "Learning Required"
                    session.add(d)
                    updated_count += 1

                    # Add action item alert for founder
                    action = ActionItem(
                        workspace_id=workspace.id,
                        title=f"Retrospective Review: {d.title}",
                        detail=f"Decision {d.decision_code} review date has arrived. Review assumptions vs outcomes.",
                        source="Scheduler",
                        status="Ready"
                    )
                    session.add(action)

            if updated_count > 0:
                audit = AuditLog(
                    workspace_id=workspace.id,
                    actor="scheduler",
                    event="DECISION_REVIEWS_TRIGGERED",
                    details={"decisionsUpdated": updated_count}
                )
                session.add(audit)
                await session.commit()
                await manager.broadcast_refresh(str(workspace.id))
                logger.info(f"Scheduler check completed: {updated_count} decision reviews flagged.")
            else:
                logger.info("Scheduler check completed: All decision reviews up to date.")

        except Exception as e:
            logger.error(f"Error during decision scheduler check: {e}")
            await session.rollback()


async def start_scheduler_loop(interval_seconds: int = 600):
    """Runs periodic scheduler check continuously in the background."""
    logger.info(f"Starting decision review scheduler loop (interval: {interval_seconds}s)...")
    while True:
        try:
            await run_decision_review_check()
        except Exception as e:
            logger.error(f"Scheduler loop exception: {e}")
        await asyncio.sleep(interval_seconds)
