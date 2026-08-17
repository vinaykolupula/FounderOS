"""
FounderOS FastAPI Application Entrypoint

This module sets up the core FastAPI server for FounderOS, configuring:
1. Database initialization and background worker lifecycle management (Ingestion, Scheduler, Execution loops).
2. CORS middleware for seamless communication with the React/Vite frontend.
3. Modular API router inclusion (Workspace, Auth, CEO Brief, Morning Briefing, Executive Board Debate, Settings, Tasks).
4. Real-time WebSocket connection handling for background push notifications to the frontend cockpit.
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db import init_db
from app.routers import workspace, auth, brief, debate, settings as model_settings, tasks, briefing, executive_tools
from app.workers.ingest import start_background_ingestion_loop
from app.workers.execution import start_execution_loop
from app.services.scheduler import start_scheduler_loop
from app.services.events import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application Lifespan Context Manager.
    
    On Startup:
    - Automatically creates database tables (if not existing).
    - Spawns background worker loops (Signal Ingestion every 5m, Scheduler every 10m, Autonomous Task Execution every 15s).
    
    On Shutdown:
    - Gracefully cancels running background tasks to prevent memory leaks or hanging DB connections.
    """
    # 1. Initialize SQLite/PostgreSQL Database tables
    await init_db()

    # 2. Start background worker loops as async tasks
    ingest_task = asyncio.create_task(start_background_ingestion_loop(interval_seconds=300))
    scheduler_task = asyncio.create_task(start_scheduler_loop(interval_seconds=600))
    execution_task = asyncio.create_task(start_execution_loop(interval_seconds=15))

    yield

    # 3. Clean up and cancel background workers on server shutdown
    ingest_task.cancel()
    scheduler_task.cancel()
    execution_task.cancel()


# Instantiate FastAPI Application
app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure Cross-Origin Resource Sharing (CORS) for frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(workspace.router)
app.include_router(auth.router)
app.include_router(brief.router)
app.include_router(briefing.router)
app.include_router(debate.router)
app.include_router(model_settings.router)
app.include_router(tasks.router)
app.include_router(executive_tools.router)


@app.get("/")
async def root():
    """Root health check endpoint."""
    return {
        "status": "healthy",
        "service": "FounderOS Executive Operating System API",
        "docs": "/docs"
    }


@app.websocket("/ws/{workspace_id}")
async def websocket_endpoint(websocket: WebSocket, workspace_id: str):
    """
    WebSocket Connection Endpoint for Real-time Cockpit Updates.
    
    Allows the backend workers (e.g. task execution completion, brief updates) to push 
    instant UI refresh events to connected client workspace sessions.
    """
    await manager.connect(websocket, workspace_id)
    try:
        while True:
            # Maintain active connection loop
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, workspace_id)
