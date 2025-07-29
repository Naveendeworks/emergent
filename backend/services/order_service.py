from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.order import Order, OrderCreate, OrderUpdate, OrderStats
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.orders
    
    async def create_order(self, order_data: OrderCreate) -> Order:
        """Create a new order"""
        try:
            order = Order(
                customerName=order_data.customerName,
                items=order_data.items,
                totalItems=sum(item.quantity for item in order_data.items)
            )
            
            order_dict = order.dict()
            result = await self.collection.insert_one(order_dict)
            
            if result.inserted_id:
                order_dict['_id'] = str(result.inserted_id)
                return Order(**order_dict)
            else:
                raise Exception("Failed to create order")
                
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            raise e
    
    async def get_all_orders(self) -> List[Order]:
        """Get all orders"""
        try:
            cursor = self.collection.find({}).sort("orderTime", -1)
            orders = []
            async for order_doc in cursor:
                order_doc['_id'] = str(order_doc['_id'])
                orders.append(Order(**order_doc))
            return orders
        except Exception as e:
            logger.error(f"Error fetching orders: {str(e)}")
            raise e
    
    async def get_order_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        try:
            order_doc = await self.collection.find_one({"id": order_id})
            if order_doc:
                order_doc['_id'] = str(order_doc['_id'])
                return Order(**order_doc)
            return None
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {str(e)}")
            raise e
    
    async def update_order(self, order_id: str, order_data: OrderCreate) -> Optional[Order]:
        """Update order with new items, customer name, and payment method"""
        try:
            # Calculate new total items
            total_items = sum(item.quantity for item in order_data.items)
            
            update_data = {
                "customerName": order_data.customerName,
                "items": [item.dict() for item in order_data.items],
                "paymentMethod": order_data.paymentMethod,
                "totalItems": total_items
            }
            
            result = await self.collection.update_one(
                {"id": order_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_order_by_id(order_id)
            return None
        except Exception as e:
            logger.error(f"Error updating order {order_id}: {str(e)}")
            raise e
    
    async def complete_order(self, order_id: str) -> Optional[Order]:
        """Mark order as completed"""
        try:
            result = await self.collection.update_one(
                {"id": order_id},
                {"$set": {"status": "completed"}}
            )
            
            if result.modified_count > 0:
                return await self.get_order_by_id(order_id)
            return None
        except Exception as e:
            logger.error(f"Error completing order {order_id}: {str(e)}")
            raise e
    
    async def get_order_stats(self) -> OrderStats:
        """Get order statistics"""
        try:
            # Get today's date range
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            
            # Count orders by status for today
            pending_count = await self.collection.count_documents({
                "status": "pending",
                "orderTime": {"$gte": today, "$lt": tomorrow}
            })
            
            completed_count = await self.collection.count_documents({
                "status": "completed",
                "orderTime": {"$gte": today, "$lt": tomorrow}
            })
            
            total_count = pending_count + completed_count
            
            return OrderStats(
                pending=pending_count,
                completed=completed_count,
                total=total_count
            )
        except Exception as e:
            logger.error(f"Error getting order stats: {str(e)}")
            raise e
    
    async def delete_order(self, order_id: str) -> bool:
        """Delete/cancel an order"""
        try:
            result = await self.collection.delete_one({"id": order_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting order {order_id}: {str(e)}")
            raise e