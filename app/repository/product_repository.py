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
    async def get_all_sizes():
        async with db.get_connection() as conn:
            return await conn.fetch("""
                SELECT DISTINCT 
                    s.id_size,
                    concat(f.value, ' ', sf.value) as name
                FROM size s
                JOIN size_data sf ON s.id_size = sf.id_size
                JOIN sizing_format f ON sf.id_sizing_format = f.id_sizing_format
                ORDER BY name
            """)

    @staticmethod
    async def get_category_hierarchy(category_id: Optional[int] = None):
        async with db.get_connection() as conn:
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
                subcategories = await conn.fetch("""
                    SELECT id_category, name
                    FROM category
                    WHERE parent_category IS NULL
                    ORDER BY name
                """)
                
            return {"breadcrumbs": breadcrumbs, "subcategories": subcategories}

    async def get_product_variants(product_id: int):
        async with db.get_connection() as conn:
            query = """
                SELECT id_variant, name, color
                FROM variant
                WHERE id_product = $1 AND active = true;
            """
            return await conn.fetch(query, product_id)

    async def get_product_sizing_formats(product_id: int):
        """Get all available sizing formats for a product"""
        async with db.get_connection() as conn:
            query = """
                SELECT DISTINCT sf.id_sizing_format, sf.value as format_name
                FROM product p
                JOIN variant v ON p.id_product = v.id_product
                JOIN variant_size vs ON v.id_variant = vs.id_variant
                JOIN size s ON vs.id_size = s.id_size
                JOIN size_data sd ON s.id_size = sd.id_size
                JOIN sizing_format sf ON sd.id_sizing_format = sf.id_sizing_format
                WHERE p.id_product = $1 AND v.active = true
                ORDER BY sf.id_sizing_format
            """
            return await conn.fetch(query, product_id)

    async def get_product_variant_sizes(id_variant: int, format_id: int = None):
        """Get sizes for variant in specific format, default to first available format"""
        async with db.get_connection() as conn:
            # If no format specified, get the first available format
            if format_id is None:
                format_query = """
                    SELECT sf.id_sizing_format
                    FROM variant_size vs
                    JOIN size s ON vs.id_size = s.id_size
                    JOIN size_data sd ON s.id_size = sd.id_size
                    JOIN sizing_format sf ON sd.id_sizing_format = sf.id_sizing_format
                    WHERE vs.id_variant = $1
                    ORDER BY sf.id_sizing_format
                    LIMIT 1
                """
                format_result = await conn.fetchrow(format_query, id_variant)
                if format_result:
                    format_id = format_result['id_sizing_format']
                else:
                    return []

            query = """
                SELECT 
                    s.id_size,
                    s."order" as size_order,
                    vs.id_variant_size,
                    sd.value as size_value
                FROM variant_size vs
                JOIN size s ON vs.id_size = s.id_size
                JOIN size_data sd ON s.id_size = sd.id_size
                WHERE vs.id_variant = $1 AND sd.id_sizing_format = $2
                ORDER BY s."order"
            """
            return await conn.fetch(query, id_variant, format_id)

    @staticmethod
    async def get_total_discount_for_product_at_moment(product_id: int):
        async with db.get_connection() as conn:
            query = """
                SELECT 
                    (total_discount_for_product_at_moment($1, CURRENT_TIMESTAMP::TIMESTAMP, NULL)).total_discount,
                    (total_discount_for_product_at_moment($1, CURRENT_TIMESTAMP::TIMESTAMP, NULL)).shortest_discount_from,
                    (total_discount_for_product_at_moment($1, CURRENT_TIMESTAMP::TIMESTAMP, NULL)).shortest_discount_to;
            """
            return await conn.fetchrow(query, product_id)

    @staticmethod
    async def get_min_price_30_days(product_id: int):
        async with db.get_connection() as conn:
            query = """
                SELECT 
                    (get_min_price_30_days($1)) as min_price;
            """
            return await conn.fetchrow(query, product_id)

    @staticmethod
    async def get_product(product_id: int):
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
        async with db.get_connection() as conn:
            base_query = """
                SELECT 
                    p.id_product, 
                    p.name, 
                    p.thumbnail_path, 
                    c.name as category_name,
                    (SELECT price 
                    FROM price_history ph 
                    WHERE ph.id_product = p.id_product 
                    ORDER BY created_at DESC 
                    LIMIT 1) as current_price,
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
        """Get recently added products for home page"""
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