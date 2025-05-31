from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import os

from markupsafe import Markup
from db import db
import markdown

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/category")

@router.get("/{id_category}")
async def category_page(request: Request, id_category: int):
    return {"message": "Category endpoint is working", "id_category": id_category}