from fastapi import WebSocket
from typing import Dict, List
import json, logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.game_connections: Dict[str, List[WebSocket]] = {}
        self.coach_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, game_id: str, role: str = "viewer"):
        await websocket.accept()
        group = self.coach_connections if role == "coach" else self.game_connections
        if game_id not in group:
            group[game_id] = []
        group[game_id].append(websocket)

    def disconnect(self, websocket: WebSocket, game_id: str, role: str = "viewer"):
        group = self.coach_connections if role == "coach" else self.game_connections
        if game_id in group:
            group[game_id] = [ws for ws in group[game_id] if ws != websocket]

    async def broadcast_alert(self, game_id: str, data: dict):
        msg = json.dumps({"type": "alert", "game_id": game_id, "data": data, "timestamp": datetime.utcnow().isoformat()})
        for group in [self.coach_connections, self.game_connections]:
            if game_id not in group:
                continue
            dead = []
            for ws in group[game_id]:
                try:
                    await ws.send_text(msg)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                group[game_id] = [w for w in group[game_id] if w != ws]

manager = ConnectionManager()