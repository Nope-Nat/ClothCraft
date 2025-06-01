from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from repository.product_repository import ProductRepository
from template import templates
import os

from markupsafe import Markup
from db import db
import markdown

router = APIRouter(prefix="/product")

def parse_optional_id(id_str: Optional[str]) -> Optional[int]:
    if id_str is None:
        return None
    try:
        return int(id_str)
    except (ValueError, TypeError):
        return None

@router.get("/{id_product}", response_class=HTMLResponse)
async def product_page(
    request: Request, id_product: int,
    size: Optional[str] = None,
    variant: Optional[str] = None,
):
    product_data = await ProductRepository.get_product(id_product)
    category_id = product_data["id_category"]
    category_data = await ProductRepository.get_category_hierarchy(category_id)

    id_size = parse_optional_id(size)
    id_variants_size = parse_optional_id(variant)

    # Price and discount data
    original_price = product_data["current_price"]
    discount_percentage = 20
    discounted_price = round(original_price * (1 - discount_percentage / 100), 2)
    discount_start_date = "2025-05-01"
    discount_end_date = "2025-06-30"
    lowest_price_30_days = 75.99
    
    product_variants = [
        {"name": "Classic Red", "color": "#DC3545"},
        {"name": "Ocean Blue", "color": "#0D6EFD"},
        {"name": "Forest Green", "color": "#198754"},
        {"name": "Midnight Black", "color": "#212529"}
    ]
    
    available_sizes = ["XS", "S", "M", "L", "XL", "XXL"]

    html_description = markdown.markdown(product_data["description"], extensions=['tables'])

    # Example tags with types for styling
    tags = [
        "New Arrival", 
        "Best Seller", 
        "Premium Quality", 
        "Eco-Friendly", 
        "Limited Edition"
    ]

    images_paths = [product_data["thumbnail_path"]] if product_data["thumbnail_path"] else []
    if product_data.get("images_paths"):
        images_paths.extend(product_data["images_paths"])
    
    images_alt_descriptions = [product_data["thumbnail_alt"]] if product_data.get("thumbnail_alt") else []
    if product_data.get("images_alt_descriptions"):
        images_alt_descriptions.extend(product_data["images_alt_descriptions"])

    return await templates.TemplateResponse("product.html", {
        "request": request,
        "id_product": id_product,
        "name": product_data["name"],
        "breadcrumbs": category_data["breadcrumbs"],
        "sku_code": product_data["sku_code"],
        "short_description": product_data["short_description"],
        "description": Markup(html_description),
        "images_paths": images_paths,
        "images_alt_descriptions": images_alt_descriptions,
        "original_price": original_price,
        "discounted_price": discounted_price,
        "discount_percentage": discount_percentage,
        "discount_start_date": discount_start_date,
        "discount_end_date": discount_end_date,
        "lowest_price_30_days": lowest_price_30_days,
        "product_variants": product_variants,
        "available_sizes": available_sizes,
        "selected_size": id_size,
        "selected_variant": id_variants_size,
        "tags": tags
    })