from typing import Optional, List
from fastapi import APIRouter, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from repository.product_repository import ProductRepository
from template import templates
import os

from markupsafe import Markup
from db import db
import markdown
from fastapi.responses import JSONResponse
from utils.auth_utils import verify_admin_access

router = APIRouter(prefix="/admin/modify_product")

@router.get("/{id_product}", response_class=HTMLResponse)
async def product_page(request: Request, id_product: int):
    # Verify admin access
    await verify_admin_access(request)
    
    return await templates.TemplateResponse("admin/modify_product.html", {
        "request": request,
        "id_product": id_product,
        })