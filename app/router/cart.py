from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from repository.cart_repository import cart_repo
from utils.auth_utils import get_current_user
from template import templates

router = APIRouter(prefix="/cart", tags=["cart"])

@router.get("/", response_class=HTMLResponse)
async def cart_page(request: Request):
    """Display user's cart"""
    # Check if user is authenticated
    current_user = await get_current_user(request)
    
    if not current_user:
        return RedirectResponse(
            url="/auth/login?error=Please login to view your cart",
            status_code=303
        )
    
    # Get user's cart items
    cart = await cart_repo.get_user_cart(current_user.user_id)
    
    return await templates.TemplateResponse("cart.html", {
        "request": request,
        "cart": cart
    })
