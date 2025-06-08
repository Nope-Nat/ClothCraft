from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from repository.product_repository import ProductRepository
from template import templates
from utils.auth_utils import get_current_user, require_admin
import os
from fastapi import Form, Depends
from utils.auth_utils import admin_required

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

# First route handler
@router.get("/{id_product}", response_class=HTMLResponse)
async def product_page(
    request: Request,
    id_product: int,
    id_size: Optional[str] = None,
    id_variant: Optional[str] = None,
    id_format: Optional[str] = None,
):
    user_data = await get_current_user(request)
    is_admin = require_admin(user_data)
    
    product_data = await ProductRepository.get_product(id_product)
    category_id = product_data["id_category"]
    category_data = await ProductRepository.get_category_hierarchy(category_id)

    id_size = parse_optional_id(id_size)
    id_variant = parse_optional_id(id_variant)
    id_format = parse_optional_id(id_format)

    discount_data = await ProductRepository.get_product_discount_info(id_product)
    if not discount_data:
        discount_data = {
            "discount_percent": 0,
            "discount_from": None,
            "discount_to": None
        }
    original_price = product_data["current_price"]
    discount_percentage = discount_data["discount_percent"]
    discounted_price = round(original_price * (1 - discount_percentage / 100), 2)
    discount_start_date = discount_data["discount_from"]
    discount_end_date = discount_data["discount_to"]
    lowest_price_30_days = (await ProductRepository.get_min_price_30_days(id_product))["min_price"]
    
    product_variants_raw = await ProductRepository.get_product_variants(id_product)
    product_variants = []
    for variant in product_variants_raw:
        color_data = variant['color']
        assert isinstance(color_data, bytes)
        color_value = f"#{int.from_bytes(color_data, byteorder='big'):06X}"
        product_variants.append({
            "id": variant['id_variant'],
            "name": variant['name'],
            "color": color_value
        })
    
    # Ensure default variant is selected
    if id_variant is None and product_variants:
        id_variant = product_variants[0]["id"]
    
    # Get available sizing formats for the product
    available_formats = []
    variant_sizes = []
    if id_variant is not None:
        available_formats = await ProductRepository.get_product_sizing_formats(id_product)
        
        # Ensure default format is selected
        if id_format is None and available_formats:
            id_format = available_formats[0]["id_sizing_format"]
        
        # Get sizes for the selected variant and format
        if id_format is not None:
            variant_sizes_raw = await ProductRepository.get_product_variant_sizes(id_variant, id_format)
            variant_sizes = [
                {
                    'id_size': size_data['id_size'],
                    'size_order': size_data['size_order'],
                    'id_variant_size': size_data['id_variant_size'],
                    'size_value': size_data['size_value'],
                    'available_quantity': size_data['available_quantity'],
                    'in_stock': size_data['available_quantity'] > 0
                }
                for size_data in variant_sizes_raw
            ]
    
    # Ensure default size is selected (only from in-stock sizes)
    if id_size is None and variant_sizes:
        in_stock_sizes = [size for size in variant_sizes if size['in_stock']]
        if in_stock_sizes:
            id_size = in_stock_sizes[0]["id_size"]
    
    # Calculate variant_size_id for the form
    variant_size_id = None
    if id_variant and id_size:
        async with db.get_connection() as conn:
            result = await conn.fetchrow(
                "SELECT id_variant_size FROM variant_size WHERE id_variant = $1 AND id_size = $2",
                id_variant, id_size
            )
            if result:
                variant_size_id = result["id_variant_size"]

    html_description = markdown.markdown(product_data["description"], extensions=['tables'])

    images_paths = [product_data["thumbnail_path"]] if product_data["thumbnail_path"] else []
    if product_data.get("images_paths"):
        images_paths.extend(product_data["images_paths"])
    
    images_alt_descriptions = [product_data["thumbnail_alt"]] if product_data.get("thumbnail_alt") else []
    if product_data.get("images_alt_descriptions"):
        images_alt_descriptions.extend(product_data["images_alt_descriptions"])

    materials_info = await ProductRepository.get_product_materials_info(id_product)
    tags_info = await ProductRepository.get_product_tags_info(id_product)
    tags = [ t["tag_name"] for t in tags_info ]

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
        "available_formats": available_formats,
        "variant_sizes": variant_sizes,
        "id_size": id_size,
        "id_variant": id_variant,
        "id_format": id_format,
        "variant_size_id": variant_size_id,
        "tags": tags,
        "materials_info": materials_info,
        "tags_info": tags_info,
        "is_admin": is_admin,
    })

# Second route handler - fix indentation by moving it out of product_page
@router.post("/{id_product}/add-to-storage")
async def add_to_storage(
    request: Request,
    id_product: int,
    variant_id: int = Form(...),
    quantity: int = Form(...),
    user_data: dict = Depends(admin_required)
):
    try:
        async with db.get_connection() as conn:
            await conn.execute(
                """
                SELECT add_storage_delivery_part(
                    $1::integer,
                    $2::integer
                )
                """,
                variant_id, quantity
            )
        return RedirectResponse(
            url=f"/product/{id_product}",
            status_code=303
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))