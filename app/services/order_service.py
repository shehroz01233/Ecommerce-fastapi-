from sqlalchemy.orm import Session
from ..models.order import Order
from ..models.product import Product
from ..schemas.order_schema import OrderCreate


# =========================
# CREATE ORDER (CHECKOUT)
# =========================
def create_order(db: Session, user_id: int, order_data: OrderCreate):

    total_price = 0

    # calculate total price
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()

        if not product:
            return {"error": f"Product {item.product_id} not found"}

        if product.stock < item.quantity:
            return {"error": f"Not enough stock for {product.name}"}

        total_price += product.price * item.quantity

        # reduce stock (important real-world logic)
        product.stock -= item.quantity

    # create order
    order = Order(
        user_id=user_id,
        total_price=total_price,
        status="PENDING"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return {
        "message": "Order created successfully",
        "order": order,
        "total_price": total_price
    }


# =========================
# GET USER ORDERS
# =========================
def get_user_orders(db: Session, user_id: int):
    return db.query(Order).filter(Order.user_id == user_id).all()


# =========================
# GET ALL ORDERS (ADMIN)
# =========================
def get_all_orders(db: Session):
    return db.query(Order).all()


# =========================
# UPDATE ORDER STATUS (ADMIN)
# =========================
def update_order_status(db: Session, order_id: int, status: str):

    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        return None

    order.status = status

    db.commit()
    db.refresh(order)

    return order