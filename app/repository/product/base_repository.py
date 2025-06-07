from db import db

class BaseRepository:
    """Repository for basic product-related data fetching operations."""
    
    @staticmethod
    async def get_all_categories():
        """Get all categories ordered by name."""
        async with db.get_connection() as conn:
            return await conn.fetch("""
                SELECT *
                FROM category 
                ORDER BY name
            """)
    
    @staticmethod
    async def get_all_sizing_types():
        """Get all sizing types ordered by name."""
        async with db.get_connection() as conn:
            return await conn.fetch("""
                SELECT *
                FROM sizing_type 
                ORDER BY name
            """)

    @staticmethod
    async def get_all_countries():
        """Get all countries ordered by name."""
        async with db.get_connection() as conn:
            return await conn.fetch("""
                SELECT *
                FROM country 
                ORDER BY name
            """)
    
    @staticmethod
    async def get_all_tags():
        """Get all tags ordered by name."""
        async with db.get_connection() as conn:
            return await conn.fetch("""
                SELECT *
                FROM tag
                ORDER BY name
            """)

    @staticmethod
    async def get_all_sizes():
        """Get all available sizes with their format names."""
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