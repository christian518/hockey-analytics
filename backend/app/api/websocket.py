from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import asyncio, logging
from app.core.websocket_manager import manager

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/game/{game_id}")
async def game_websocket(websocket: WebSocket, game_id: str, role: str = Query("viewer")):
    await manager.connect(websocket, game_id, role)
    try:
        await websocket.send_json({"type": "connected", "game_id": game_id, "role": role})
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "ping"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, game_id, role)
    except Exception as e:
        logger.error(f"WS error: {e}")
        manager.disconnect(websocket, game_id, role)