from sqlalchemy.orm import Session
from ..models.product import Product
from ..schemas.product_schema import ProductCreate, ProductUpdate


# =========================
# CREATE PRODUCT
# =========================
def create_product(db: Session, product: ProductCreate):
    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


# =========================
# GET ALL PRODUCTS
# =========================
def get_all_products(db: Session):
    return db.query(Product).all()


# =========================
# GET SINGLE PRODUCT
# =========================
def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


# =========================
# UPDATE PRODUCT
# =========================
def update_product(db: Session, product_id: int, updated_data: ProductUpdate):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        return None

    if updated_data.name is not None:
        product.name = updated_data.name

    if updated_data.description is not None:
        product.description = updated_data.description

    if updated_data.price is not None:
        product.price = updated_data.price

    if updated_data.stock is not None:
        product.stock = updated_data.stock

    db.commit()
    db.refresh(product)

    return product


# =========================
# DELETE PRODUCT
# =========================
def delete_product(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        return None

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}