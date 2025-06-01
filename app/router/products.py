from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List
from repository.product_repository import ProductRepository
from template import templates

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_class=HTMLResponse)
async def list_products(
    request: Request, 
    category: Optional[str] = None,
    tags: Optional[str] = None,
    sizes: Optional[str] = None
):
    """Products listing page with template"""
    try:
        category_id = None
        if category and category.strip():
            try:
                category_id = int(category)
            except ValueError:
                pass

        category_data = await ProductRepository.get_category_hierarchy(category_id)
        
        all_tags = await ProductRepository.get_all_tags()
        all_sizes = await ProductRepository.get_all_sizes()
        
        selected_tags = []
        if tags:
            selected_tags = [int(tag) for tag in tags.split(',') if tag.strip().isdigit()]

        selected_sizes = []
        if sizes:
            selected_sizes = [int(size) for size in sizes.split(',') if size.strip().isdigit()]
        
        products = await ProductRepository.get_products(category_id, selected_tags, selected_sizes)
        
        return await templates.TemplateResponse("products/list.html", {
            "request": request,
            "products": products,
            "breadcrumbs": category_data["breadcrumbs"],
            "subcategories": category_data["subcategories"],
            "all_tags": all_tags,
            "all_sizes": all_sizes,
            "selected_category": category_id,
            "selected_tags": selected_tags,
            "selected_sizes": selected_sizes
        })
            
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")