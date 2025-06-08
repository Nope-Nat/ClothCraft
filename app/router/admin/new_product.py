from typing import Optional, List
from fastapi import APIRouter, Request, Form, HTTPException, status, File, UploadFile
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
import hashlib
import time
from pathlib import Path

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
    thumbnail_file: Optional[UploadFile] = File(None)
):
    """Create a new product with optional image upload"""
    await verify_admin_access(request)
    
    # Get form data for potential re-display on error
    async def get_template_data_with_error(error_msg: str):
        template_data = await get_product_form_data()
        template_data.update({
            "request": request,
            "errors": [error_msg],
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
        return template_data
    
    try:
        final_thumbnail_path = thumbnail_path
        
        # Handle image upload if provided
        if thumbnail_file and thumbnail_file.filename:
            try:
                # Validate file type
                allowed_types = {'image/jpeg', 'image/png', 'image/webp', 'image/jpg'}
                if thumbnail_file.content_type not in allowed_types:
                    template_data = await get_template_data_with_error("Invalid file type. Please upload JPEG, PNG, or WebP images only.")
                    return templates.TemplateResponse("admin/new_product.html", template_data)
                
                # Read file content
                file_content = await thumbnail_file.read()
                
                # Generate unique filename using hash + timestamp
                file_hash = hashlib.sha256(file_content + str(time.time()).encode()).hexdigest()[:16]
                file_extension = thumbnail_file.filename.split('.')[-1].lower()
                if file_extension not in ['jpg', 'jpeg', 'png', 'webp']:
                    file_extension = 'jpg'
                
                filename = f"{file_hash}.{file_extension}"
                
                # Ensure the static/img directory exists
                img_dir = Path("static/img")
                img_dir.mkdir(parents=True, exist_ok=True)
                
                # Save file
                file_path = img_dir / filename
                with open(file_path, "wb") as f:
                    f.write(file_content)
                
                # Update thumbnail path to use uploaded file
                final_thumbnail_path = f"/static/img/{filename}"
                
            except Exception as e:
                template_data = await get_template_data_with_error(f"Failed to upload image: {str(e)}")
                return templates.TemplateResponse("admin/new_product.html", template_data)
        
        # Validate form inputs
        if not product_name.strip():
            template_data = await get_template_data_with_error("Product name is required")
            return templates.TemplateResponse("admin/new_product.html", template_data)
        
        if not sku_code.strip() or len(sku_code.strip()) < 8:
            template_data = await get_template_data_with_error("SKU code must be at least 8 characters long")
            return templates.TemplateResponse("admin/new_product.html", template_data)
        
        if initial_price <= 0:
            template_data = await get_template_data_with_error("Initial price must be greater than 0")
            return templates.TemplateResponse("admin/new_product.html", template_data)
        
        # Create the product
        new_product_id = await ProductRepository.create_product(
            id_category=id_category,
            id_sizing_type=id_sizing_type,
            id_country=id_country,
            sku_code=sku_code.strip(),
            short_description=short_description.strip(),
            thumbnail_path=final_thumbnail_path.strip() if final_thumbnail_path else '/static/img/no_image.png',
            product_name=product_name.strip(),
            initial_price=initial_price,
            initial_description=initial_description.strip(),
            tag_ids=selected_tags
        )
        
        # Redirect to the product page
        return RedirectResponse(url=f"/product/{new_product_id}", status_code=303)
        
    except Exception as e:
        # Get form data and add error + form values for re-display
        template_data = await get_template_data_with_error(f"Error creating product: {str(e)}")
        return templates.TemplateResponse("admin/new_product.html", template_data)

