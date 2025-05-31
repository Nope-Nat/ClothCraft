import os
from fastapi import Response

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
