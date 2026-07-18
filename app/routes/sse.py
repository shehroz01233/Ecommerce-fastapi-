import json
import asyncio
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from ..core.redis import redis_manager
from ..services.notification_service import NotificationService

router = APIRouter(tags=["SSE"])


async def event_generator(channel: str, user_id: int = None):
    if not redis_manager.connected:
        yield f"data: {json.dumps({'type': 'info', 'message': 'Real-time requires Redis'})}\n\n"
        return

    pubsub = None
    try:
        pubsub = redis_manager.redis.pubsub()

        if user_id:
            pubsub.subscribe(
                NotificationService.CHANNELS["user_notifications"].format(user_id=user_id),
                NotificationService.CHANNELS["stock_updates"],
                NotificationService.CHANNELS["price_drops"],
                NotificationService.CHANNELS["flash_sales"]
            )
        else:
            pubsub.subscribe(channel)

        while True:
            message = pubsub.get_message(timeout=1.0)
            if message and message["type"] == "message":
                data = message["data"]
                yield f"data: {data}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
            await asyncio.sleep(0.5)
    except asyncio.CancelledError:
        pass
    except GeneratorExit:
        pass
    finally:
        if pubsub:
            try:
                pubsub.unsubscribe()
            except Exception:
                pass


@router.get("/sse/stock-updates")
async def sse_stock_updates():
    return StreamingResponse(
        event_generator(NotificationService.CHANNELS["stock_updates"]),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@router.get("/sse/price-drops")
async def sse_price_drops():
    return StreamingResponse(
        event_generator(NotificationService.CHANNELS["price_drops"]),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@router.get("/sse/flash-sales")
async def sse_flash_sales():
    return StreamingResponse(
        event_generator(NotificationService.CHANNELS["flash_sales"]),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@router.get("/sse/user/{user_id}")
async def sse_user_notifications(user_id: int):
    return StreamingResponse(
        event_generator("user", user_id=user_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@router.get("/sse/admin")
async def sse_admin():
    return StreamingResponse(
        event_generator(NotificationService.CHANNELS["admin_alerts"]),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )
