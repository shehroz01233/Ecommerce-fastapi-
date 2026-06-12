from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas.product_schema import ProductCreate, ProductUpdate
from ..services import product_service

router = APIRouter(prefix="/products", tags=["Products"])


# =========================
# CREATE PRODUCT
# =========================
@router.post("/")
def create(product: ProductCreate, db: Session = Depends(get_db)):
    return product_service.create_product(db, product)


# =========================
# GET ALL PRODUCTS
# =========================
@router.get("/")
def get_all(db: Session = Depends(get_db)):
    return product_service.get_all_products(db)


# =========================
# GET SINGLE PRODUCT
# =========================
@router.get("/{product_id}")
def get_one(product_id: int, db: Session = Depends(get_db)):
    product = product_service.get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


# =========================
# UPDATE PRODUCT
# =========================
@router.put("/{product_id}")
def update(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    updated = product_service.update_product(db, product_id, product)

    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")

    return updated


# =========================
# DELETE PRODUCT
# =========================
@router.delete("/{product_id}")
def delete(product_id: int, db: Session = Depends(get_db)):
    result = product_service.delete_product(db, product_id)

    if not result:
        raise HTTPException(status_code=404, detail="Product not found")

    return result