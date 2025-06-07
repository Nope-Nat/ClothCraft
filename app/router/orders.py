from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from repository.order_repository import order_repo
from utils.auth_utils import get_current_user
from template import templates
from model.order_model import OrderStatus

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/", response_class=HTMLResponse)
async def orders_list(request: Request):
    """Display user's orders list"""
    current_user = await get_current_user(request)
    
    if not current_user:
        return RedirectResponse(
            url="/auth/login?error=Please login to view your orders",
            status_code=303
        )
    
    orders = await order_repo.get_user_orders(current_user.user_id)
    
    return await templates.TemplateResponse("order/list.html", {
        "request": request,
        "orders": orders,
        "OrderStatus": OrderStatus
    })

@router.post("/{order_id}/return", response_class=HTMLResponse)
async def request_return(request: Request, order_id: int):
    """Request return for a delivered order"""
    try:
        current_user = await get_current_user(request)
        
        if not current_user:
            return RedirectResponse(
                url="/auth/login?error=Please login to perform this action",
                status_code=303
            )
        
        order = await order_repo.get_order(order_id)
        
        if not order:
            return RedirectResponse(
                url="/orders?error=Order not found",
                status_code=303
            )
        
        if str(order.user_id) != str(current_user.user_id):
            return RedirectResponse(
                url="/orders?error=Unauthorized access",
                status_code=303
            )
        
        if order.current_status != OrderStatus.DELIVERED:
            return RedirectResponse(
                url="/orders?error=Order must be delivered before requesting return",
                status_code=303
            )

        success = await order_repo.update_order_status(order_id, OrderStatus.RETURN_REQUESTED.value)
        
        if not success:
            return RedirectResponse(
                url="/orders?error=Failed to update order status",
                status_code=303
            )

        return RedirectResponse(
            url="/orders?success=Return request submitted successfully",
            status_code=303
        )
        
    except Exception as e:
        return RedirectResponse(
            url=f"/orders?error=Error processing request: {str(e)}",
            status_code=303
        )