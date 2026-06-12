from datetime import datetime
import re


# =========================
# VALIDATE EMAIL FORMAT
# =========================
def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


# =========================
# FORMAT PRICE (2 DECIMALS)
# =========================
def format_price(price: float) -> float:
    return round(price, 2)


# =========================
# CALCULATE CART TOTAL
# =========================
def calculate_total(items: list) -> float:
    """
    items format:
    [
        {"price": 100, "quantity": 2},
        {"price": 50, "quantity": 1}
    ]
    """
    total = 0

    for item in items:
        total += item["price"] * item["quantity"]

    return round(total, 2)


# =========================
# GET CURRENT TIMESTAMP
# =========================
def current_time():
    return datetime.utcnow()


# =========================
# GENERATE SIMPLE ORDER CODE
# =========================
def generate_order_code(order_id: int) -> str:
    return f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{order_id}"


# =========================
# VALIDATE POSITIVE NUMBER
# =========================
def is_positive_number(value: int | float) -> bool:
    return value > 0