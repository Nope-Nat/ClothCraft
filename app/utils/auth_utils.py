import os
from typing import Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, Response, status
from model.auth_model import UserSessionData
from repository.auth_repository import auth_repo

def set_session_cookie(response: Response, session_id: str, cookie_name: str = "session_id") -> None:
    """
    Set session cookie with environment-appropriate security settings
    
    Args:
        response: FastAPI Response object
        session_id: Session ID to store in cookie
        cookie_name: Name of the cookie (default: "session_id")
    """
    is_production = os.getenv("RELEASE", "false").lower() == "true"
    
    response.set_cookie(
        key=cookie_name,
        value=str(session_id),
        httponly=True,
        secure=is_production,  # Only send over HTTPS in production
        samesite="lax",
        max_age=30 * 24 * 60 * 60  # 30 days in seconds
    )

def clear_session_cookie(response: Response, cookie_name: str = "session_id") -> None:
    """
    Clear session cookie
    
    Args:
        response: FastAPI Response object
        cookie_name: Name of the cookie to clear (default: "session_id")
    """
    response.delete_cookie(key=cookie_name)

async def get_current_user(request: Request) -> Optional[UserSessionData]:
    """
    Get current user data from session cookie
    
    Args:
        request: FastAPI Request object
        
    Returns:
        UserSessionData if valid session exists, None otherwise
    """
    session_id = request.cookies.get("session_id")
    
    if not session_id:
        return None
    
    try:
        session_id_int = int(session_id)
        return await auth_repo.get_user_from_session(session_id_int)
    except (ValueError, TypeError):
        return None

def require_admin(user_data: Optional[UserSessionData]) -> bool:
    """
    Check if user is admin
    
    Args:
        user_data: User session data
        
    Returns:
        True if user is admin, False otherwise
    """
    return user_data is not None and user_data.is_admin

def require_auth(user_data: Optional[UserSessionData]) -> bool:
    """
    Check if user is authenticated
    
    Args:
        user_data: User session data
        
    Returns:
        True if user is authenticated, False otherwise
    """
    return user_data is not None

async def cleanup_old_sessions(days: int = 30) -> int:
    """
    Clean up sessions older than specified number of days
    
    Args:
        days: Number of days (default: 30)
        
    Returns:
        Number of sessions deleted
        
    Example:
        # Clean up sessions older than 30 days
        deleted_count = await cleanup_old_sessions(30)
        
        # Clean up sessions older than 7 days
        deleted_count = await cleanup_old_sessions(7)
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    return await auth_repo.delete_old_sessions(cutoff_date)

def get_session_cutoff_date(days: int = 30) -> datetime:
    """
    Get cutoff date for session cleanup
    
    Args:
        days: Number of days ago (default: 30)
        
    Returns:
        datetime object representing the cutoff date
        
    Example:
        # Get timestamp for 30 days ago
        cutoff = get_session_cutoff_date(30)
        
        # Get timestamp for 7 days ago  
        cutoff = get_session_cutoff_date(7)
    """
    return datetime.now() - timedelta(days=days)

async def verify_admin_access(request: Request):
    """Verify that the current user is an admin. Raises appropriate exceptions if not."""
    user_data = await get_current_user(request)
    
    if not require_admin(user_data):
        if not user_data:
            # Not authenticated - redirect to login
            raise HTTPException(
                status_code=status.HTTP_302_FOUND,
                detail="Authentication required",
                headers={"Location": "/auth/login"}
            )
        else:
            # Authenticated but not admin - return 403
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
    
    return user_data

from fastapi import HTTPException, Request, Depends
from typing import Optional
# ...existing code...

async def admin_required(request: Request) -> dict:
    """
    Dependency that ensures the user is logged in and is an admin.
    Raises HTTPException if not authorized.
    """
    user_data = await get_current_user(request)
    
    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )
    
    if not require_admin(user_data):
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    return user_data
