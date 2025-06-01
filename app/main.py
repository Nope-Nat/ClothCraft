from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from router.health import router as health_router
from router.products import router as products_router
from router.product import router as product_router
from router.category import router as category_router
from router.auth import router as auth_router
from router.orders import router as orders_router
from db import db
from repository.product_repository import ProductRepository
from template import templates
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
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(health_router)     
app.include_router(products_router)
app.include_router(product_router)
app.include_router(category_router)
app.include_router(auth_router)
app.include_router(orders_router)

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    await db.connect()

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await db.disconnect()

@app.get("/")
async def root(request: Request):
    recent_products = await ProductRepository.get_recent_products(limit=10)
    return await templates.TemplateResponse("home.html", {
        "request": request, 
        "recent_products": recent_products
    })