from ..core.redis import redis_manager
from datetime import datetime


class NotificationService:
    CHANNELS = {
        "stock_updates": "channel:stock_updates",
        "order_updates": "channel:order_updates",
        "price_drops": "channel:price_drops",
        "flash_sales": "channel:flash_sales",
        "user_notifications": "channel:user:{user_id}",
        "admin_alerts": "channel:admin_alerts",
        "reviews": "channel:reviews:{product_id}",
    }

    @staticmethod
    def notify_stock_update(product_id: int, product_name: str, stock: int):
        redis_manager.publish(
            NotificationService.CHANNELS["stock_updates"],
            {
                "type": "stock_update",
                "product_id": product_id,
                "product_name": product_name,
                "stock": stock,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    @staticmethod
    def notify_order_status(user_id: int, order_id: int, status: str):
        redis_manager.publish(
            NotificationService.CHANNELS["order_updates"],
            {
                "type": "order_update",
                "user_id": user_id,
                "order_id": order_id,
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        redis_manager.publish(
            NotificationService.CHANNELS["user_notifications"].format(user_id=user_id),
            {
                "type": "order_update",
                "order_id": order_id,
                "status": status,
                "message": f"Your order #{order_id} is now {status}",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    @staticmethod
    def notify_price_drop(product_id: int, product_name: str, old_price: float, new_price: float):
        discount = round((1 - new_price / old_price) * 100, 1) if old_price > 0 else 0
        redis_manager.publish(
            NotificationService.CHANNELS["price_drops"],
            {
                "type": "price_drop",
                "product_id": product_id,
                "product_name": product_name,
                "old_price": old_price,
                "new_price": new_price,
                "discount": discount,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    @staticmethod
    def notify_flash_sale(title: str, discount_percent: int, product_ids: list):
        redis_manager.publish(
            NotificationService.CHANNELS["flash_sales"],
            {
                "type": "flash_sale",
                "title": title,
                "discount_percent": discount_percent,
                "product_ids": product_ids,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    @staticmethod
    def notify_admin_alert(message: str, severity: str = "info"):
        redis_manager.publish(
            NotificationService.CHANNELS["admin_alerts"],
            {
                "type": "admin_alert",
                "message": message,
                "severity": severity,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    @staticmethod
    def notify_new_review(product_id: int, user_name: str, rating: int):
        redis_manager.publish(
            NotificationService.CHANNELS["reviews"].format(product_id=product_id),
            {
                "type": "new_review",
                "product_id": product_id,
                "user_name": user_name,
                "rating": rating,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    @staticmethod
    def send_personal_notification(user_id: int, message: str, notif_type: str = "info"):
        redis_manager.publish(
            NotificationService.CHANNELS["user_notifications"].format(user_id=user_id),
            {
                "type": notif_type,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
        )


notification_service = NotificationService()
