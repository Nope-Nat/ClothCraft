from typing import Optional, List
from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from utils.auth_utils import verify_admin_access
from repository.product_repository import ProductRepository
from repository.order_repository import order_repo
from repository.discount_repository import discount_repo
from template import templates
import os

from markupsafe import Markup
from db import db
import markdown
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/admin")

@router.get("/", response_class=HTMLResponse)
async def admin_page(request: Request):
    await verify_admin_access(request)

    return await templates.TemplateResponse("admin/admin.html", {
        "request": request,
    })

@router.get("/orders", response_class=HTMLResponse)
async def admin_orders_page(request: Request, status: Optional[str] = None):
    """Admin orders management page with filtering"""
    await verify_admin_access(request)
    
    # Get all orders with optional status filtering
    orders = await order_repo.get_all_orders(status)
    
    # Get available statuses for filter dropdown
    available_statuses = await order_repo.get_available_statuses()
    
    return await templates.TemplateResponse("admin/orders.html", {
        "request": request,
        "orders": orders,
        "available_statuses": available_statuses,
        "selected_status": status
    })

@router.post("/orders/{order_id}/update-status")
async def update_order_status(request: Request, order_id: int, new_status: str = Form()):
    """Update order status"""
    await verify_admin_access(request)
    
    try:
        success = await order_repo.update_order_status_admin(order_id, new_status)
        
        if success:
            return RedirectResponse(url="/admin/orders?success=Order status updated successfully", status_code=303)
        else:
            return RedirectResponse(url="/admin/orders?error=Failed to update order status", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/admin/orders?error=Failed to update order status: {str(e)}", status_code=303)

@router.get("/discounts", response_class=HTMLResponse)
async def admin_discounts_page(request: Request, coupon_code: Optional[str] = None, status: Optional[str] = None):
    """Admin discounts management page with filtering"""
    await verify_admin_access(request)
    
    # Get all discounts with optional filtering
    discounts = await discount_repo.get_discounts_with_filters(coupon_code, status)
    
    return await templates.TemplateResponse("admin/discounts.html", {
        "request": request,
        "discounts": discounts,
        "selected_coupon_code": coupon_code,
        "selected_status": status
    })

@router.get("/discounts/new", response_class=HTMLResponse)
async def admin_new_discount_page(request: Request):
    """Create new discount page"""
    await verify_admin_access(request)
    
    # Get categories, tags, and products for the form
    categories = await discount_repo.get_all_categories()
    tags = await discount_repo.get_all_tags()
    products = await discount_repo.get_all_products_minimal()
    
    return await templates.TemplateResponse("admin/new_discount.html", {
        "request": request,
        "categories": categories,
        "tags": tags,
        "products": products
    })

@router.get("/discounts/{discount_id}", response_class=HTMLResponse)
async def admin_discount_details(request: Request, discount_id: int):
    """View detailed information about a specific discount"""
    await verify_admin_access(request)
    
    # Get discount details
    discount = await discount_repo.get_discount_details(discount_id)
    if not discount:
        return RedirectResponse(url="/admin/discounts?error=Discount not found", status_code=303)
    
    # Get affected products
    affected_products = await discount_repo.get_discount_affected_products(discount_id)
    
    return await templates.TemplateResponse("admin/discount_details.html", {
        "request": request,
        "discount": discount,
        "affected_products": affected_products
    })

@router.post("/discounts/preview", response_class=HTMLResponse)
async def preview_discount_affected_products(request: Request):
    """AJAX endpoint to preview affected products based on form selections"""
    await verify_admin_access(request)
    
    # Parse form data
    form_data = await request.form()
    category_ids = [int(x) for x in form_data.getlist('categories') if x]
    tag_ids = [int(x) for x in form_data.getlist('tags') if x]
    product_ids = [int(x) for x in form_data.getlist('products') if x]
    
    # Get affected products
    affected_products = await discount_repo.get_affected_products_preview(
        category_ids=category_ids,
        tag_ids=tag_ids,
        product_ids=product_ids
    )
    
    return await templates.TemplateResponse("admin/discount_preview.html", {
        "request": request,
        "affected_products": affected_products
    })

@router.post("/discounts/new")
async def create_new_discount(
    request: Request,
    percentage: float = Form(...),
    coupon_code: Optional[str] = Form(None),
    from_date: str = Form(...),
    to_date: Optional[str] = Form(None),
    categories: List[int] = Form(default=[]),
    tags: List[int] = Form(default=[]),
    products: List[int] = Form(default=[])
):
    """Create a new discount"""
    await verify_admin_access(request)
    
    try:
        # Validate percentage
        if percentage <= 0 or percentage > 100:
            return RedirectResponse(
                url="/admin/discounts/new?error=Discount percentage must be between 0 and 100",
                status_code=303
            )
        
        # Validate that at least one selection is made
        if not categories and not tags and not products:
            return RedirectResponse(
                url="/admin/discounts/new?error=Please select at least one category, tag, or product",
                status_code=303
            )
        
        # Clean up coupon code
        clean_coupon_code = coupon_code.strip().upper() if coupon_code and coupon_code.strip() else None
        
        # Clean up to_date
        clean_to_date = to_date if to_date and to_date.strip() else None
        
        # Create the discount
        success = await discount_repo.create_discount(
            percentage=percentage,
            coupon_code=clean_coupon_code,
            from_date=from_date,
            to_date=clean_to_date,
            category_ids=categories,
            tag_ids=tags,
            product_ids=products
        )
        
        if success:
            return RedirectResponse(
                url="/admin/discounts?success=Discount created successfully",
                status_code=303
            )
        else:
            return RedirectResponse(
                url="/admin/discounts/new?error=Failed to create discount. Please check your selections.",
                status_code=303
            )
            
    except ValueError as e:
        return RedirectResponse(
            url=f"/admin/discounts/new?error=Invalid input: {str(e)}",
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/admin/discounts/new?error=Error creating discount: {str(e)}",
            status_code=303
        )