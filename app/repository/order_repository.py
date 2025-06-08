from typing import List, Optional
from datetime import datetime
from uuid import UUID
from db import db
from model.order_model import OrderSummary, OrderProduct

class OrderRepository:
    
    async def get_user_orders(self, user_id: UUID) -> List[OrderSummary]:
        """Get all orders for a specific user"""
        query = """
            WITH order_totals AS (
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
                o.id_user,
                o.shipping_price,
                o.payed_at,
                o.cancelled_at,
                o.shippment_tracking_number::text,
                o.return_tracking_number::text,
                o.secret_code,
                osv.status as current_status,
                osv.created_at as status_updated_at,
                COALESCE(ot.total_amount, 0) as total_amount
            FROM "order" o
            LEFT JOIN order_status_view osv ON o.id_order = osv.id_order
            LEFT JOIN order_totals ot ON o.id_order = ot.id_order
            WHERE o.id_user = $1
            ORDER BY o.payed_at DESC NULLS LAST, o.id_order DESC
        """
        async with db.get_connection() as conn:
            rows = await conn.fetch(query, user_id)
            return [OrderSummary(
                id_order=row['id_order'],
                user_id=row['id_user'],
                shipping_price=row['shipping_price'],
                payed_at=row['payed_at'],
                cancelled_at=row['cancelled_at'],
                shippment_tracking_number=row['shippment_tracking_number'],
                return_tracking_number=row['return_tracking_number'],
                secret_code=row['secret_code'],
                current_status=row['current_status'],
                status_updated_at=row['status_updated_at'],
                total_amount=row['total_amount'],
                products=await self._get_order_products(row['id_order'])
            ) for row in rows]

    async def get_order(self, order_id: int) -> Optional[OrderSummary]:
        """Get a specific order by ID"""
        query = """
            SELECT 
                o.id_order,
                o.id_user,
                o.shipping_price,
                o.payed_at,
                o.cancelled_at,
                o.shippment_tracking_number::text,
                o.return_tracking_number::text,
                o.secret_code,
                osv.status as current_status,
                osv.created_at as status_updated_at,
                COALESCE(
                    (SELECT SUM(op.quantity * ph.price)
                    FROM order_product op
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
                    WHERE op.id_order = o.id_order
                    ), 0) as total_amount
            FROM "order" o
            LEFT JOIN order_status_view osv ON o.id_order = osv.id_order
            WHERE o.id_order = $1
        """
        async with db.get_connection() as conn:
            row = await conn.fetchrow(query, order_id)
            if not row:
                return None
                
            return OrderSummary(
                id_order=row['id_order'],
                user_id=row['id_user'],
                shipping_price=row['shipping_price'],
                payed_at=row['payed_at'],
                cancelled_at=row['cancelled_at'],
                shippment_tracking_number=row['shippment_tracking_number'],
                return_tracking_number=row['return_tracking_number'],
                secret_code=row['secret_code'],
                current_status=row['current_status'],
                status_updated_at=row['status_updated_at'],
                total_amount=row['total_amount'],
                products=await self._get_order_products(row['id_order'])
            )

    async def _get_order_products(self, order_id: int) -> List[OrderProduct]:
        """Get products for a specific order"""
        query = """
            SELECT 
                p.name as product_name,
                v.name as variant_name,
                encode(v.color, 'hex') as color,
                sd.value as size,
                op.quantity,
                ph.price
            FROM order_product op
            JOIN variant_size vs ON op.id_variant_size = vs.id_variant_size
            JOIN variant v ON vs.id_variant = v.id_variant
            JOIN product p ON v.id_product = p.id_product
            JOIN size s ON vs.id_size = s.id_size
            JOIN size_data sd ON s.id_size = sd.id_size
            JOIN LATERAL (
                SELECT price 
                FROM price_history ph2 
                WHERE ph2.id_product = p.id_product 
                ORDER BY ph2.created_at DESC 
                LIMIT 1
            ) ph ON true
            WHERE op.id_order = $1
        """
        async with db.get_connection() as conn:
            rows = await conn.fetch(query, order_id)
            return [OrderProduct(
                product_name=row['product_name'],
                variant_name=row['variant_name'],
                color=row['color'],
                size=row['size'],
                quantity=row['quantity'],
                price=row['price']
            ) for row in rows]

    async def update_order_status(self, order_id: int, new_status: str) -> bool:
        """Update order status"""
        query = """
            UPDATE order_status_view 
            SET status = $2::order_status 
            WHERE id_order = $1
            RETURNING id_order;
        """
        try:
            async with db.get_connection() as conn:
                result = await conn.fetchval(query, order_id, new_status)
                print(f"Updated order {order_id} status to {new_status}, result: {result}")
                return result is not None
        except Exception as e:
            print(f"Error updating order status: {str(e)}")
            return False

# Global repository instance
order_repo = OrderRepository()