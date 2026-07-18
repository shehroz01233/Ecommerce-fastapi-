import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import List, Dict
from ..core.redis import redis_manager
from ..services.notification_service import NotificationService

router = APIRouter(tags=["Notifications"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            "global": [],
            "admin": [],
        }
        self.user_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str = "global", user_id: int = None):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)

        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, channel: str = "global", user_id: int = None):
        if channel in self.active_connections:
            if websocket in self.active_connections[channel]:
                self.active_connections[channel].remove(websocket)

        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)

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


@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket, channel: str = Query("global")):
    await manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "subscribe":
                    new_channel = msg.get("channel", "global")
                    if new_channel not in manager.active_connections:
                        manager.active_connections[new_channel] = []
                    manager.active_connections[new_channel].append(websocket)
                    await manager.send_personal_message(
                        json.dumps({"type": "subscribed", "channel": new_channel}),
                        websocket
                    )
                elif msg.get("type") == "ping":
                    await manager.send_personal_message(
                        json.dumps({"type": "pong"}),
                        websocket
                    )
            except json.JSONDecodeError:
                await manager.broadcast(f"Notification: {data}", channel)
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)


@router.websocket("/ws/user/{user_id}")
async def websocket_user_notifications(websocket: WebSocket, user_id: int):
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

            async def listen_redis():
                try:
                    while True:
                        message = pubsub.get_message(timeout=0.1)
                        if message and message["type"] == "message":
                            await manager.send_personal_message(message["data"], websocket)
                        await asyncio.sleep(0.05)
                except Exception:
                    pass

            redis_task = asyncio.create_task(listen_redis())
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
        manager.disconnect(websocket, "global", user_id)
        if redis_task:
            redis_task.cancel()
        if pubsub:
            try:
                pubsub.unsubscribe()
            except Exception:
                pass


@router.websocket("/ws/admin")
async def websocket_admin(websocket: WebSocket):
    await manager.connect(websocket, "admin")

    pubsub = None
    redis_task = None

    if redis_manager.connected:
        try:
            pubsub = redis_manager.subscribe(
                NotificationService.CHANNELS["admin_alerts"],
                NotificationService.CHANNELS["order_updates"]
            )

            async def listen_redis():
                try:
                    while True:
                        message = pubsub.get_message(timeout=0.1)
                        if message and message["type"] == "message":
                            await manager.send_personal_message(message["data"], websocket)
                        await asyncio.sleep(0.05)
                except Exception:
                    pass

            redis_task = asyncio.create_task(listen_redis())
        except Exception:
            pass

    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, "admin")
        if redis_task:
            redis_task.cancel()
        if pubsub:
            try:
                pubsub.unsubscribe()
            except Exception:
                pass
