from fastapi import APIRouter, HTTPException, status, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from model.auth_model import UserResponse, LoginRequest, RegisterRequest
from repository.auth_repository import auth_repo
from utils.auth_utils import set_session_cookie, clear_session_cookie

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/auth", tags=["authentication"])

def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    return request.client.host

def get_device_details(request: Request) -> str:
    """Get basic device details from headers"""
    user_agent = request.headers.get("user-agent", "Unknown")
    return user_agent[:200]  # Limit length

def format_validation_errors(errors) -> str:
    """Format Pydantic validation errors into a readable message"""
    error_messages = []
    for error in errors:
        field = error['loc'][-1] if error['loc'] else 'field'
        message = error['msg']
        error_messages.append(f"{field.replace('_', ' ').title()}: {message}")
    return "; ".join(error_messages)

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    """Display login form"""
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "error": error
    })

@router.post("/login")
async def login(
    request: Request, 
    email: str = Form(...),
    password: str = Form(...)
):
    """Process login form"""
    try:
        # Validate using Pydantic model
        login_data = LoginRequest(email=email, password=password)
    except ValidationError as e:
        error_message = format_validation_errors(e.errors())
        return RedirectResponse(
            url=f"/auth/login?error={error_message}",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
    # Verify user credentials
    user = await auth_repo.verify_user(login_data.email, login_data.password)
    
    if not user:
        return RedirectResponse(
            url="/auth/login?error=Invalid email or password",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
    # Create session
    session = await auth_repo.create_session(
        user_id=user.id_user,
        ip=get_client_ip(request),
        device_details=get_device_details(request)
    )
    
    if not session:
        return RedirectResponse(
            url="/auth/login?error=Failed to create session",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
    # Create redirect response to home page
    redirect_response = RedirectResponse(
        url="/",
        status_code=status.HTTP_303_SEE_OTHER
    )
    
    # Set session cookie using utility function
    set_session_cookie(redirect_response, session.id_session)
    
    return redirect_response

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, error: str = None):
    """Display registration form"""
    return templates.TemplateResponse("auth/register.html", {
        "request": request,
        "error": error
    })

@router.post("/register")
async def register(
    request: Request,
    response: Response,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    terms: str = Form(None)  # Change back to str to handle checkbox properly
):
    """Process registration form"""
    try:
        # Convert checkbox value to boolean properly
        # HTML checkboxes send "on" or the value when checked, None when unchecked
        terms_bool = terms is not None and terms.lower() in ["on", "true", "1", "agreed"]
        
        # Validate using Pydantic model
        register_data = RegisterRequest(
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password,
            terms=terms_bool
        )
    except ValidationError as e:
        error_message = format_validation_errors(e.errors())
        return RedirectResponse(
            url=f"/auth/register?error={error_message}",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
    # Create new user (only after all validation passes)
    user = await auth_repo.create_user(
        username=register_data.username,
        email=register_data.email,
        password=register_data.password
    )
    
    if not user:
        return RedirectResponse(
            url="/auth/register?error=Failed to create user. Username may already exist.",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
    # Create session for new user
    session = await auth_repo.create_session(
        user_id=user.id_user,
        ip=get_client_ip(request),
        device_details=get_device_details(request)
    )
    
    # Create redirect response to home page
    redirect_response = RedirectResponse(
        url="/",
        status_code=status.HTTP_303_SEE_OTHER
    )
    
    if session:
        # Set session cookie using utility function
        set_session_cookie(redirect_response, session.id_session)
    
    return redirect_response

@router.post("/logout")
async def logout(request: Request):
    """Process logout"""
    session_id = request.cookies.get("session_id")
    
    if session_id:
        try:
            # Delete session from database
            await auth_repo.delete_session(int(session_id))
        except (ValueError, TypeError):
            pass  # Invalid session ID format
    
    # Create redirect response
    redirect_response = RedirectResponse(
        url="/auth/login",
        status_code=status.HTTP_303_SEE_OTHER
    )
    
    # Clear session cookie using utility function
    clear_session_cookie(redirect_response)
    
    return redirect_response


