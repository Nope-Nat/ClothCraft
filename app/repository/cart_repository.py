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
                sf.value as size,
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
            ORDER BY p.name, v.name
        """
        
        async with db.get_connection() as conn:
            rows = await conn.fetch(query, user_id)
            products = [CartProduct(**dict(row)) for row in rows]
            
            total_amount = sum(product.price * product.quantity for product in products)
            total_items = sum(product.quantity for product in products)
            
            return CartSummary(
                products=products,
                total_amount=total_amount,
                total_items=total_items
            )

# Global repository instance
cart_repo = CartRepository()
