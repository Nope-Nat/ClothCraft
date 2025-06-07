from typing import Optional, List
from fastapi import APIRouter, HTTPException, Request, Form, status
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
from utils.auth_utils import verify_admin_access

router = APIRouter(prefix="/admin/new_product")

async def get_product_form_data():
    """Get all the data needed for the product form template."""
    categories = await ProductRepository.get_all_categories()
    sizing_types = await ProductRepository.get_all_sizing_types()
    countries = await ProductRepository.get_all_countries()
    tags = await ProductRepository.get_all_tags()
    
    return {
        "categories": categories,
        "sizing_types": sizing_types,
        "countries": countries,
        "tags": tags,
    }

@router.get("/", response_class=HTMLResponse)
async def product_page(request: Request):
    # Verify admin access
    await verify_admin_access(request)
    
    # Get form data
    template_data = await get_product_form_data()
    template_data["request"] = request

    return await templates.TemplateResponse("admin/new_product.html", template_data)

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
    selected_tags: List[int] = Form(default=[]),
):
    # Verify admin access
    await verify_admin_access(request)
    
    errors = []
    
    try:
        if errors:
            # Get form data and add form values for re-display
            template_data = await get_product_form_data()
            template_data.update({
                "request": request,
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
                "selected_tags": selected_tags,
            })
            
            return templates.TemplateResponse("admin/new_product.html", template_data)
        
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
            initial_description=initial_description.strip(),
            tag_ids=selected_tags
        )
        
        # Redirect to the product page
        return RedirectResponse(url=f"/product/{new_product_id}", status_code=303)
        
    except Exception as e:
        # Get form data and add error + form values for re-display
        template_data = await get_product_form_data()
        template_data.update({
            "request": request,
            "errors": [f"Error creating product: {str(e)}"],
            "product_name": product_name,
            "id_category": id_category,
            "id_sizing_type": id_sizing_type,
            "id_country": id_country,
            "sku_code": sku_code,
            "short_description": short_description,
            "thumbnail_path": thumbnail_path,
            "initial_price": initial_price,
            "initial_description": initial_description,
            "selected_tags": selected_tags,
        })
        
        return await templates.TemplateResponse("admin/new_product.html", template_data)

