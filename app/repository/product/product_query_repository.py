from typing import List, Optional
from db import db

class ProductQueryRepository:
    """Repository for product search and filtering operations."""
    
    @staticmethod
    async def get_product(product_id: int):
        """Get detailed product information by ID."""
        async with db.get_connection() as conn:
            query = """
                SELECT
                    p.id_product, p.name, p.id_category, c.name as category_name,
                    p.sku_code,
                    p.thumbnail_path,
                    (
                        SELECT array_agg(img_path ORDER BY "order")
                        FROM product_image pi
                        WHERE pi.id_product = p.id_product
                    ) as images_paths,
                    (
                        SELECT array_agg(alt_desc ORDER BY "order")
                        FROM product_image pi
                        WHERE pi.id_product = p.id_product
                    ) as images_alt_descriptions,
                    p.short_description,
                    (
                        SELECT description
                        FROM product_details_history pdh
                        WHERE pdh.id_product = p.id_product
                        ORDER BY pdh.created_at DESC
                        LIMIT 1
                    ) as description,
                    (
                        SELECT price 
                        FROM price_history ph 
                        WHERE ph.id_product = p.id_product 
                        ORDER BY created_at DESC 
                        LIMIT 1
                    ) as current_price,
                    array_agg(DISTINCT t.name) FILTER (WHERE t.id_tag IS NOT NULL) as tags
                FROM product p
                LEFT JOIN category c ON p.id_category = c.id_category
                LEFT JOIN tag_product tp ON p.id_product = tp.id_product
                LEFT JOIN tag t ON tp.id_tag = t.id_tag
                WHERE p.id_product = $1
                GROUP BY p.id_product, c.name;
            """
            return await conn.fetchrow(query, product_id)

    @staticmethod
    async def get_products(category_id: Optional[int] = None, tag_ids: List[int] = None, size_ids: List[int] = None):
        """Get products with optional filtering by category, tags, and sizes."""
        async with db.get_connection() as conn:
            base_query = """
                SELECT 
                    p.id_product, 
                    p.name, 
                    p.thumbnail_path, 
                    c.name as category_name,
                    get_product_regular_price(p.id_product) as current_price,
                    get_product_discounted_price(p.id_product, NULL) as discounted_price,
                    array_agg(DISTINCT t.name) FILTER (WHERE t.id_tag IS NOT NULL) as tags,
                    array_agg(DISTINCT concat(sf.value, ' ', f.value)) 
                        FILTER (WHERE sf.id_sizing_format IS NOT NULL) as sizes
                FROM product p
                LEFT JOIN category c ON p.id_category = c.id_category
                LEFT JOIN tag_product tp ON p.id_product = tp.id_product
                LEFT JOIN tag t ON tp.id_tag = t.id_tag
                LEFT JOIN variant v ON v.id_product = p.id_product
                LEFT JOIN variant_size vs ON vs.id_variant = v.id_variant
                LEFT JOIN size s ON vs.id_size = s.id_size
                LEFT JOIN size_data sf ON s.id_size = sf.id_size
                LEFT JOIN sizing_format f ON sf.id_sizing_format = f.id_sizing_format
            """

            conditions = ["p.active = true"]
            params = []
            param_count = 1

            if category_id is not None:
                conditions.append(f"""
                    p.id_category IN (
                        WITH RECURSIVE category_tree AS (
                            SELECT id_category FROM category WHERE id_category = ${param_count}
                            UNION ALL
                            SELECT c.id_category FROM category c
                            JOIN category_tree ct ON c.parent_category = ct.id_category
                        )
                        SELECT id_category FROM category_tree
                    )
                """)
                params.append(category_id)
                param_count += 1

            if tag_ids and len(tag_ids) > 0:
                conditions.append(f"p.id_product IN (SELECT id_product FROM tag_product WHERE id_tag = ANY(${param_count}))")
                params.append(tag_ids)
                param_count += 1

            if size_ids and len(size_ids) > 0:
                conditions.append(f"p.id_product IN (SELECT DISTINCT p.id_product FROM product p JOIN variant v ON v.id_product = p.id_product JOIN variant_size vs ON vs.id_variant = v.id_variant WHERE vs.id_size = ANY(${param_count}))")
                params.append(size_ids)

            query = f"""
                {base_query}
                WHERE {' AND '.join(conditions)}
                GROUP BY p.id_product, p.name, p.thumbnail_path, c.name
                ORDER BY c.name, p.name
            """
            
            return await conn.fetch(query, *params)

    @staticmethod
    async def get_recent_products(limit: int = 10):
        """Get recently added products for home page."""
        async with db.get_connection() as conn:
            query = """
                SELECT p.id_product, p.name, p.thumbnail_path, p.short_description, c.name as category_name,
                    (SELECT price 
                    FROM price_history ph 
                    WHERE ph.id_product = p.id_product 
                    ORDER BY created_at DESC 
                    LIMIT 1) as current_price,
                    p.created_at
                FROM product p
                LEFT JOIN category c ON p.id_category = c.id_category
                WHERE p.active = true
                ORDER BY p.created_at DESC
                LIMIT $1
            """
            return await conn.fetch(query, limit)