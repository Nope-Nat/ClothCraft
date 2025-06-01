from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from repository.order_repository import order_repo
from utils.auth_utils import get_current_user

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/", response_class=HTMLResponse)
async def orders_list(request: Request):
    """Display user's orders list"""
    # Check if user is authenticated
    current_user = await get_current_user(request)
    
    if not current_user:
        return RedirectResponse(
            url="/auth/login?error=Please login to view your orders",
            status_code=303
        )
    
    # Get user's orders
    orders = await order_repo.get_user_orders(current_user.user_id)
    
    return templates.TemplateResponse("order/list.html", {
        "request": request,
        "current_user": current_user,
        "orders": orders
    })
