"""
WebSocket Connection Manager for Real-Time Pit-Wall Telemetry Streaming.
"""
from __future__ import annotations

import json
from typing import Dict, List
from fastapi import WebSocket


class TelemetryWebSocketManager:
    def __init__(self):
        # Maps session_id -> List[WebSocket]
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket) -> None:
        """Accept WebSocket and subscribe client to a session room."""
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket) -> None:
        """Remove disconnected client from session room."""
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def broadcast_to_session(self, session_id: str, payload: dict) -> None:
        """Broadcast live telemetry frame to all pit wall clients watching the session."""
        if session_id not in self.active_connections:
            return

        message = json.dumps(payload)
        dead_connections = []

        for connection in self.active_connections[session_id]:
            try:
                await connection.send_text(message)
            except Exception:
                dead_connections.append(connection)

        # Cleanup failed connections
        for dead in dead_connections:
            self.disconnect(session_id, dead)

    async def broadcast_global(self, payload: dict) -> None:
        """Broadcast an alert or message across all active sessions."""
        message = json.dumps(payload)
        for session_id, connections in list(self.active_connections.items()):
            for connection in connections:
                try:
                    await connection.send_text(message)
                except Exception:
                    pass


ws_manager = TelemetryWebSocketManager()
