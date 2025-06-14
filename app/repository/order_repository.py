from typing import List, Optional
from datetime import datetime
from uuid import UUID
from db import db
from model.order_model import OrderSummary, OrderProduct

class OrderRepository:
    
    async def get_user_orders(self, user_id: UUID) -> List[OrderSummary]:
        """Get all orders for a specific user"""
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
                COALESCE(ot.subtotal_discounted, 0) as total_amount
            FROM "order" o
            LEFT JOIN order_status_view osv ON o.id_order = osv.id_order
            LEFT JOIN LATERAL get_order_total_at_timestamp(o.id_order, COALESCE(o.payed_at, NOW())) ot ON true
            WHERE o.id_user = $1
            ORDER BY o.payed_at DESC NULLS LAST, o.id_order DESC
        """
        async with db.get_connection() as conn:
            rows = await conn.fetch(query, user_id)
            orders = []
            
            for row in rows:
                order_calculation = await self._get_order_calculation(row['id_order'])
                order_summary = OrderSummary(
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
                order_summary.order_calculation = order_calculation
                orders.append(order_summary)
            
            return orders

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
                COALESCE(ot.subtotal_discounted, 0) as total_amount
            FROM "order" o
            LEFT JOIN order_status_view osv ON o.id_order = osv.id_order
            LEFT JOIN LATERAL get_order_total_at_timestamp(o.id_order, COALESCE(o.payed_at, NOW())) ot ON true
            WHERE o.id_order = $1
        """
        async with db.get_connection() as conn:
            row = await conn.fetchrow(query, order_id)
            if not row:
                return None
            
            order_calculation = await self._get_order_calculation(row['id_order'])
            order_summary = OrderSummary(
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
            order_summary.order_calculation = order_calculation
            return order_summary

    async def _get_order_calculation(self, order_id: int):
        """Get order calculation details for discount display"""
        query = """
            SELECT * FROM get_order_total_at_timestamp($1, (
                SELECT COALESCE(payed_at, NOW()) 
                FROM "order" 
                WHERE id_order = $1
            ))
        """
        async with db.get_connection() as conn:
            row = await conn.fetchrow(query, order_id)
            return row if row else None

    async def _get_order_products(self, order_id: int) -> List[OrderProduct]:
        """Get products for a specific order with proper discount calculations"""
        query = """
            SELECT * FROM calculate_order_price_at_timestamp($1, (
                SELECT COALESCE(payed_at, NOW()) 
                FROM "order" 
                WHERE id_order = $1
            ))
        """
        async with db.get_connection() as conn:
            rows = await conn.fetch(query, order_id)
            return [OrderProduct(
                product_name=row['product_name'],
                variant_name=row['variant_name'],
                color=row['color'],
                size=row['size_value'],
                quantity=row['quantity'],
                price=row['discounted_price'],
                regular_price=row['regular_price'],
                discounted_price=row['discounted_price']
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

    async def get_all_orders(self, status_filter: Optional[str] = None) -> List[dict]:
        """Get all orders for admin with optional status filtering"""
        query = """
            SELECT 
                o.id_order,
                o.id_user,
                u.username,
                o.shipping_price,
                o.payed_at,
                o.cancelled_at,
                o.shippment_tracking_number::text,
                o.return_tracking_number::text,
                o.secret_code,
                osv.status as current_status,
                osv.created_at as status_updated_at,
                COALESCE(ot.subtotal_discounted, 0) as total_amount
            FROM "order" o
            LEFT JOIN "user" u ON o.id_user = u.id_user
            LEFT JOIN order_status_view osv ON o.id_order = osv.id_order
            LEFT JOIN LATERAL get_order_total_at_timestamp(o.id_order, COALESCE(o.payed_at, NOW())) ot ON true
        """
        
        params = []
        if status_filter and status_filter.strip():
            query += " WHERE osv.status = $1"
            params.append(status_filter)
        
        query += " ORDER BY o.payed_at DESC NULLS LAST, o.id_order DESC"
        
        async with db.get_connection() as conn:
            rows = await conn.fetch(query, *params)
            orders = []
            
            for row in rows:
                # Get order calculation details
                order_calculation = await self._get_order_calculation(row['id_order'])
                
                # Get order products for each order
                products_query = """
                    SELECT * FROM calculate_order_price_at_timestamp($1, (
                        SELECT COALESCE(payed_at, NOW()) 
                        FROM "order" 
                        WHERE id_order = $1
                    ))
                """
                products_rows = await conn.fetch(products_query, row['id_order'])
                
                order_dict = dict(row)
                order_dict['products'] = [dict(p) for p in products_rows]
                order_dict['order_calculation'] = order_calculation
                orders.append(order_dict)
            
            return orders

    async def get_available_statuses(self) -> List[str]:
        """Get all available order statuses"""
        query = """
            SELECT DISTINCT status 
            FROM order_status_view 
            ORDER BY status
        """
        
        async with db.get_connection() as conn:
            rows = await conn.fetch(query)
            return [row['status'] for row in rows]

    async def update_order_status_admin(self, order_id: int, new_status: str) -> bool:
        """Update order status (admin function)"""
        query = """
            INSERT INTO order_history (id_order, status, created_at)
            VALUES ($1, $2::order_status, NOW())
        """
        try:
            async with db.get_connection() as conn:
                await conn.execute(query, order_id, new_status)
                return True
        except Exception as e:
            print(f"Error updating order status: {str(e)}")
            return False

# Global repository instance
order_repo = OrderRepository()