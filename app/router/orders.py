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
    # Check if user is authenticated
    current_user = await get_current_user(request)
    
    if not current_user:
        return RedirectResponse(
            url="/auth/login?error=Please login to view your orders",
            status_code=303
        )
    
    # Get user's orders
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
        print(f"Processing return for order {order_id} by user {current_user.user_id}")
        
        if not current_user:
            return RedirectResponse(
                url="/auth/login?error=Please login to perform this action",
                status_code=303
            )
        
        # Verify order belongs to user and is in delivered status
        order = await order_repo.get_order(order_id)
        print(f"Found order: {order.id_order if order else None} for user {order.user_id if order else None}")
        
        if not order or order.user_id != current_user.user_id:
            print(f"Order validation failed: order exists: {order is not None}, user match: {order.user_id if order else None} == {current_user.user_id}")
            return RedirectResponse(
                url="/orders?error=Invalid order or unauthorized access",
                status_code=303
            )
        
        if order.current_status != OrderStatus.DELIVERED:
            return RedirectResponse(
                url=f"/orders?error=Order {order_id} cannot be returned - wrong status: {order.current_status}",
                status_code=303
            )
        
        # Update order status
        success = await order_repo.update_order_status(order_id, OrderStatus.RETURN_REQUESTED.value)
        
        if not success:
            return RedirectResponse(
                url=f"/orders?error=Failed to update status for order {order_id}",
                status_code=303
            )
        
        return RedirectResponse(
            url="/orders?success=OK",
            status_code=303
        )
        
    except Exception as e:
        return RedirectResponse(
            url=f"/orders?error=Error processing return: {str(e)}",
            status_code=303
        )