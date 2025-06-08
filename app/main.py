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
from router.cart import router as cart_router
from router.admin.admin import router as admin_router
from router.admin.new_product import router as new_product_router
from router.admin.modify_product import router as modify_product_router
from db import db
from repository.product.product_query_repository import ProductQueryRepository
from template import templates
import asyncio
import logging

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
app.include_router(cart_router)
app.include_router(admin_router)
app.include_router(new_product_router)
app.include_router(modify_product_router)

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup with retry logic"""
    max_retries = 10
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            await db.connect()
            logging.info("Database connection established successfully")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                logging.warning(f"Database connection attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 1.5, 30)  # Exponential backoff, max 30 seconds
            else:
                logging.error(f"Failed to connect to database after {max_retries} attempts: {e}")
                raise

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await db.disconnect()

@app.get("/")
async def root(request: Request):
    recent_products = await ProductQueryRepository.get_products(limit=12)
    return await templates.TemplateResponse("home.html", {
        "request": request, 
        "recent_products": recent_products
    })