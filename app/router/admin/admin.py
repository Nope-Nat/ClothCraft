from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Form
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

router = APIRouter(prefix="/admin")

@router.get("/", response_class=HTMLResponse)
async def admin_page(request: Request):
    return await templates.TemplateResponse("admin/admin.html", {
        "request": request,
    })