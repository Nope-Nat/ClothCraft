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
    product_materials = await VariantRepository.get_product_materials(id_product)
    all_materials = await VariantRepository.get_all_materials()
    
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
        "product_materials": product_materials,
        "all_materials": all_materials,
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

@router.post("/{id_product}/update_materials")
async def update_materials(request: Request, id_product: int):
    await verify_admin_access(request)
    
    try:
        form_data = await request.form()
        materials_data = []
        
        # Parse form data - assuming format: material_1, percentage_1, material_2, percentage_2, etc.
        i = 0
        while f"material_{i}" in form_data:
            id_material = int(form_data[f"material_{i}"])
            percentage = float(form_data[f"percentage_{i}"])
            materials_data.append((id_material, percentage))
            i += 1
        
        await VariantRepository.update_product_materials(id_product, materials_data)
        
    except Exception as e:
        # For now, just redirect back - could add query parameter for error display
        return RedirectResponse(url=f"/admin/modify_product/{id_product}?error={str(e)}", status_code=status.HTTP_303_SEE_OTHER)
    
    return RedirectResponse(url=f"/admin/modify_product/{id_product}", status_code=status.HTTP_303_SEE_OTHER)