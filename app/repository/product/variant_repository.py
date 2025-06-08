from db import db

class VariantRepository:
    """Repository for product variant and sizing operations."""
    
    @staticmethod
    async def get_product_variants(product_id: int, include_inactive: bool = False):
        """Get all variants for a specific product."""
        async with db.get_connection() as conn:
            conditions = ["id_product = $1"]
            if not include_inactive:
                conditions.append("active = true")
            
            where_clause = " AND ".join(conditions)
            
            query = f"""
                SELECT 
                    id_variant, 
                    id_product, 
                    name, 
                    color, 
                    active,
                    created_at
                FROM variant 
                WHERE {where_clause}
                ORDER BY created_at
            """
            rows = await conn.fetch(query, product_id)
            return [dict(row) for row in rows]

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

    @staticmethod
    async def get_variant_existing_sizes(id_variant: int):
        """Get sizes already assigned to a variant."""
        async with db.get_connection() as conn:
            query = """
                SELECT vs.id_size
                FROM variant_size vs
                WHERE vs.id_variant = $1
            """
            result = await conn.fetch(query, id_variant)
            return [row['id_size'] for row in result]

    @staticmethod
    async def get_compatible_sizes_for_product(product_id: int):
        """Get all sizes compatible with product's sizing type."""
        async with db.get_connection() as conn:
            query = """
                SELECT s.id_size, sd.value as size_name, sf.value as format_name
                FROM size s
                JOIN size_data sd ON s.id_size = sd.id_size
                JOIN sizing_format sf ON sd.id_sizing_format = sf.id_sizing_format
                WHERE s.id_sizing_type = (
                    SELECT id_sizing_type FROM product WHERE id_product = $1
                )
                ORDER BY s."order", sf.value
            """
            return await conn.fetch(query, product_id)

    @staticmethod
    async def add_size_to_variant(id_variant: int, id_size: int):
        """Add a size to a variant if not already exists."""
        async with db.get_connection() as conn:
            query = """
                INSERT INTO variant_size (id_variant, id_size)
                VALUES ($1, $2)
                ON CONFLICT DO NOTHING
            """
            await conn.execute(query, id_variant, id_size)

    @staticmethod
    async def add_variant(product_id: int, name: str, color: str):
        """Add a new variant to a product."""
        async with db.get_connection() as conn:
            # Convert hex color to bytes
            color_bytes = bytes.fromhex(color.lstrip('#'))
            query = """
                INSERT INTO variant (id_product, name, color, active)
                VALUES ($1, $2, $3, true)
            """
            await conn.execute(query, product_id, name, color_bytes)

    @staticmethod
    async def get_product_materials(product_id: int):
        """Get current materials for a product with material type names."""
        async with db.get_connection() as conn:
            query = """
                SELECT pm.id_material, pm.percentage, mt.name as material_name
                FROM product_material pm
                JOIN material m ON pm.id_material = m.id_material
                JOIN material_type mt ON m.id_material_type = mt.id_material_type
                WHERE pm.id_product = $1
                ORDER BY pm.percentage DESC
            """
            return await conn.fetch(query, product_id)

    @staticmethod
    async def get_all_materials():
        """Get all available materials with their type names."""
        async with db.get_connection() as conn:
            query = """
                SELECT m.id_material, mt.name as material_name
                FROM material m
                JOIN material_type mt ON m.id_material_type = mt.id_material_type
                ORDER BY mt.name
            """
            return await conn.fetch(query)

    @staticmethod
    async def update_product_materials(product_id: int, materials_data: list):
        """Update product materials. materials_data is list of (id_material, percentage)."""
        async with db.get_connection() as conn:
            async with conn.transaction():
                # Delete existing materials
                await conn.execute("DELETE FROM product_material WHERE id_product = $1", product_id)
                
                # Insert new materials
                for id_material, percentage in materials_data:
                    if percentage > 0:  # Only insert materials with positive percentage
                        await conn.execute(
                            "INSERT INTO product_material (id_product, id_material, percentage) VALUES ($1, $2, $3)",
                            product_id, id_material, percentage
                        )