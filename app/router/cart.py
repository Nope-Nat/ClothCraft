from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from repository.cart_repository import cart_repo
from utils.auth_utils import get_current_user
from template import templates
from typing import Optional

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
    
    # Get coupon code from cookies
    coupon_code = request.cookies.get("coupon_code")
    
    # Get user's cart items with pricing
    cart = await cart_repo.get_user_cart(current_user.user_id, coupon_code)
    
    return await templates.TemplateResponse("cart.html", {
        "request": request,
        "cart": cart
    })

@router.post("/add")
async def add_to_cart(
    request: Request,
    variant_size_id: int = Form(..., alias="variant_size_id"),
    quantity: int = Form(default=1),
    callback: Optional[str] = Query(default=None)
):
    """Add variant size to cart and redirect back to callback URL"""
    # Check if user is authenticated
    current_user = await get_current_user(request)
    
    if not current_user:
        callback_url = callback or request.headers.get("referer", "/")
        return RedirectResponse(
            url=f"/auth/login?error=Please login to add items to cart&callback={callback_url}",
            status_code=303
        )
    
    try:
        # Add item to cart
        success = await cart_repo.add_to_cart(
            user_id=current_user.user_id,
            variant_size_id=variant_size_id,
            quantity=quantity
        )
        
        if success:
            # Determine redirect URL
            redirect_url = callback or request.headers.get("referer", "/cart")
            return RedirectResponse(url=redirect_url, status_code=303)
        else:
            # Failed to add to cart
            redirect_url = callback or request.headers.get("referer", "/")
            return RedirectResponse(
                url=f"{redirect_url}?error=Failed to add item to cart",
                status_code=303
            )
    except Exception as e:
        # Handle any errors
        redirect_url = callback or request.headers.get("referer", "/")
        return RedirectResponse(
            url=f"{redirect_url}?error=Error adding item to cart",
            status_code=303
        )

@router.post("/remove")
async def remove_from_cart(
    request: Request,
    variant_size_id: int = Form(..., alias="variant_size_id"),
    callback: Optional[str] = Query(default=None)
):
    """Remove item from cart"""
    # Check if user is authenticated
    current_user = await get_current_user(request)
    
    if not current_user:
        return RedirectResponse(
            url="/auth/login?error=Please login to modify cart",
            status_code=303
        )
    
    try:
        success = await cart_repo.remove_from_cart(
            user_id=current_user.user_id,
            variant_size_id=variant_size_id
        )
        
        redirect_url = callback or "/cart"
        if success:
            return RedirectResponse(url=redirect_url, status_code=303)
        else:
            return RedirectResponse(
                url=f"{redirect_url}?error=Failed to remove item from cart",
                status_code=303
            )
    except Exception as e:
        redirect_url = callback or "/cart"
        return RedirectResponse(
            url=f"{redirect_url}?error=Error removing item from cart",
            status_code=303
        )

@router.post("/coupon")
async def apply_coupon(
    request: Request,
    coupon_code: str = Form(..., alias="coupon_code")
):
    """Apply or remove coupon code"""
    # Check if user is authenticated
    current_user = await get_current_user(request)
    
    if not current_user:
        return RedirectResponse(
            url="/auth/login?error=Please login to apply coupons",
            status_code=303
        )
    
    response = RedirectResponse(url="/cart/", status_code=303)
    
    if coupon_code and coupon_code.strip():
        # Set coupon code in cookie (expires in 30 days)
        response.set_cookie(
            key="coupon_code",
            value=coupon_code.strip().upper(),
            max_age=30*24*60*60,  # 30 days
            httponly=True
        )
    else:
        # Remove coupon code
        response.delete_cookie("coupon_code")
    
    return response


