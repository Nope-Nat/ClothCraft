from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import os

from markupsafe import Markup
from db import db
import markdown

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/product")

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
    })