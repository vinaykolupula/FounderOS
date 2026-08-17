"""
Tasks Router Module

Provides endpoints for task management:
1. List & Priority Sort (P0_CRITICAL > P1_HIGH > P2_MEDIUM > P3_LOW).
2. Task Creation & Status Updates.
3. Task Delegation to Autonomous AI Execution Worker.
4. Simulated Multi-Tool System Scan (Gmail, Calendar, Linear).
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List, Optional
from pydantic import BaseModel, Field

from app.db import get_async_session
from app.models import Task, TaskBase, Workspace

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: Optional[str] = Field(default=None, max_length=50)
    category: Optional[str] = Field(default=None, max_length=50)
    status: Optional[str] = Field(default=None, max_length=50)
    due_date: Optional[str] = Field(default=None, max_length=100)


@router.get("", response_model=List[Task])
async def list_tasks(
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_async_session)
):
    ws_result = await session.execute(select(Workspace))
    workspace = ws_result.scalars().first()
    if not workspace:
        return []

    query = select(Task).where(Task.workspace_id == workspace.id)
    if category:
        query = query.where(Task.category == category)
    if priority:
        query = query.where(Task.priority == priority)
    
    # Priority sorting order: P0_CRITICAL > P1_HIGH > P2_MEDIUM > P3_LOW
    result = await session.execute(query)
    tasks = result.scalars().all()
    
    priority_order = {"P0_CRITICAL": 0, "P1_HIGH": 1, "P2_MEDIUM": 2, "P3_LOW": 3}
    sorted_tasks = sorted(tasks, key=lambda t: (priority_order.get(t.priority, 4), t.id))
    return sorted_tasks


@router.post("", response_model=Task)
async def create_task(payload: TaskCreate, session: AsyncSession = Depends(get_async_session)):
    ws_result = await session.execute(select(Workspace))
    workspace = ws_result.scalars().first()
    if not workspace:
        workspace = Workspace(is_onboarded=True)
        session.add(workspace)
        await session.commit()
        await session.refresh(workspace)
        
    assert workspace.id is not None

    db_task = Task(**payload.model_dump(), workspace_id=workspace.id)
    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)
    return db_task


@router.patch("/{task_id}", response_model=Task)
async def update_task(task_id: int, payload: TaskUpdate, session: AsyncSession = Depends(get_async_session)):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@router.post("/{task_id}/delegate", response_model=Task)
async def delegate_task_to_agent(task_id: int, session: AsyncSession = Depends(get_async_session)):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "DELEGATED"
    task.category = "DELEGATED"
    task.agent_note = "FounderOS Agent autonomously analyzing payload and preparing draft execution receipt."

    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@router.post("/scan", response_model=List[Task])
async def agent_scan_monitored_systems(session: AsyncSession = Depends(get_async_session)):
    """
    Agent scans overall emails, calendar, Linear issues, and system alerts to discover
    and prioritize founder tasks.
    """
    ws_result = await session.execute(select(Workspace))
    workspace = ws_result.scalars().first()
    if not workspace:
        workspace = Workspace(is_onboarded=True)
        session.add(workspace)
        await session.commit()
        await session.refresh(workspace)
        
    assert workspace.id is not None

    # Simulated agent discovery items
    discovered_tasks = [
        Task(
            workspace_id=workspace.id,
            title="Review Enterprise SLA clause for Atlas Logistics contract",
            description="Incoming email from Atlas legal requests custom 99.9% uptime SLA response before 5 PM.",
            priority="P0_CRITICAL",
            category="TODAY",
            source="EMAIL",
            status="PENDING",
            due_date="Today 5:00 PM",
            agent_note="Discovered from Gmail monitoring. Flagged P0 due to deal size ($120k ARR)."
        ),
        Task(
            workspace_id=workspace.id,
            title="Prepare discovery call notes for Sequoia Partner sync",
            description="Calendar event tomorrow at 10:00 AM. Agent extracted metric pitch deck highlights.",
            priority="P1_HIGH",
            category="UPCOMING",
            source="CALENDAR",
            status="PENDING",
            due_date="Tomorrow 10:00 AM",
            agent_note="Discovered from Google Calendar sync."
        ),
        Task(
            workspace_id=workspace.id,
            title="Approve activation funnel patch on Linear issue #LIN-284",
            description="Linear issue created by Product lead regarding first-value completion drop.",
            priority="P1_HIGH",
            category="TODAY",
            source="LINEAR",
            status="PENDING",
            due_date="Today",
            agent_note="Discovered from Linear integration webhook."
        )
    ]

    for t in discovered_tasks:
        session.add(t)
    
    await session.commit()
    
    # Return all tasks sorted by priority
    res = await session.execute(select(Task))
    all_tasks = res.scalars().all()
    priority_order = {"P0_CRITICAL": 0, "P1_HIGH": 1, "P2_MEDIUM": 2, "P3_LOW": 3}
    return sorted(all_tasks, key=lambda t: (priority_order.get(t.priority, 4), t.id))
