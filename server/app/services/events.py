"""
WebSocket & Distributed Broadcast Event Bus

Manages real-time UI synchronizations across worker processes:
- In-memory pub/sub backend for single-node local development.
- Redis pub/sub backend for horizontal worker scaling in production clusters.
- Automatic graceful fallback if Redis is unavailable or uninstalled.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Awaitable, Optional, Set
from fastapi import WebSocket

from app.config import settings

logger = logging.getLogger("founderos.events")


class BaseBroadcastBackend(ABC):
    """Abstract interface for pub/sub message dissemination across web worker processes."""

    @abstractmethod
    async def publish(self, channel: str, message: dict):
        """Publishes an event message to a channel topic."""
        pass

    @abstractmethod
    async def subscribe(self, channel: str, callback: Callable[[dict], Awaitable[None]]):
        """Subscribes a local callback listener to channel events."""
        pass


class InMemoryBroadcastBackend(BaseBroadcastBackend):
    """Local in-process broadcast provider for single-node / development environments."""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[dict], Awaitable[None]]]] = {}

    async def publish(self, channel: str, message: dict):
        listeners = self._subscribers.get(channel, [])
        for cb in listeners:
            try:
                res = cb(message)
                if asyncio.iscoroutine(res):
                    await res
            except Exception as e:
                logger.warning(f"Error invoking in-memory broadcast callback on {channel}: {e}")

    async def subscribe(self, channel: str, callback: Callable[[dict], Awaitable[None]]):
        if channel not in self._subscribers:
            self._subscribers[channel] = []
        self._subscribers[channel].append(callback)


class RedisBroadcastBackend(BaseBroadcastBackend):
    """
    Distributed Redis pub/sub backend enabling horizontal multi-worker scaling.
    Gracefully falls back to InMemoryBroadcastBackend if redis-py is uninstalled or unreachable.
    """

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._fallback_backend = InMemoryBroadcastBackend()
        self._redis_client = None
        self._pubsub = None
        self._subscribers: Dict[str, List[Callable[[dict], Awaitable[None]]]] = {}
        self._active_channels: Set[str] = set()
        self._listener_task: Optional[asyncio.Task] = None
        self._is_connected = False

    async def _init_redis(self) -> bool:
        """Initializes async Redis connection pool."""
        if self._is_connected and self._redis_client:
            return True

        try:
            import redis.asyncio as aioredis
            self._redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Ping test connection
            await self._redis_client.ping()
            self._pubsub = self._redis_client.pubsub()
            self._is_connected = True
            logger.info(f"Connected to Redis broadcast pub/sub at {self.redis_url}")
            return True
        except ImportError:
            logger.warning("redis-py is not installed. RedisBroadcastBackend falling back to InMemoryBroadcastBackend.")
            return False
        except Exception as e:
            logger.warning(f"Failed to connect to Redis at {self.redis_url}: {e}. Falling back to in-memory broadcast.")
            return False

    async def publish(self, channel: str, message: dict):
        # Always publish locally first for lowest intra-process latency
        await self._fallback_backend.publish(channel, message)

        ok = await self._init_redis()
        if ok and self._redis_client:
            try:
                payload = json.dumps(message)
                await self._redis_client.publish(channel, payload)
            except Exception as e:
                logger.warning(f"Redis publish failed on {channel}: {e}")

    async def subscribe(self, channel: str, callback: Callable[[dict], Awaitable[None]]):
        await self._fallback_backend.subscribe(channel, callback)

        if channel not in self._subscribers:
            self._subscribers[channel] = []
        self._subscribers[channel].append(callback)

        ok = await self._init_redis()
        if ok and self._pubsub:
            if channel not in self._active_channels:
                try:
                    await self._pubsub.subscribe(channel)
                    self._active_channels.add(channel)
                    if not self._listener_task or self._listener_task.done():
                        self._listener_task = asyncio.create_task(self._listen_loop())
                except Exception as e:
                    logger.warning(f"Failed to subscribe to Redis channel {channel}: {e}")

    async def _listen_loop(self):
        """Asynchronous reader loop listening to Redis pubsub events and dispatching to callbacks."""
        try:
            while self._is_connected and self._pubsub:
                try:
                    msg = await self._pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                    if msg and msg.get("type") == "message":
                        ch = msg.get("channel")
                        raw_data = msg.get("data")
                        if ch and raw_data:
                            try:
                                parsed = json.loads(raw_data)
                            except Exception:
                                parsed = {"raw": raw_data}
                            listeners = self._subscribers.get(ch, [])
                            for cb in listeners:
                                try:
                                    res = cb(parsed)
                                    if asyncio.iscoroutine(res):
                                        await res
                                except Exception as err:
                                    logger.warning(f"Redis listener callback error on {ch}: {err}")
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.warning(f"Error in Redis broadcast reader loop: {e}")
                    await asyncio.sleep(1.0)
        finally:
            logger.debug("Redis broadcast listener loop terminated.")


class ConnectionManager:
    """
    Manages client WebSocket connections per workspace and integrates with the
    underlying broadcast backend for horizontal worker scaling.
    """

    def __init__(self, backend: Optional[BaseBroadcastBackend] = None):
        # Maps workspace_id to a list of active websocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
        if backend is not None:
            self.backend = backend
        elif settings.REDIS_URL:
            self.backend = RedisBroadcastBackend(settings.REDIS_URL)
        else:
            self.backend = InMemoryBroadcastBackend()
        self._subscribed_channels: set = set()

    async def connect(self, websocket: WebSocket, workspace_id: str):
        await websocket.accept()
        if workspace_id not in self.active_connections:
            self.active_connections[workspace_id] = []
        self.active_connections[workspace_id].append(websocket)

        channel = f"workspace:{workspace_id}"
        if channel not in self._subscribed_channels:
            self._subscribed_channels.add(channel)
            await self.backend.subscribe(
                channel,
                lambda msg, wid=workspace_id: self._deliver_local(wid, msg)
            )

    def disconnect(self, websocket: WebSocket, workspace_id: str):
        if workspace_id in self.active_connections:
            if websocket in self.active_connections[workspace_id]:
                self.active_connections[workspace_id].remove(websocket)
            if not self.active_connections[workspace_id]:
                del self.active_connections[workspace_id]

    async def _deliver_local(self, workspace_id: str, message: dict):
        """Delivers a broadcast message to all active WebSocket connections for the workspace."""
        if workspace_id not in self.active_connections:
            return
        stale_connections = []
        for connection in list(self.active_connections[workspace_id]):
            try:
                await connection.send_json(message)
            except Exception:
                stale_connections.append(connection)

        # Clean up dead connections
        for stale in stale_connections:
            self.disconnect(stale, workspace_id)

    async def broadcast_refresh(self, workspace_id: str):
        """Broadcasts a REFRESH signal via the broadcast backend."""
        # 1. Publish to backend pub/sub (which dispatches to all subscribed workers)
        await self.backend.publish(f"workspace:{workspace_id}", {"type": "REFRESH"})
        # 2. Directly deliver to local active connections if not already delivered via backend callback
        if not self._subscribers_registered_for(workspace_id):
            await self._deliver_local(workspace_id, {"type": "REFRESH"})

    def _subscribers_registered_for(self, workspace_id: str) -> bool:
        return f"workspace:{workspace_id}" in self._subscribed_channels


manager = ConnectionManager()
