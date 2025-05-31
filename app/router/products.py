from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import os
from repository.product_repository import ProductRepository

template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=template_dir)
router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_class=HTMLResponse)
async def list_products(request: Request, category: Optional[str] = None):
    """Products listing page with template"""
    try:
        # Get categories for filter
        categories = await ProductRepository.get_all_categories()
        
        # Get products with optional category filter
        category_id = None
        if category and category.strip():
            try:
                category_id = int(category)
            except ValueError:
                pass
        
        products = await ProductRepository.get_products(category_id)
        
        return templates.TemplateResponse("products/list.html", {
            "request": request,
            "products": products,
            "categories": categories,
            "selected_category": category_id
        })
            
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")