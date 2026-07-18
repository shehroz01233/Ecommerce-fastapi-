import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import List, Dict, Optional
from ..core.redis import redis_manager
from ..core.security import decode_access_token
from ..services.notification_service import NotificationService

router = APIRouter(tags=["Notifications"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            "global": [],
            "admin": [],
        }
        self.user_connections: Dict[int, List[WebSocket]] = {}
        self.connection_channels: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, channel: str = "global", user_id: int = None):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)
        self.connection_channels[websocket] = channel

        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int = None):
        channel = self.connection_channels.pop(websocket, "global")
        if channel in self.active_connections and websocket in self.active_connections[channel]:
            self.active_connections[channel].remove(websocket)

        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)

    def switch_channel(self, websocket: WebSocket, new_channel: str):
        old_channel = self.connection_channels.get(websocket, "global")
        if old_channel in self.active_connections and websocket in self.active_connections[old_channel]:
            self.active_connections[old_channel].remove(websocket)

        if new_channel not in self.active_connections:
            self.active_connections[new_channel] = []
        self.active_connections[new_channel].append(websocket)
        self.connection_channels[websocket] = new_channel

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception:
            pass

    async def broadcast(self, message: str, channel: str = "global"):
        if channel in self.active_connections:
            dead = []
            for connection in self.active_connections[channel]:
                try:
                    await connection.send_text(message)
                except Exception:
                    dead.append(connection)
            for d in dead:
                self.active_connections[channel].remove(d)

    async def send_to_user(self, user_id: int, message: str):
        if user_id in self.user_connections:
            dead = []
            for connection in self.user_connections[user_id]:
                try:
                    await connection.send_text(message)
                except Exception:
                    dead.append(connection)
            for d in dead:
                self.user_connections[user_id].remove(d)


manager = ConnectionManager()


def _verify_ws_token(token: str) -> Optional[dict]:
    if not token:
        return None
    payload = decode_access_token(token)
    return payload


@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket, channel: str = Query("global"), token: str = Query(None)):
    payload = _verify_ws_token(token)
    if not payload:
        await websocket.accept()
        await websocket.close(code=4001, reason="Invalid or missing token")
        return

    await manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "subscribe":
                    new_channel = msg.get("channel", "global")
                    manager.switch_channel(websocket, new_channel)
                    await manager.send_personal_message(
                        json.dumps({"type": "subscribed", "channel": new_channel}),
                        websocket
                    )
                elif msg.get("type") == "ping":
                    await manager.send_personal_message(json.dumps({"type": "pong"}), websocket)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def _listen_redis_pubsub(pubsub, websocket):
    try:
        while True:
            message = await asyncio.to_thread(pubsub.get_message, timeout=0.1)
            if message and message["type"] == "message":
                await manager.send_personal_message(message["data"], websocket)
            await asyncio.sleep(0.05)
    except asyncio.CancelledError:
        pass
    except Exception:
        pass


@router.websocket("/ws/user/{user_id}")
async def websocket_user_notifications(websocket: WebSocket, user_id: int, token: str = Query(None)):
    payload = _verify_ws_token(token)
    if not payload or int(payload.get("sub", 0)) != user_id:
        await websocket.accept()
        await websocket.close(code=4001, reason="Unauthorized")
        return

    await manager.connect(websocket, channel="global", user_id=user_id)

    pubsub = None
    redis_task = None

    if redis_manager.connected:
        try:
            pubsub = redis_manager.subscribe(
                NotificationService.CHANNELS["user_notifications"].format(user_id=user_id),
                NotificationService.CHANNELS["stock_updates"],
                NotificationService.CHANNELS["price_drops"],
                NotificationService.CHANNELS["flash_sales"]
            )
            if pubsub:
                redis_task = asyncio.create_task(_listen_redis_pubsub(pubsub, websocket))
        except Exception:
            pass

    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await manager.send_personal_message(json.dumps({"type": "pong"}), websocket)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        if redis_task:
            redis_task.cancel()
        if pubsub:
            try:
                pubsub.unsubscribe()
            except Exception:
                pass


@router.websocket("/ws/admin")
async def websocket_admin(websocket: WebSocket, token: str = Query(None)):
    payload = _verify_ws_token(token)
    if not payload or payload.get("role") != "ADMIN":
        await websocket.accept()
        await websocket.close(code=4001, reason="Admin access required")
        return

    await manager.connect(websocket, "admin")

    pubsub = None
    redis_task = None

    if redis_manager.connected:
        try:
            pubsub = redis_manager.subscribe(
                NotificationService.CHANNELS["admin_alerts"],
                NotificationService.CHANNELS["order_updates"]
            )
            if pubsub:
                redis_task = asyncio.create_task(_listen_redis_pubsub(pubsub, websocket))
        except Exception:
            pass

    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        if redis_task:
            redis_task.cancel()
        if pubsub:
            try:
                pubsub.unsubscribe()
            except Exception:
                pass
