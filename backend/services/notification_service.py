from typing import List, Optional
from asyncpg import Pool
from models.notification import Notification, NotificationCreate, NotificationUpdate, EASTERN_TZ
from models.order import Order, OrderItem
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, pool: Pool):
        self.pool = pool
    
    def get_eastern_time(self):
        """Get current Eastern time"""
        return datetime.now(EASTERN_TZ)
    
    async def create_notification(self, notification_data: NotificationCreate) -> Notification:
        """Create a new notification"""
        try:
            current_time = self.get_eastern_time()
            
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    INSERT INTO notifications (
                        customer_name, 
                        message, 
                        order_id, 
                        created_at,
                        status
                    ) VALUES ($1, $2, $3, $4, $5)
                    RETURNING *
                """,
                notification_data.customerName,
                notification_data.message,
                notification_data.orderId,
                current_time,
                'active'
                )
                
                if row:
                    return Notification(**dict(row))
                else:
                    raise Exception("Failed to create notification")
                
        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            raise e
    
    async def get_active_notifications(self) -> List[Notification]:
        """Get all active notifications for display"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM notifications 
                    WHERE status = 'active' 
                    ORDER BY created_at DESC
                """)
                return [Notification(**dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching active notifications: {str(e)}")
            raise e
    
    async def get_all_notifications(self, limit: int = 100) -> List[Notification]:
        """Get all notifications with limit"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM notifications 
                    ORDER BY created_at DESC 
                    LIMIT $1
                """, limit)
                return [Notification(**dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching notifications: {str(e)}")
            raise e
    
    async def update_notification(self, notification_id: str, update_data: NotificationUpdate) -> Optional[Notification]:
        """Update notification status"""
        try:
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            
            # Build SET clause and parameters
            set_items = []
            params = [notification_id]  # First parameter is notification_id
            param_index = 2  # Start from $2 since $1 is notification_id
            
            for key, value in update_dict.items():
                set_items.append(f"{key} = ${param_index}")
                params.append(value)
                param_index += 1
            
            set_clause = ", ".join(set_items)
            
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    f"UPDATE notifications SET {set_clause} WHERE id = $1 RETURNING *",
                    *params
                )
                if row:
                    return Notification(**dict(row))
                return None
        except Exception as e:
            logger.error(f"Error updating notification {notification_id}: {str(e)}")
            raise e
    
    async def get_notification_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM notifications WHERE id = $1",
                    notification_id
                )
                if row:
                    return Notification(**dict(row))
                return None
        except Exception as e:
            logger.error(f"Error fetching notification {notification_id}: {str(e)}")
            raise e
    
    async def delete_notification(self, notification_id: str) -> bool:
        """Delete notification"""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute(
                    "DELETE FROM notifications WHERE id = $1",
                    notification_id
                )
                return result == "DELETE 1"
        except Exception as e:
            logger.error(f"Error deleting notification {notification_id}: {str(e)}")
            raise e
    
    async def create_order_ready_notification(self, order: Order) -> Notification:
        """Create a notification when order is ready"""
        try:
            # Format items list
            items_text = ", ".join([f"{item.name} (x{item.quantity})" for item in order.items])
            
            message = f"🍽️ Your order is ready for pickup! Items: {items_text}. Please come to the counter. Thank you!"
            
            notification_data = NotificationCreate(
                customerName=order.customerName,
                message=message,
                orderId=order.id
            )
            
            return await self.create_notification(notification_data)
        except Exception as e:
            logger.error(f"Error creating order ready notification: {str(e)}")
            raise e
    
    async def clear_old_notifications(self, hours_old: int = 24):
        """Clear notifications older than specified hours"""
        try:
            cutoff_time = self.get_eastern_time() - timedelta(hours=hours_old)
            
            async with self.pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM notifications 
                    WHERE created_at < $1
                """, cutoff_time)
                
                deleted_count = int(result.split()[1]) if result else 0
                logger.info(f"Cleared {deleted_count} old notifications")
                return deleted_count
        except Exception as e:
            logger.error(f"Error clearing old notifications: {str(e)}")
            raise e