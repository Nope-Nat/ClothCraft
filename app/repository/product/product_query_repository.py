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
    async def get_products(category_id: Optional[int] = None, tag_ids: List[int] = None, size_ids: List[int] = None, include_inactive: bool = False, limit: Optional[int] = None):
        """Get products with optional filtering by category, tags, and sizes."""
        conditions = []
        params = []
        param_counter = 1
        
        if not include_inactive:
            conditions.append("p.active = true")
        
        if category_id:
            conditions.append(f"p.id_category = ${param_counter}")
            params.append(category_id)
            param_counter += 1
        
        if tag_ids:
            placeholders = ",".join([f"${i}" for i in range(param_counter, param_counter + len(tag_ids))])
            conditions.append(f"p.id_product IN (SELECT tp.id_product FROM tag_product tp WHERE tp.id_tag IN ({placeholders}))")
            params.extend(tag_ids)
            param_counter += len(tag_ids)
        
        if size_ids:
            placeholders = ",".join([f"${i}" for i in range(param_counter, param_counter + len(size_ids))])
            conditions.append(f"""
                p.id_product IN (
                    SELECT DISTINCT v.id_product 
                    FROM variant v 
                    JOIN variant_size vs ON v.id_variant = vs.id_variant 
                    WHERE vs.id_size IN ({placeholders})
                )
            """)
            params.extend(size_ids)
            param_counter += len(size_ids)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        limit_clause = f"LIMIT ${param_counter}" if limit else ""
        if limit:
            params.append(limit)
        
        query = f"""
            SELECT 
                p.id_product,
                p.name,
                p.active,
                p.thumbnail_path,
                c.name as category_name,
                ppv.price as current_price,
                COALESCE(
                    ppv.price * (1 - COALESCE(
                        (SELECT MAX(dh.discount) 
                         FROM discount_history dh 
                         WHERE dh.id_product = p.id_product 
                           AND dh."from" <= NOW() 
                           AND (dh."to" IS NULL OR dh."to" >= NOW())
                           AND dh.secret_code IS NULL), 0) / 100),
                    ppv.price
                ) as discounted_price,
                array_agg(DISTINCT t.name) FILTER (WHERE t.name IS NOT NULL) as tags
            FROM product p
            LEFT JOIN category c ON p.id_category = c.id_category
            LEFT JOIN product_price_view ppv ON p.id_product = ppv.id_product
            LEFT JOIN tag_product tp ON p.id_product = tp.id_product
            LEFT JOIN tag t ON tp.id_tag = t.id_tag
            {where_clause}
            GROUP BY p.id_product, p.name, p.active, p.thumbnail_path, c.name, ppv.price
            ORDER BY p.created_at DESC
            {limit_clause}
        """
        
        async with db.get_connection() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]
