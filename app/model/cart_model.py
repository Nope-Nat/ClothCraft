from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CartProduct(BaseModel):
    id_variant_size: int
    id_product: int
    product_name: str
    variant_name: str
    color: str
    id_size: int
    size_order: int
    size: str
    quantity: int
    regular_price: float
    discounted_price: float
    price: float  # For compatibility - same as discounted_price
    thumbnail_path: Optional[str] = None
    discount_percent: Optional[float] = None
    discount_code: Optional[str] = None
    discount_from: Optional[datetime] = None
    discount_to: Optional[datetime] = None
    available_quantity: int = 0
    is_available: bool = True
    shortage: int = 0

    @property
    def has_discount(self) -> bool:
        """Check if product has an active discount"""
        return self.discount_percent is not None and self.discount_percent > 0

class CartSummary(BaseModel):
    products: List[CartProduct]
    total_amount: float
    total_regular_amount: float
    total_savings: float
    total_items: int
    coupon_code: Optional[str] = None
    can_checkout: bool = True
