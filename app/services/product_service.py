from sqlalchemy.orm import Session
from ..models.product import Product
from ..schemas.product_schema import ProductCreate, ProductUpdate


def create_product(db: Session, product: ProductCreate):
    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        category=product.category,
        image_url=product.image_url
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


def get_all_products(db: Session, search: str = None, category: str = None):
    query = db.query(Product)

    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%") |
            Product.description.ilike(f"%{search}%")
        )

    if category and category != "All":
        query = query.filter(Product.category == category)

    return query.all()


def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


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
    if updated_data.category is not None:
        product.category = updated_data.category
    if updated_data.image_url is not None:
        product.image_url = updated_data.image_url

    db.commit()
    db.refresh(product)

    return product


def delete_product(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        return None

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}


def get_categories(db: Session):
    categories = db.query(Product.category).distinct().all()
    return [c[0] for c in categories if c[0]]
