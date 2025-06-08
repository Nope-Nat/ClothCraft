from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from utils.auth_utils import verify_admin_access
from repository.product_repository import ProductRepository
from repository.order_repository import order_repo
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