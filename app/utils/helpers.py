from datetime import datetime


def format_price(price: float) -> float:
    return round(price, 2)


def generate_order_code(order_id: int) -> str:
    return f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{order_id}"
