from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import os

from markupsafe import Markup
from db import db
import markdown

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/products")

@router.get("/{id_product}", response_class=HTMLResponse)
async def product_page(request: Request, id_product: int):
    name = "Sample Product"
    subcategories_list = [
        {"id": 1, "name": "Subcategory 1"},
        {"id": 2, "name": "Subcategory 2"},
        {"id": 3, "name": "T-Shirt"}
    ]
    country = "USA"
    sku_code = "SKU123456"
    short_description = "This is a sample product description."

    description = (
        "# Heading 1\n"
        "## Heading 2\n"
        "### Heading 3\n"
        "* Bullet point 1\n"
        "    * Sub-bullet point 1\n"
        "* Bullet point 2\n"
        "**Bold text** and *italic text*.\n"
        "[Link to example](https://example.com)\n"
    )

    images_paths = [
        "static/img/example1.webp",
        "static/img/example2.webp",
        "static/img/example3.webp"
    ]

    # Price and discount data
    original_price = 99.99
    discount_percentage = 20
    discounted_price = round(original_price * (1 - discount_percentage / 100), 2)
    discount_start_date = "2025-05-01"
    discount_end_date = "2025-06-30"
    lowest_price_30_days = 75.99
    
    # Product variants with colors (based on database schema)
    product_variants = [
        {"name": "Classic Red", "color": "#DC3545"},
        {"name": "Ocean Blue", "color": "#0D6EFD"},
        {"name": "Forest Green", "color": "#198754"},
        {"name": "Midnight Black", "color": "#212529"}
    ]
    
    # Available sizes
    available_sizes = ["XS", "S", "M", "L", "XL", "XXL"]

    html_description = markdown.markdown(description)

    return templates.TemplateResponse("product.html", {
        "request": request,
        "id_product": id_product,
        "name": name,
        "subcategories_list": subcategories_list,
        "country": country,
        "sku_code": sku_code,
        "short_description": short_description,
        "description": Markup(html_description),
        "images_paths": images_paths,
        "original_price": original_price,
        "discounted_price": discounted_price,
        "discount_percentage": discount_percentage,
        "discount_start_date": discount_start_date,
        "discount_end_date": discount_end_date,
        "lowest_price_30_days": lowest_price_30_days,
        "product_variants": product_variants,
        "available_sizes": available_sizes,
    })