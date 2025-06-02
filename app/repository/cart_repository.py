from typing import List, Optional
from db import db
from model.cart_model import CartProduct, CartSummary

class CartRepository:
    
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
    
    async def get_user_cart_with_availability(self, user_id: str, secret_code: str = None) -> CartSummary:
        """Get all cart items for a specific user with pricing, discount info, and availability checking"""
        query = """
            SELECT 
                cpv.id_variant_size,
                p.id_product,
                p.name as product_name,
                v.name as variant_name,
                v.color,
                s.id_size,
                s."order" as size_order,
                sd.value as size,
                cpv.quantity,
                get_product_regular_price(p.id_product) as regular_price,
                get_product_discounted_price(p.id_product, $2) as discounted_price,
                p.thumbnail_path,
                di.discount_percent,
                di.discount_code,
                di.discount_from,
                di.discount_to,
                COALESCE(
                    (SELECT SUM(sdp.quantity) 
                     FROM storage_delivery_part sdp 
                     WHERE sdp.id_variant_size = cpv.id_variant_size), 0
                ) - COALESCE(
                    (SELECT SUM(op.quantity) 
                     FROM order_product op 
                     WHERE op.id_variant_size = cpv.id_variant_size), 0
                ) as available_quantity
            FROM cart_product_variant cpv
            JOIN variant_size vs ON cpv.id_variant_size = vs.id_variant_size
            JOIN variant v ON vs.id_variant = v.id_variant
            JOIN product p ON v.id_product = p.id_product
            JOIN size s ON vs.id_size = s.id_size
            JOIN size_data sd ON s.id_size = sd.id_size
            JOIN sizing_format sf ON sd.id_sizing_format = sf.id_sizing_format
            LEFT JOIN LATERAL get_product_discount_info(p.id_product, $2) di ON true
            WHERE cpv.id_user = $1 
            AND sf.value = 'International'
            ORDER BY p.name, v.name, s."order"
        """
        
        async with db.get_connection() as conn:
            rows = await conn.fetch(query, user_id, secret_code)
            
            # Convert rows to CartProduct objects with proper color conversion
            products = []
            cart_has_unavailable_items = False
            
            for row in rows:
                row_dict = dict(row)
                # Convert color bytes to hex string
                if row_dict['color'] and isinstance(row_dict['color'], bytes):
                    row_dict['color'] = f"#{int.from_bytes(row_dict['color'], byteorder='big'):06X}"
                
                # Use discounted_price as the main price field for compatibility
                row_dict['price'] = row_dict['discounted_price']
                
                # Check if item is available in sufficient quantity
                row_dict['is_available'] = row_dict['available_quantity'] >= row_dict['quantity']
                row_dict['shortage'] = max(0, row_dict['quantity'] - row_dict['available_quantity'])
                
                if not row_dict['is_available']:
                    cart_has_unavailable_items = True
                
                products.append(CartProduct(**row_dict))
            
            total_amount = sum(product.discounted_price * product.quantity for product in products if product.is_available)
            total_regular_amount = sum(product.regular_price * product.quantity for product in products if product.is_available)
            total_savings = total_regular_amount - total_amount
            total_items = sum(product.quantity for product in products if product.is_available)
            
            return CartSummary(
                products=products,
                total_amount=total_amount,
                total_regular_amount=total_regular_amount,
                total_savings=total_savings,
                total_items=total_items,
                coupon_code=secret_code,
                can_checkout=not cart_has_unavailable_items
            )

# Global repository instance
cart_repo = CartRepository()
