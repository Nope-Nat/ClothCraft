from fastapi import APIRouter, HTTPException
from db import db

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
