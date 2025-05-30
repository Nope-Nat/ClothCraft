from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from router.health import router as health_router
from db import db

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change this in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(health_router)

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    await db.connect()

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await db.disconnect()

@app.get("/")
async def root():
    return {"message": "Hello, World4!"}