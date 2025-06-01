from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List
import os
from repository.product_repository import ProductRepository

template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=template_dir)
router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_class=HTMLResponse)
async def list_products(
    request: Request, 
    category: Optional[str] = None,
    tags: Optional[str] = None
):
    """Products listing page with template"""
    try:
        # Get category_id if provided
        category_id = None
        if category and category.strip():
            try:
                category_id = int(category)
            except ValueError:
                pass

        # Get category hierarchy and subcategories
        category_data = await ProductRepository.get_category_hierarchy(category_id)
        
        # Get all available tags
        all_tags = await ProductRepository.get_all_tags()
        
        # Parse selected tags
        selected_tags = []
        if tags:
            selected_tags = [int(tag) for tag in tags.split(',') if tag.strip().isdigit()]
        
        # Get filtered products
        products = await ProductRepository.get_products(category_id, selected_tags)
        
        return templates.TemplateResponse("products/list.html", {
            "request": request,
            "products": products,
            "breadcrumbs": category_data["breadcrumbs"],
            "subcategories": category_data["subcategories"],
            "all_tags": all_tags,
            "selected_category": category_id,
            "selected_tags": selected_tags
        })
            
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")