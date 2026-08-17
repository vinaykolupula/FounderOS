import asyncio
from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Maps workspace_id to a list of active websocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, workspace_id: str):
        await websocket.accept()
        if workspace_id not in self.active_connections:
            self.active_connections[workspace_id] = []
        self.active_connections[workspace_id].append(websocket)

    def disconnect(self, websocket: WebSocket, workspace_id: str):
        if workspace_id in self.active_connections:
            if websocket in self.active_connections[workspace_id]:
                self.active_connections[workspace_id].remove(websocket)
            if not self.active_connections[workspace_id]:
                del self.active_connections[workspace_id]

    async def broadcast_refresh(self, workspace_id: str):
        if workspace_id in self.active_connections:
            stale_connections = []
            for connection in list(self.active_connections[workspace_id]):
                try:
                    await connection.send_json({"type": "REFRESH"})
                except Exception:
                    stale_connections.append(connection)
            
            # Clean up dead connections
            for stale in stale_connections:
                self.disconnect(stale, workspace_id)

manager = ConnectionManager()
