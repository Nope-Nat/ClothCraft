from pydantic import BaseModel
from typing import List

class CartProduct(BaseModel):
    id_variant_size: int
    product_name: str
    variant_name: str
    color: str
    size: str
    quantity: int
    price: float
    thumbnail_path: str

class CartSummary(BaseModel):
    products: List[CartProduct]
    total_amount: float
    total_items: int

    class Config:
        from_attributes = True
