from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.notification import Notification, NotificationCreate, NotificationUpdate, EASTERN_TZ
from models.order import Order, OrderItem
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.notifications
    
    def get_eastern_time(self):
        """Get current Eastern time"""
        return datetime.now(EASTERN_TZ)
    
    async def create_notification(self, notification_data: NotificationCreate) -> Notification:
        """Create a new notification"""
        try:
            current_time = self.get_eastern_time()
            notification = Notification(
                customerName=notification_data.customerName,
                message=notification_data.message,
                orderId=notification_data.orderId,
                createdAt=current_time
            )
            
            notification_dict = notification.dict()
            # Convert datetime objects to strings for MongoDB
            if notification_dict.get('createdAt'):
                notification_dict['createdAt'] = notification_dict['createdAt'].isoformat()
            
            result = await self.collection.insert_one(notification_dict)
            
            if result.inserted_id:
                notification_dict['_id'] = str(result.inserted_id)
                # Convert back to datetime objects for response
                if notification_dict.get('createdAt'):
                    notification_dict['createdAt'] = datetime.fromisoformat(notification_dict['createdAt'])
                return Notification(**notification_dict)
            else:
                raise Exception("Failed to create notification")
                
        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            raise e
    
    async def get_active_notifications(self) -> List[Notification]:
        """Get all active notifications for display"""
        try:
            cursor = self.collection.find({"isActive": True}).sort("createdAt", -1)
            notifications = []
            async for notification_doc in cursor:
                notification_doc['_id'] = str(notification_doc['_id'])
                # Convert ISO string back to datetime if needed
                if isinstance(notification_doc.get('createdAt'), str):
                    notification_doc['createdAt'] = datetime.fromisoformat(notification_doc['createdAt'])
                
                notifications.append(Notification(**notification_doc))
            return notifications
        except Exception as e:
            logger.error(f"Error fetching active notifications: {str(e)}")
            raise e
    
    async def get_all_notifications(self, limit: int = 100) -> List[Notification]:
        """Get all notifications with limit"""
        try:
            cursor = self.collection.find({}).sort("createdAt", -1).limit(limit)
            notifications = []
            async for notification_doc in cursor:
                notification_doc['_id'] = str(notification_doc['_id'])
                # Convert ISO string back to datetime if needed
                if isinstance(notification_doc.get('createdAt'), str):
                    notification_doc['createdAt'] = datetime.fromisoformat(notification_doc['createdAt'])
                
                notifications.append(Notification(**notification_doc))
            return notifications
        except Exception as e:
            logger.error(f"Error fetching notifications: {str(e)}")
            raise e
    
    async def update_notification(self, notification_id: str, update_data: NotificationUpdate) -> Optional[Notification]:
        """Update notification status"""
        try:
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            
            result = await self.collection.update_one(
                {"id": notification_id},
                {"$set": update_dict}
            )
            
            if result.modified_count > 0:
                return await self.get_notification_by_id(notification_id)
            return None
        except Exception as e:
            logger.error(f"Error updating notification {notification_id}: {str(e)}")
            raise e
    
    async def get_notification_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID"""
        try:
            notification_doc = await self.collection.find_one({"id": notification_id})
            if notification_doc:
                notification_doc['_id'] = str(notification_doc['_id'])
                if isinstance(notification_doc.get('createdAt'), str):
                    notification_doc['createdAt'] = datetime.fromisoformat(notification_doc['createdAt'])
                
                return Notification(**notification_doc)
            return None
        except Exception as e:
            logger.error(f"Error fetching notification {notification_id}: {str(e)}")
            raise e
    
    async def delete_notification(self, notification_id: str) -> bool:
        """Delete notification"""
        try:
            result = await self.collection.delete_one({"id": notification_id})
            return result.deleted_count > 0
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
            
            result = await self.collection.delete_many({
                "createdAt": {"$lt": cutoff_time.isoformat()}
            })
            
            logger.info(f"Cleared {result.deleted_count} old notifications")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error clearing old notifications: {str(e)}")
            raise e