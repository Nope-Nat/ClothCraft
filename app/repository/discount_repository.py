from typing import List, Optional, Dict, Any
from db import db

class DiscountRepository:
    """Repository for discount-related database operations"""
    
    async def get_discounts_with_filters(self, coupon_code: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get discounts with optional filtering"""
        conditions = []
        params = []
        param_counter = 1
        
        # Build WHERE conditions for the main query (not the CTE)
        where_conditions = []
        
        if coupon_code and coupon_code.strip():
            where_conditions.append(f"dg.secret_code ILIKE ${param_counter}")
            params.append(f"%{coupon_code.strip()}%")
            param_counter += 1
        
        if status == "active":
            where_conditions.append("dg.status = 'active'")
        elif status == "expired":
            where_conditions.append("dg.status = 'expired'")
        elif status == "future":
            where_conditions.append("dg.status = 'future'")
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        query = f"""
            WITH discount_groups AS (
                SELECT 
                    MIN(dh.id_discount) as id_discount,
                    dh.discount,
                    dh."from",
                    dh."to",
                    dh.secret_code,
                    CASE 
                        WHEN dh."from" <= NOW() AND (dh."to" IS NULL OR dh."to" >= NOW()) THEN 'active'
                        WHEN dh."to" IS NOT NULL AND dh."to" < NOW() THEN 'expired'
                        WHEN dh."from" > NOW() THEN 'future'
                    END as status,
                    COUNT(*) as products_count
                FROM discount_history dh
                GROUP BY dh.discount, dh."from", dh."to", dh.secret_code
            )
            SELECT 
                dg.id_discount,
                dg.discount,
                dg."from",
                dg."to",
                dg.secret_code,
                dg.status,
                dg.products_count,
                CASE 
                    WHEN dg.secret_code IS NOT NULL THEN CONCAT('Coupon: ', dg.secret_code)
                    ELSE 'General Discount'
                END as discount_name
            FROM discount_groups dg
            {where_clause}
            ORDER BY 
                CASE WHEN dg."to" IS NULL THEN 0 ELSE 1 END,
                dg."to" ASC NULLS FIRST,
                dg."from" DESC
        """
        
        async with db.get_connection() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]

    async def get_discount_details(self, discount_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific discount"""
        query = """
            SELECT 
                dh.id_discount,
                dh.id_product,
                p.name as product_name,
                dh.discount,
                dh."from",
                dh."to",
                dh.secret_code,
                CASE 
                    WHEN dh."from" <= NOW() AND (dh."to" IS NULL OR dh."to" >= NOW()) THEN 'active'
                    WHEN dh."to" IS NOT NULL AND dh."to" < NOW() THEN 'expired'
                    WHEN dh."from" > NOW() THEN 'future'
                END as status
            FROM discount_history dh
            JOIN product p ON dh.id_product = p.id_product
            WHERE dh.id_discount = $1
        """
        
        async with db.get_connection() as conn:
            row = await conn.fetchrow(query, discount_id)
            return dict(row) if row else None

    async def get_discount_affected_products(self, discount_id: int) -> List[Dict[str, Any]]:
        """Get products affected by a specific discount"""
        query = """
            SELECT 
                p.id_product,
                p.name,
                p.thumbnail_path,
                ppv.price as current_price,
                dh.discount
            FROM discount_history dh
            JOIN product p ON dh.id_product = p.id_product
            LEFT JOIN product_price_view ppv ON p.id_product = ppv.id_product
            WHERE (
                -- If the discount has a secret code, match by secret code
                (dh.secret_code IS NOT NULL AND dh.secret_code = (
                    SELECT secret_code 
                    FROM discount_history 
                    WHERE id_discount = $1
                ))
                OR
                -- If the discount has no secret code, match by discount percentage, from, and to dates
                (dh.secret_code IS NULL AND (
                    SELECT secret_code FROM discount_history WHERE id_discount = $1
                ) IS NULL AND
                dh.discount = (SELECT discount FROM discount_history WHERE id_discount = $1) AND
                dh."from" = (SELECT "from" FROM discount_history WHERE id_discount = $1) AND
                dh."to" IS NOT DISTINCT FROM (SELECT "to" FROM discount_history WHERE id_discount = $1))
            )
            ORDER BY p.name
        """
        
        async with db.get_connection() as conn:
            rows = await conn.fetch(query, discount_id)
            return [dict(row) for row in rows]

# Global repository instance
discount_repo = DiscountRepository()
