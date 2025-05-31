from typing import List, Optional
from db import db

class ProductRepository:
    @staticmethod
    async def get_all_categories():
        async with db.get_connection() as conn:
            return await conn.fetch("""
                SELECT id_category, name 
                FROM category 
                ORDER BY name
            """)

    @staticmethod
    async def get_products(category_id: Optional[int] = None):
        async with db.get_connection() as conn:
            query = """
                SELECT p.id_product, p.name, p.thumbnail_path, c.name as category_name,
                       (SELECT price 
                        FROM price_history ph 
                        WHERE ph.id_product = p.id_product 
                        ORDER BY created_at DESC 
                        LIMIT 1) as current_price
                FROM product p
                LEFT JOIN category c ON p.id_category = c.id_category
                WHERE p.active = true
            """
            
            params = []
            if category_id is not None:
                query += " AND p.id_category = $1"
                params.append(category_id)
            
            return await conn.fetch(query, *params)