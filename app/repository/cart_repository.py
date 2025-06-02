from typing import List, Optional
from db import db
from model.cart_model import CartProduct, CartSummary

class CartRepository:
    
    async def get_user_cart(self, user_id: str) -> CartSummary:
        """Get all cart items for a specific user"""
        query = """
            SELECT 
                cpv.id_variant_size,
                p.name as product_name,
                v.name as variant_name,
                v.color,
                s.id_size,
                s."order" as size_order,
                sd.value as size,
                cpv.quantity,
                ph.price,
                p.thumbnail_path
            FROM cart_product_variant cpv
            JOIN variant_size vs ON cpv.id_variant_size = vs.id_variant_size
            JOIN variant v ON vs.id_variant = v.id_variant
            JOIN product p ON v.id_product = p.id_product
            JOIN size s ON vs.id_size = s.id_size
            JOIN size_data sd ON s.id_size = sd.id_size
            JOIN sizing_format sf ON sd.id_sizing_format = sf.id_sizing_format
            JOIN LATERAL (
                SELECT price 
                FROM price_history ph2 
                WHERE ph2.id_product = p.id_product 
                ORDER BY ph2.created_at DESC 
                LIMIT 1
            ) ph ON true
            WHERE cpv.id_user = $1 
            AND sf.value = 'International'  -- Use consistent sizing format
            ORDER BY p.name, v.name, s."order"
        """
        
        async with db.get_connection() as conn:
            rows = await conn.fetch(query, user_id)
            
            # Convert rows to CartProduct objects with proper color conversion
            products = []
            for row in rows:
                row_dict = dict(row)
                # Convert color bytes to hex string
                if row_dict['color'] and isinstance(row_dict['color'], bytes):
                    row_dict['color'] = f"#{int.from_bytes(row_dict['color'], byteorder='big'):06X}"
                products.append(CartProduct(**row_dict))
            
            total_amount = sum(product.price * product.quantity for product in products)
            total_items = sum(product.quantity for product in products)
            
            return CartSummary(
                products=products,
                total_amount=total_amount,
                total_items=total_items
            )
    
    async def add_to_cart(self, user_id: str, variant_size_id: int, quantity: int = 1) -> bool:
        """Add item to cart or update quantity if item already exists"""
        query = """
            INSERT INTO cart_product_variant (id_user, id_variant_size, quantity)
            VALUES ($1, $2, $3)
            ON CONFLICT (id_user, id_variant_size) 
            DO UPDATE SET quantity = cart_product_variant.quantity + EXCLUDED.quantity
        """
        
        try:
            async with db.get_connection() as conn:
                result = await conn.execute(query, user_id, variant_size_id, quantity)
                return "INSERT" in result or "UPDATE" in result
        except Exception as e:
            print(f"Error adding to cart: {e}")
            return False
    
    async def update_cart_quantity(self, user_id: str, variant_size_id: int, quantity: int) -> bool:
        """Update quantity of specific item in cart"""
        query = """
            UPDATE cart_product_variant 
            SET quantity = $3
            WHERE id_user = $1 AND id_variant_size = $2
        """
        
        try:
            async with db.get_connection() as conn:
                result = await conn.execute(query, user_id, variant_size_id, quantity)
                return result == "UPDATE 1"
        except Exception as e:
            print(f"Error updating cart quantity: {e}")
            return False
    
    async def remove_from_cart(self, user_id: str, variant_size_id: int) -> bool:
        """Remove item from cart"""
        query = """
            DELETE FROM cart_product_variant 
            WHERE id_user = $1 AND id_variant_size = $2
        """
        
        try:
            async with db.get_connection() as conn:
                result = await conn.execute(query, user_id, variant_size_id)
                return result == "DELETE 1"
        except Exception as e:
            print(f"Error removing from cart: {e}")
            return False
    
    async def clear_cart(self, user_id: str) -> bool:
        """Clear all items from user's cart"""
        query = "DELETE FROM cart_product_variant WHERE id_user = $1"
        
        try:
            async with db.get_connection() as conn:
                await conn.execute(query, user_id)
                return True
        except Exception as e:
            print(f"Error clearing cart: {e}")
            return False
    
    async def get_cart_count(self, user_id: str) -> int:
        """Get total number of items in user's cart"""
        query = """
            SELECT COALESCE(SUM(quantity), 0) as total_items
            FROM cart_product_variant 
            WHERE id_user = $1
        """
        
        try:
            async with db.get_connection() as conn:
                row = await conn.fetchrow(query, user_id)
                return row['total_items'] if row else 0
        except Exception as e:
            print(f"Error getting cart count: {e}")
            return 0

# Global repository instance
cart_repo = CartRepository()
