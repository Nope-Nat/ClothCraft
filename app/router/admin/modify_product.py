from fastapi import APIRouter, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from repository.product_repository import ProductRepository
from template import templates
from repository.product.variant_repository import VariantRepository

from db import db
from fastapi.responses import JSONResponse
from utils.auth_utils import verify_admin_access

router = APIRouter(prefix="/admin/modify_product")

@router.get("/{id_product}", response_class=HTMLResponse)
async def product_page(request: Request, id_product: int):
    await verify_admin_access(request)
    
    variants = await VariantRepository.get_product_variants(id_product)
    compatible_sizes = await VariantRepository.get_compatible_sizes_for_product(id_product)
    
    variant_data = []
    for variant in variants:
        existing_sizes = await VariantRepository.get_variant_existing_sizes(variant['id_variant'])
        available_sizes = [size for size in compatible_sizes if size['id_size'] not in existing_sizes]
        variant_data.append({
            'variant': variant,
            'available_sizes': available_sizes
        })
    
    return await templates.TemplateResponse("admin/modify_product.html", {
        "request": request,
        "id_product": id_product,
        "variant_data": variant_data,
    })

@router.post("/{id_product}/add_size")
async def add_size_to_variant(request: Request, id_product: int, id_variant: int = Form(), id_size: int = Form()):
    await verify_admin_access(request)
    
    await VariantRepository.add_size_to_variant(id_variant, id_size)
    
    return RedirectResponse(url=f"/admin/modify_product/{id_product}", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/{id_product}/add_variant")
async def add_variant(request: Request, id_product: int, name: str = Form(), color: str = Form()):
    await verify_admin_access(request)
    
    await VariantRepository.add_variant(id_product, name, color)
    
    return RedirectResponse(url=f"/admin/modify_product/{id_product}", status_code=status.HTTP_303_SEE_OTHER)