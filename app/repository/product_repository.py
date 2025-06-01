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
    async def get_category_hierarchy(category_id: Optional[int] = None):
        async with db.get_connection() as conn:
            # Get current category and its ancestors
            breadcrumb_query = """
                WITH RECURSIVE category_path AS (
                    SELECT id_category, name, parent_category, 1 as level
                    FROM category
                    WHERE id_category = $1
                    UNION ALL
                    SELECT c.id_category, c.name, c.parent_category, cp.level + 1
                    FROM category c
                    JOIN category_path cp ON c.id_category = cp.parent_category
                )
                SELECT * FROM category_path ORDER BY level DESC;
            """
            
            # Get subcategories of current category
            subcategories_query = """
                SELECT id_category, name
                FROM category
                WHERE parent_category = $1
                ORDER BY name
            """
            
            if category_id:
                breadcrumbs = await conn.fetch(breadcrumb_query, category_id)
                subcategories = await conn.fetch(subcategories_query, category_id)
            else:
                breadcrumbs = []
                # Get root categories (no parent)
                subcategories = await conn.fetch("""
                    SELECT id_category, name
                    FROM category
                    WHERE parent_category IS NULL
                    ORDER BY name
                """)
                
            return {"breadcrumbs": breadcrumbs, "subcategories": subcategories}

    @staticmethod
    async def get_products(category_id: Optional[int] = None, tag_ids: List[int] = None):
        async with db.get_connection() as conn:
            base_query = """
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
            """

            if category_id is not None:
                # Use CTE to get all subcategories
                query = f"""
                    WITH RECURSIVE category_tree AS (
                        -- Base case: selected category
                        SELECT id_category, name
                        FROM category
                        WHERE id_category = $1
                        
                        UNION ALL
                        
                        -- Recursive case: all subcategories
                        SELECT c.id_category, c.name
                        FROM category c
                        JOIN category_tree ct ON c.parent_category = ct.id_category
                    )
                    {base_query}
                    WHERE p.active = true 
                    AND p.id_category IN (SELECT id_category FROM category_tree)
                """
                params = [category_id]
                param_count = 2
            else:
                query = f"{base_query} WHERE p.active = true"
                params = []
                param_count = 1

            if tag_ids and len(tag_ids) > 0:
                query += f" AND p.id_product IN (SELECT id_product FROM tag_product WHERE id_tag = ANY(${param_count}))"
                params.append(tag_ids)
            
            query += """
                GROUP BY p.id_product, p.name, p.thumbnail_path, c.name
                ORDER BY c.name, p.name
            """
            
            return await conn.fetch(query, *params)
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
                ORDER BY p.name
            """
            
            return await conn.fetch(query, *params)