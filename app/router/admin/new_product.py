from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from repository.product_repository import ProductRepository
from template import templates
import os

from markupsafe import Markup
from db import db
import markdown
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/admin/new_product")

@router.get("/", response_class=HTMLResponse)
async def product_page(request: Request):
    categories = await ProductRepository.get_all_categories()
    sizing_types = await ProductRepository.get_all_sizing_types()
    countries = await ProductRepository.get_all_countries()

    return await templates.TemplateResponse("admin/new_product.html", {
        "request": request,
        "categories": categories,
        "sizing_types": sizing_types,
        "countries": countries,
    })

@router.post("/", response_class=HTMLResponse)
async def create_product(
    request: Request,
    product_name: str = Form(...),
    id_category: int = Form(...),
    id_sizing_type: int = Form(...),
    id_country: int = Form(...),
    sku_code: str = Form(...),
    short_description: str = Form(...),
    thumbnail_path: str = Form(...),
    initial_price: float = Form(...),
    initial_description: str = Form(...),
):
    errors = []
    
    try:
        # Validate required fields
        if not product_name or len(product_name.strip()) < 1:
            errors.append("Product name is required")
        if not sku_code or len(sku_code.strip()) < 1:
            errors.append("SKU code is required")
        if initial_price <= 0:
            errors.append("Price must be greater than 0")
            
        if errors:
            categories = await ProductRepository.get_all_categories()
            sizing_types = await ProductRepository.get_all_sizing_types()
            countries = await ProductRepository.get_all_countries()
            
            return templates.TemplateResponse("admin/new_product.html", {
                "request": request,
                "categories": categories,
                "sizing_types": sizing_types,
                "countries": countries,
                "errors": errors,
                "product_name": product_name,
                "id_category": id_category,
                "id_sizing_type": id_sizing_type,
                "id_country": id_country,
                "sku_code": sku_code,
                "short_description": short_description,
                "thumbnail_path": thumbnail_path,
                "initial_price": initial_price,
                "initial_description": initial_description,
            })
        
        # Create the product
        new_product_id = await ProductRepository.create_product(
            id_category=id_category,
            id_sizing_type=id_sizing_type,
            id_country=id_country,
            sku_code=sku_code.strip(),
            short_description=short_description.strip(),
            thumbnail_path=thumbnail_path.strip() if thumbnail_path else '/static/img/no_image.png',
            product_name=product_name.strip(),
            initial_price=initial_price,
            initial_description=initial_description.strip()
        )
        
        # Redirect to the product page
        return RedirectResponse(url=f"/product/{new_product_id}", status_code=303)
        
    except Exception as e:
        categories = await ProductRepository.get_all_categories()
        sizing_types = await ProductRepository.get_all_sizing_types() 
        countries = await ProductRepository.get_all_countries()
        
        errors.append(f"Error creating product: {str(e)}")
        return await templates.TemplateResponse("admin/new_product.html", {
            "request": request,
            "categories": categories,
            "sizing_types": sizing_types,
            "countries": countries,
            "errors": errors,
            "product_name": product_name,
            "id_category": id_category,
            "id_sizing_type": id_sizing_type,
            "id_country": id_country,
            "sku_code": sku_code,
            "short_description": short_description,
            "thumbnail_path": thumbnail_path,
            "initial_price": initial_price,
            "initial_description": initial_description,
        })

