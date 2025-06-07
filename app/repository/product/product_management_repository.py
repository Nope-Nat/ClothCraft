from typing import List, Optional
from db import db

class ProductManagementRepository:
    """Repository for product creation, updates, and management operations."""
    
    @staticmethod
    async def create_product(
        id_category: int,
        id_sizing_type: int,
        id_country: int,
        sku_code: str,
        short_description: str,
        thumbnail_path: str,
        product_name: str,
        initial_price: float,
        initial_description: str,
        tag_ids: Optional[List[int]] = None
    ):
        """Create a new product with initial price, description, image, and tags."""
        async with db.get_connection() as conn:
            async with conn.transaction():
                # Insert the main product
                product_query = """
                    INSERT INTO product(id_category, id_sizing_type, id_country, sku_code, active, short_description, thumbnail_path, name) 
                    VALUES ($1, $2, $3, $4, true, $5, $6, $7)
                    RETURNING id_product
                """
                product_result = await conn.fetchrow(
                    product_query, 
                    id_category, id_sizing_type, id_country, sku_code, 
                    short_description, thumbnail_path, product_name
                )
                new_product_id = product_result['id_product']
                
                # Insert price history
                await conn.execute(
                    "INSERT INTO price_history(id_product, price) VALUES ($1, $2)",
                    new_product_id, initial_price
                )
                
                # Insert product description
                await conn.execute(
                    "INSERT INTO product_details_history(id_product, description) VALUES ($1, $2)",
                    new_product_id, initial_description
                )
                
                # Insert product image
                await conn.execute(
                    "INSERT INTO product_image(id_product, img_path, \"order\") VALUES ($1, $2, 1)",
                    new_product_id, thumbnail_path
                )
                
                # Insert product tags if any are selected
                if tag_ids:
                    tag_query = """
                        INSERT INTO tag_product(id_product, id_tag) VALUES ($1, $2)
                    """
                    for tag_id in tag_ids:
                        await conn.execute(tag_query, new_product_id, tag_id)
                
                return new_product_id