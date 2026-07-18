import json
from datetime import datetime
from ..core.redis import redis_manager
from .notification_service import notification_service


def process_order_background(order_id: int, user_id: int, user_email: str, total_price: float, items: list):
    redis_manager.cache_set(
        f"order_processing:{order_id}",
        {"status": "processing", "started_at": datetime.utcnow().isoformat()},
        expire=3600
    )

    notification_service.send_personal_notification(
        user_id,
        f"Your order #{order_id} is being processed. Total: ${total_price:.2f}",
        "order_processing"
    )

    if redis_manager.connected:
        try:
            analytics_key = f"analytics:orders:{datetime.utcnow().strftime('%Y-%m-%d')}"
            redis_manager.redis.hincrby(analytics_key, "total_orders", 1)
            redis_manager.redis.hincrbyfloat(analytics_key, "total_revenue", total_price)
            redis_manager.redis.expire(analytics_key, 86400 * 30)

            for item in items:
                product_key = f"analytics:products:{item['product_id']}"
                redis_manager.redis.hincrby(product_key, "units_sold", item["quantity"])
                redis_manager.redis.hincrbyfloat(product_key, "revenue", item["price"] * item["quantity"])
                redis_manager.redis.expire(product_key, 86400 * 30)
        except Exception:
            pass

    notification_service.notify_admin_alert(
        f"New order #{order_id} - ${total_price:.2f} ({len(items)} items)",
        "order"
    )


def process_stock_alert(product_id: int, product_name: str, stock: int):
    if stock <= 5:
        notification_service.notify_admin_alert(
            f"Low stock alert: {product_name} has only {stock} units left",
            "warning"
        )
        notification_service.notify_stock_update(product_id, product_name, stock)

    if stock == 0:
        notification_service.notify_admin_alert(
            f"Out of stock: {product_name}",
            "critical"
        )


def process_review_notification(product_id: int, user_name: str, rating: int):
    notification_service.notify_new_review(product_id, user_name, rating)


def process_analytics_update(event_type: str, data: dict):
    if not redis_manager.connected:
        return
    try:
        analytics_key = f"analytics:events:{datetime.utcnow().strftime('%Y-%m-%d')}"
        redis_manager.redis.hincrby(analytics_key, event_type, 1)
        redis_manager.redis.expire(analytics_key, 86400 * 30)

        recent_key = "analytics:recent_events"
        redis_manager.redis.lpush(recent_key, json.dumps({
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }))
        redis_manager.redis.ltrim(recent_key, 0, 99)
        redis_manager.redis.expire(recent_key, 86400)
    except Exception:
        pass
