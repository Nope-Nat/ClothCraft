from db import db

class VariantRepository:
    """Repository for product variant and sizing operations."""
    
    @staticmethod
    async def get_product_variants(product_id: int):
        """Get all active variants for a product."""
        async with db.get_connection() as conn:
            query = """
                SELECT id_variant, name, color
                FROM variant
                WHERE id_product = $1 AND active = true;
            """
            return await conn.fetch(query, product_id)

    @staticmethod
    async def get_product_sizing_formats(product_id: int):
        """Get all available sizing formats for a product."""
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

    @staticmethod
    async def get_product_variant_sizes(id_variant: int, format_id: int = None):
        """Get sizes for variant in specific format with stock quantities."""
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
                    sd.value as size_value,
                    COALESCE(
                        (SELECT SUM(sdp.quantity) 
                         FROM storage_delivery_part sdp 
                         WHERE sdp.id_variant_size = vs.id_variant_size), 0
                    ) - COALESCE(
                        (SELECT SUM(op.quantity) 
                         FROM order_product op 
                         WHERE op.id_variant_size = vs.id_variant_size), 0
                    ) as available_quantity
                FROM variant_size vs
                JOIN size s ON vs.id_size = s.id_size
                JOIN size_data sd ON s.id_size = sd.id_size
                WHERE vs.id_variant = $1 AND sd.id_sizing_format = $2
                ORDER BY s."order"
            """
            return await conn.fetch(query, id_variant, format_id)