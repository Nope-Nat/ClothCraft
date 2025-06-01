from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PAID = "paid"
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURN_REQUESTED = "return_requested"
    RETURN_REJECTED = "return_rejected"
    RETURN_PENDING = "return_pending"
    RETURN_SHIPPED = "return_shipped"
    RETURN_DELIVERED = "return_delivered"

class OrderProduct(BaseModel):
    product_name: str
    variant_name: str
    color: str
    size: str
    quantity: int
    price: float

class OrderSummary(BaseModel):
    id_order: int
    shipping_price: float
    payed_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    shippment_tracking_number: Optional[str]
    return_tracking_number: Optional[str]
    secret_code: Optional[str]
    current_status: OrderStatus
    status_updated_at: datetime
    total_amount: float
    products: List[OrderProduct]

    class Config:
        from_attributes = True
