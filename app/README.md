# ClothCraft API Examples

This document provides examples and patterns for implementing routers, repositories, and models in the ClothCraft API.

## Model

Models use Pydantic for validation and serialization. They define the data structure and validation rules.

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserModel(BaseModel):
    id: int
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    is_active: bool = True
    created_at: datetime
    
    # Config class is optional - only needed for specific behaviors
    class Config:
        # Allows creating model from database row objects (asyncpg.Record)
        from_attributes = True
        
        # Custom JSON serialization for specific types
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Simple models without Config class (most common case)
class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

# When Config is NOT needed (default behavior works fine):
class SimpleProduct(BaseModel):
    name: str
    price: float
    # No Config needed - Pydantic handles basic types automatically
```

**When to use Config class:**
- `from_attributes = True`: When creating models from database rows (`UserModel(**dict(row))`)
- `json_encoders`: When you need custom serialization (e.g., datetime formatting)
- `validate_assignment = True`: When you want validation on field assignment after creation
- `alias_generator`: When database field names differ from Python conventions

**Most models don't need Config** - use it only when you need specific behavior.

## Repository

Repositories handle database operations using raw SQL queries with asyncpg. They abstract database logic from business logic.

```python
from typing import List, Optional
from db import db
from models.user import UserModel

class UserRepository:
    
    async def create_user(self, username: str, email: str, password_hash: str) -> UserModel:
        """Create a new user with parameterized query"""
        query = """
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES ($1, $2, $3, now())
            RETURNING id, username, email, is_active, created_at
        """
        
        async with db.get_connection() as conn:
            row = await conn.fetchrow(query, username, email, password_hash)
            return UserModel(**dict(row))
    
    async def get_user_by_id(self, user_id: int) -> Optional[UserModel]:
        """Get user by ID with error handling"""
        query = """
            SELECT id, username, email, is_active, created_at
            FROM users 
            WHERE id = $1 AND is_active = true
        """
        
        async with db.get_connection() as conn:
            row = await conn.fetchrow(query, user_id)
            return UserModel(**dict(row)) if row else None
    
    async def update_user_status(self, user_id: int, is_active: bool) -> bool:
        """Update user status and return success"""
        query = """
            UPDATE users 
            SET is_active = $2, updated_at = now()
            WHERE id = $1
        """
        
        async with db.get_connection() as conn:
            result = await conn.execute(query, user_id, is_active)
            return result == "UPDATE 1"
    
    async def search_users(self, search_term: str, limit: int = 10) -> List[UserModel]:
        """Search users with LIKE pattern"""
        query = """
            SELECT id, username, email, is_active, created_at
            FROM users 
            WHERE (username ILIKE $1 OR email ILIKE $1) 
            AND is_active = true
            ORDER BY username
            LIMIT $2
        """
        
        async with db.get_connection() as conn:
            rows = await conn.fetch(query, f"%{search_term}%", limit)
            return [UserModel(**dict(row)) for row in rows]

# Global repository instance
user_repo = UserRepository()
```

## Router

Routers define API endpoints using FastAPI. They handle HTTP requests, validation, and responses.

```python
from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from models.user import UserCreateRequest, UserResponse
from repository.user_repository import user_repo

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreateRequest):
    """Create a new user"""
    try:
        # Hash password (simplified for example)
        password_hash = hash_password(user_data.password)
        
        user = await user_repo.create_user(
            username=user_data.username,
            email=user_data.email,
            password_hash=password_hash
        )
        
        return UserResponse(**user.dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {str(e)}"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get user by ID"""
    user = await user_repo.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**user.dict())

@router.get("/", response_model=List[UserResponse])
async def search_users(
    q: str = Query(..., min_length=2, description="Search term"),
    limit: int = Query(default=10, ge=1, le=100)
):
    """Search users by username or email"""
    users = await user_repo.search_users(search_term=q, limit=limit)
    return [UserResponse(**user.dict()) for user in users]

@router.patch("/{user_id}/status")
async def update_user_status(user_id: int, is_active: bool):
    """Update user active status"""
    success = await user_repo.update_user_status(user_id, is_active)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or update failed"
        )
    
    return {"message": "User status updated successfully"}

# Include in main app
# app.include_router(router)
```

## Templates

Templates use Jinja2 for rendering HTML pages. They support template inheritance and component inclusion.

### Basic Template Structure

```html
<!-- base.html - Base template with common structure -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}ClothCraft{% endblock %}</title>
    {% block head %}{% endblock %}
</head>
<body>
    {% include "navbar.html" %}
    
    <main>
        {% block content %}
        <h1>Welcome to ClothCraft</h1>
        <p>Your premium clothing store</p>
        {% endblock %}
    </main>
    
    {% include "footer.html" %}
</body>
</html>
```

### Page Template Example

```html
<!-- product_list.html - Extends base template -->
{% extends "base.html" %}

{% block title %}Products - ClothCraft{% endblock %}

{% block content %}
<h1>Our Products</h1>

{% if products %}
    {% for product in products %}
    <div class="product-card">
        <h3>{{ product.name }}</h3>
        <p>{{ product.short_description }}</p>
        <p>Price: ${{ "%.2f"|format(product.price) }}</p>
        
        {% if product.published %}
            <span class="status-available">Available</span>
        {% else %}
            <span class="status-unavailable">Not Available</span>
        {% endif %}
    </div>
    {% endfor %}
{% else %}
    <p>No products available.</p>
{% endif %}
{% endblock %}
```

### Router with Template Response

```python
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_class=HTMLResponse)
async def products_page(request: Request):
    """Products page with template"""
    products = await product_repo.get_published_products()
    
    return templates.TemplateResponse("product_list.html", {
        "request": request,
        "products": products,
        "total_count": len(products)
    })

@router.get("/{product_id}", response_class=HTMLResponse)
async def product_detail_page(request: Request, product_id: int):
    """Product detail page"""
    product = await product_repo.get_product_by_id(product_id)
    
    if not product:
        return templates.TemplateResponse("404.html", {
            "request": request,
            "message": "Product not found"
        }, status_code=404)
    
    variants = await variant_repo.get_variants_by_product(product_id)
    
    return templates.TemplateResponse("product_detail.html", {
        "request": request,
        "product": product,
        "variants": variants
    })
```

### Template with Forms

```html
<!-- user_form.html - Form example -->
{% extends "base.html" %}

{% block content %}
<h1>Create Account</h1>

<form method="post" action="/users/">
    <div>
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required>
    </div>
    
    <div>
        <label for="email">Email:</label>
        <input type="email" id="email" name="email" required>
    </div>
    
    <div>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required>
    </div>
    
    <button type="submit">Create Account</button>
</form>

{% if errors %}
    <div class="errors">
        {% for error in errors %}
            <p>{{ error }}</p>
        {% endfor %}
    </div>
{% endif %}
{% endblock %}
```

### Template Filters and Functions

```python
# In router - passing data to template
return templates.TemplateResponse("products.html", {
    "request": request,
    "products": products,
    "current_time": datetime.now(),
    "user_authenticated": bool(request.user),
    "categories": await category_repo.get_categories()
})
```

```html
<!-- Using filters and conditionals in template -->
{% for product in products %}
    <div>
        <h3>{{ product.name|title }}</h3>
        <p>Created: {{ product.created_at.strftime("%Y-%m-%d") }}</p>
        
        {% if product.price > 50 %}
            <span class="premium">Premium Item</span>
        {% endif %}
        
        <!-- Loop controls -->
        {% if loop.first %}<div class="first-item">{% endif %}
        {% if loop.last %}</div>{% endif %}
    </div>
{% endfor %}
```

## Best Practices

### Error Handling
```python
from fastapi import HTTPException, status

# Repository level - let exceptions bubble up
async def get_item(self, item_id: int):
    query = "SELECT * FROM items WHERE id = $1"
    async with db.get_connection() as conn:
        row = await conn.fetchrow(query, item_id)
        if not row:
            return None  # Return None, don't raise here
        return ItemModel(**dict(row))

# Router level - handle business logic
@router.get("/{item_id}")
async def get_item(item_id: int):
    item = await item_repo.get_item(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return item
```

### Database Transactions
```python
async def transfer_items(self, from_id: int, to_id: int, quantity: int):
    """Example of transaction handling"""
    async with db.get_connection() as conn:
        async with conn.transaction():
            # Multiple operations in single transaction
            await conn.execute(
                "UPDATE inventory SET quantity = quantity - $1 WHERE id = $2",
                quantity, from_id
            )
            await conn.execute(
                "UPDATE inventory SET quantity = quantity + $1 WHERE id = $2", 
                quantity, to_id
            )
```

### Query Building
```python
def build_search_query(filters: dict) -> tuple[str, list]:
    """Dynamic query building"""
    conditions = ["active = true"]
    params = []
    param_count = 1
    
    if filters.get("category"):
        conditions.append(f"category_id = ${param_count}")
        params.append(filters["category"])
        param_count += 1
    
    if filters.get("price_min"):
        conditions.append(f"price >= ${param_count}")
        params.append(filters["price_min"])
        param_count += 1
    
    query = f"""
        SELECT * FROM products 
        WHERE {" AND ".join(conditions)}
        ORDER BY created_at DESC
    """
    
    return query, params
```