import json
import asyncio
from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse
from ..core.redis import redis_manager
from ..core.security import decode_access_token
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
            message = await asyncio.to_thread(pubsub.get_message, timeout=1.0)
            if message and message["type"] == "message":
                yield f"data: {message['data']}\n\n"
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


def _verify_sse_token(request: Request) -> Optional[dict]:
    token = request.query_params.get("token", "")
    if not token:
        return None
    try:
        return decode_access_token(token)
    except Exception:
        return None


@router.get("/sse/stock-updates")
async def sse_stock_updates(request: Request):
    payload = _verify_sse_token(request)
    if not payload:
        return StreamingResponse(
            iter([f"data: {json.dumps({'type': 'error', 'message': 'Unauthorized'})}\n\n"]),
            media_type="text/event-stream"
        )
    return StreamingResponse(
        event_generator(NotificationService.CHANNELS["stock_updates"]),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@router.get("/sse/price-drops")
async def sse_price_drops(request: Request):
    payload = _verify_sse_token(request)
    if not payload:
        return StreamingResponse(
            iter([f"data: {json.dumps({'type': 'error', 'message': 'Unauthorized'})}\n\n"]),
            media_type="text/event-stream"
        )
    return StreamingResponse(
        event_generator(NotificationService.CHANNELS["price_drops"]),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@router.get("/sse/flash-sales")
async def sse_flash_sales(request: Request):
    payload = _verify_sse_token(request)
    if not payload:
        return StreamingResponse(
            iter([f"data: {json.dumps({'type': 'error', 'message': 'Unauthorized'})}\n\n"]),
            media_type="text/event-stream"
        )
    return StreamingResponse(
        event_generator(NotificationService.CHANNELS["flash_sales"]),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@router.get("/sse/user/{user_id}")
async def sse_user_notifications(user_id: int, request: Request):
    payload = _verify_sse_token(request)
    if not payload:
        return StreamingResponse(
            iter([f"data: {json.dumps({'type': 'error', 'message': 'Unauthorized'})}\n\n"]),
            media_type="text/event-stream"
        )
    try:
        token_user_id = int(payload.get("sub", 0))
    except (ValueError, TypeError):
        token_user_id = 0
    if token_user_id != user_id:
        return StreamingResponse(
            iter([f"data: {json.dumps({'type': 'error', 'message': 'Unauthorized'})}\n\n"]),
            media_type="text/event-stream"
        )
    return StreamingResponse(
        event_generator("user", user_id=user_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@router.get("/sse/admin")
async def sse_admin(request: Request):
    payload = _verify_sse_token(request)
    if not payload or payload.get("role") != "ADMIN":
        return StreamingResponse(
            iter([f"data: {json.dumps({'type': 'error', 'message': 'Admin access required'})}\n\n"]),
            media_type="text/event-stream"
        )
    return StreamingResponse(
        event_generator(NotificationService.CHANNELS["admin_alerts"]),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )
