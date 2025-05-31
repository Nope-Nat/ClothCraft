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
    async def get_all_tags():
        async with db.get_connection() as conn:
            return await conn.fetch("""
                SELECT id_tag, name
                FROM tag
                ORDER BY name
            """)

    @staticmethod
    async def get_products(category_id: Optional[int] = None, tag_ids: List[int] = None):
        async with db.get_connection() as conn:
            query = """
                SELECT p.id_product, p.name, p.thumbnail_path, c.name as category_name,
                    (SELECT price 
                    FROM price_history ph 
                    WHERE ph.id_product = p.id_product 
                    ORDER BY created_at DESC 
                    LIMIT 1) as current_price,
                    array_agg(t.name) FILTER (WHERE t.id_tag IS NOT NULL) as tags
                FROM product p
                LEFT JOIN category c ON p.id_category = c.id_category
                LEFT JOIN tag_product tp ON p.id_product = tp.id_product
                LEFT JOIN tag t ON tp.id_tag = t.id_tag
                WHERE p.active = true
            """
            
            params = []
            param_count = 1
            
            if category_id is not None:
                query += f" AND p.id_category = ${param_count}"
                params.append(category_id)
                param_count += 1
            
            if tag_ids and len(tag_ids) > 0:
                query += f" AND p.id_product IN (SELECT id_product FROM tag_product WHERE id_tag = ANY(${param_count}))"
                params.append(tag_ids)
            
            query += """
                GROUP BY p.id_product, p.name, p.thumbnail_path, c.name
            """
            
            return await conn.fetch(query, *params)