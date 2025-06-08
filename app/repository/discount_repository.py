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

    async def get_all_categories(self) -> List[Dict[str, Any]]:
        """Get all categories for discount form"""
        query = """
            SELECT id_category, name, parent_category
            FROM category
            ORDER BY name
        """
        
        async with db.get_connection() as conn:
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]

    async def get_all_tags(self) -> List[Dict[str, Any]]:
        """Get all tags for discount form"""
        query = """
            SELECT id_tag, name
            FROM tag
            ORDER BY name
        """
        
        async with db.get_connection() as conn:
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]

    async def get_all_products_minimal(self) -> List[Dict[str, Any]]:
        """Get all products with minimal info for discount form"""
        query = """
            SELECT 
                p.id_product,
                p.name,
                p.active,
                c.name as category_name,
                ppv.price as current_price
            FROM product p
            LEFT JOIN category c ON p.id_category = c.id_category
            LEFT JOIN product_price_view ppv ON p.id_product = ppv.id_product
            ORDER BY p.name
        """
        
        async with db.get_connection() as conn:
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]

    async def get_affected_products_preview(self, category_ids: List[int] = None, tag_ids: List[int] = None, product_ids: List[int] = None) -> List[Dict[str, Any]]:
        """Get products that would be affected by discount based on selections"""
        # If nothing is selected, return empty list
        if not category_ids and not tag_ids and not product_ids:
            return []
        
        base_conditions = ["p.active = true"]
        params = []
        param_counter = 1
        
        selection_conditions = []
        
        # Category selection
        if category_ids:
            placeholders = ",".join([f"${i}" for i in range(param_counter, param_counter + len(category_ids))])
            selection_conditions.append(f"p.id_category IN ({placeholders})")
            params.extend(category_ids)
            param_counter += len(category_ids)
        
        # Tag selection
        if tag_ids:
            placeholders = ",".join([f"${i}" for i in range(param_counter, param_counter + len(tag_ids))])
            selection_conditions.append(f"p.id_product IN (SELECT tp.id_product FROM tag_product tp WHERE tp.id_tag IN ({placeholders}))")
            params.extend(tag_ids)
            param_counter += len(tag_ids)
        
        # Product selection
        if product_ids:
            placeholders = ",".join([f"${i}" for i in range(param_counter, param_counter + len(product_ids))])
            selection_conditions.append(f"p.id_product IN ({placeholders})")
            params.extend(product_ids)
            param_counter += len(product_ids)
        
        # Combine all conditions
        all_conditions = base_conditions.copy()
        if selection_conditions:
            # Use OR between different selection types
            all_conditions.append(f"({' OR '.join(selection_conditions)})")
        
        where_clause = "WHERE " + " AND ".join(all_conditions) if all_conditions else ""
        
        query = f"""
            SELECT 
                p.id_product,
                p.name,
                p.thumbnail_path,
                c.name as category_name,
                ppv.price as current_price,
                array_agg(DISTINCT t.name) FILTER (WHERE t.name IS NOT NULL) as tags
            FROM product p
            LEFT JOIN category c ON p.id_category = c.id_category
            LEFT JOIN product_price_view ppv ON p.id_product = ppv.id_product
            LEFT JOIN tag_product tp ON p.id_product = tp.id_product
            LEFT JOIN tag t ON tp.id_tag = t.id_tag
            {where_clause}
            GROUP BY p.id_product, p.name, p.thumbnail_path, c.name, ppv.price
            ORDER BY p.name
            LIMIT 50
        """
        
        async with db.get_connection() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]

    async def create_discount(self, percentage: float, coupon_code: str = None, from_date: str = None, to_date: str = None, category_ids: List[int] = None, tag_ids: List[int] = None, product_ids: List[int] = None) -> bool:
        """Create a new discount and apply it to selected products"""
        try:
            from datetime import datetime
            
            # Get all affected products based on selections
            affected_products = await self.get_affected_products_preview(
                category_ids=category_ids or [],
                tag_ids=tag_ids or [],
                product_ids=product_ids or []
            )
            
            if not affected_products:
                print("No affected products found")
                return False
            
            print(f"Creating discount for {len(affected_products)} products")
            
            # Convert date strings to datetime objects
            from_datetime = None
            to_datetime = None
            
            if from_date:
                try:
                    from_datetime = datetime.fromisoformat(from_date)
                except ValueError:
                    print(f"Invalid from_date format: {from_date}")
                    return False
            
            if to_date and to_date.strip():
                try:
                    to_datetime = datetime.fromisoformat(to_date)
                except ValueError:
                    print(f"Invalid to_date format: {to_date}")
                    return False
            
            async with db.get_connection() as conn:
                # Start transaction
                async with conn.transaction():
                    # Clean up coupon code
                    clean_coupon_code = coupon_code.upper() if coupon_code and coupon_code.strip() else None
                    
                    # Insert discount history records for each affected product
                    for product in affected_products:
                        insert_query = """
                            INSERT INTO discount_history (id_product, discount, "from", "to", secret_code)
                            VALUES ($1, $2, $3, $4, $5)
                        """
                        await conn.execute(
                            insert_query,
                            product['id_product'],
                            percentage,
                            from_datetime,
                            to_datetime,
                            clean_coupon_code
                        )
                        print(f"Added discount for product {product['id_product']}: {product['name']}")
                    
                    print(f"Successfully created discount: {percentage}% for {len(affected_products)} products")
                    return True
                    
        except Exception as e:
            print(f"Error creating discount: {e}")
            import traceback
            traceback.print_exc()
            return False

# Global repository instance
discount_repo = DiscountRepository()
