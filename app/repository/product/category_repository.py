from typing import Optional
from db import db

class CategoryRepository:
    """Repository for category hierarchy and navigation operations."""
    
    @staticmethod
    async def get_category_hierarchy(category_id: Optional[int] = None):
        """Get category breadcrumbs and subcategories for navigation."""
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