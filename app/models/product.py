from sqlalchemy import Column, Integer, String, Float
from ..core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String)
    price = Column(Float, nullable=False, index=True)
    stock = Column(Integer, nullable=False)
    category = Column(String, default="General", index=True)
    image_url = Column(String, default="")
