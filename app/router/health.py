from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import os
from db import db

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

@router.get("/db")
async def database_health():
    """Database connectivity check"""
    try:
        async with db.get_connection() as conn:
            result = await conn.fetchval("SELECT 1")
            if result == 1:
                return {"status": "healthy", "message": "Database connection is working"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

@router.get("/status", response_class=HTMLResponse)
async def health_status_page(request: Request):
    """Health status page with template"""
    # Get API status
    api_status = {"status": "healthy", "message": "API is running"}
    
    # Get database status
    try:
        async with db.get_connection() as conn:
            result = await conn.fetchval("SELECT 1")
            if result == 1:
                db_status = {"status": "healthy", "message": "Database connection is working"}
            else:
                db_status = {"status": "unhealthy", "message": "Database query failed"}
    except Exception as e:
        db_status = {"status": "unhealthy", "message": "Database connection failed", "error": str(e)}
    
    return templates.TemplateResponse("health/status.html", {
        "request": request,
        "api_status": api_status,
        "db_status": db_status,
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "environment": os.getenv("ENVIRONMENT", "development")
    })
