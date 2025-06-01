from typing import List, Optional
from db import db
from model.order_model import OrderSummary, OrderProduct, OrderStatus

class OrderRepository:
    
    async def get_user_orders(self, user_id: str) -> List[OrderSummary]:
        """Get all orders for a specific user"""
        query = """
            WITH latest_status AS (
                SELECT DISTINCT ON (oh.id_order) 
                    oh.id_order,
                    oh.status,
                    oh.created_at as status_updated_at
                FROM order_history oh
                ORDER BY oh.id_order, oh.created_at DESC
            ),
            order_totals AS (
                SELECT 
                    op.id_order,
                    SUM(op.quantity * ph.price) as total_amount
                FROM order_product op
                JOIN "order" o ON op.id_order = o.id_order
                JOIN variant_size vs ON op.id_variant_size = vs.id_variant_size
                JOIN variant v ON vs.id_variant = v.id_variant
                JOIN product p ON v.id_product = p.id_product
                JOIN LATERAL (
                    SELECT price 
                    FROM price_history ph2 
                    WHERE ph2.id_product = p.id_product 
                    AND ph2.created_at <= COALESCE(o.payed_at, NOW())
                    ORDER BY ph2.created_at DESC 
                    LIMIT 1
                ) ph ON true
                GROUP BY op.id_order
            )
            SELECT 
                o.id_order,
                o.shipping_price,
                o.payed_at,
                o.cancelled_at,
                o.shippment_tracking_number::text,
                o.return_tracking_number::text,
                o.secret_code,
                ls.status as current_status,
                ls.status_updated_at,
                COALESCE(ot.total_amount, 0) as total_amount
            FROM "order" o
            LEFT JOIN latest_status ls ON o.id_order = ls.id_order
            LEFT JOIN order_totals ot ON o.id_order = ot.id_order
            WHERE o.id_user = $1
            ORDER BY o.payed_at DESC NULLS LAST, o.id_order DESC
        """
        
        async with db.get_connection() as conn:
            rows = await conn.fetch(query, user_id)
            orders = []
            
            for row in rows:
                # Get products for this order
                products = await self._get_order_products(row['id_order'])
                
                order_dict = dict(row)
                order_dict['products'] = products
                orders.append(OrderSummary(**order_dict))
            
            return orders
    
    async def _get_order_products(self, order_id: int) -> List[OrderProduct]:
        """Get all products for a specific order"""
        query = """
            SELECT 
                p.name as product_name,
                v.name as variant_name,
                v.color,
                sf.value as size,
                op.quantity,
                ph.price
            FROM order_product op
            JOIN "order" o ON op.id_order = o.id_order
            JOIN variant_size vs ON op.id_variant_size = vs.id_variant_size
            JOIN variant v ON vs.id_variant = v.id_variant
            JOIN product p ON v.id_product = p.id_product
            JOIN size s ON vs.id_size = s.id_size
            JOIN size_data sd ON s.id_size = sd.id_size
            JOIN sizing_format sf ON sd.id_sizing_format = sf.id_sizing_format
            JOIN LATERAL (
                SELECT price 
                FROM price_history ph2 
                WHERE ph2.id_product = p.id_product 
                AND ph2.created_at <= COALESCE(o.payed_at, NOW())
                ORDER BY ph2.created_at DESC 
                LIMIT 1
            ) ph ON true
            WHERE op.id_order = $1
            ORDER BY p.name, v.name
        """
        
        async with db.get_connection() as conn:
            rows = await conn.fetch(query, order_id)
            return [OrderProduct(**dict(row)) for row in rows]

# Global repository instance
order_repo = OrderRepository()
