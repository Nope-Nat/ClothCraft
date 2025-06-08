from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProductDetails(BaseModel):
    id_product: int
    name: str
    short_description: str
    thumbnail_path: str
    active: bool
    sku_code: str
    category_name: str
    country_name: str
    sizing_type: str
    current_price: float
    lowest_price_30_days: float
    description: Optional[str]