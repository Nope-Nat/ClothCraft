from db import db

class ProductDetailRepository:
    """Repository for product details, materials, tags, and discount information."""
    
    @staticmethod
    async def get_product_discount_info(product_id: int):
        """Get discount information for a product."""
        async with db.get_connection() as conn:
            query = """
                SELECT *
                FROM get_product_discount_info($1, NULL) as di;
            """
            return await conn.fetchrow(query, product_id)

    @staticmethod
    async def get_product_materials_info(product_id: int):
        """Get materials information for a product."""
        async with db.get_connection() as conn:
            query = """
                SELECT *
                FROM get_product_materials_info($1) as mi;
            """
            return await conn.fetch(query, product_id)

    @staticmethod
    async def get_product_tags_info(product_id: int):
        """Get tags information for a product."""
        async with db.get_connection() as conn:
            query = """
                SELECT *
                FROM get_product_tags_info($1) as mi;
            """
            return await conn.fetch(query, product_id)

    @staticmethod
    async def get_min_price_30_days(product_id: int):
        """Get minimum price in last 30 days for a product."""
        async with db.get_connection() as conn:
            query = """
                SELECT 
                    (get_min_price_30_days($1)) as min_price;
            """
            return await conn.fetchrow(query, product_id)