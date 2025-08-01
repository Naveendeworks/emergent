from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.order import Order, OrderCreate, OrderItem, OrderStats, PaymentReport, ItemReport, EASTERN_TZ
from services.notification_service import NotificationService
from services.menu_service import MenuService
from datetime import datetime, timedelta
import logging
import pytz
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.orders
        self.counters_collection = db.counters  # For sequential order numbers
        self.notification_service = NotificationService(db)
        self.menu_service = MenuService()
    
    def get_eastern_time(self):
        """Get current Eastern time"""
        return datetime.now(EASTERN_TZ)
    
    async def get_next_order_number(self) -> str:
        """Get the next sequential order number"""
        try:
            # Use findOneAndUpdate to atomically increment the counter
            result = await self.counters_collection.find_one_and_update(
                {"_id": "order_number"},
                {"$inc": {"sequence_value": 1}},
                upsert=True,
                return_document=True
            )
            return str(result["sequence_value"])
        except Exception as e:
            logger.error(f"Error getting next order number: {str(e)}")
            # Fallback to counting existing orders + 1
            count = await self.collection.count_documents({})
            return str(count + 1)
    
    async def create_order(self, order_data: OrderCreate) -> Order:
        """Create a new order with Eastern time and calculated prices"""
        try:
            current_time = self.get_eastern_time()
            
            # Get next sequential order number
            order_number = await self.get_next_order_number()
            
            # Calculate prices for each item
            order_items_with_prices = []
            total_amount = 0.0
            
            for item_create in order_data.items:
                # Find menu item to get price
                menu_item = await self.menu_service.get_menu_item(item_create.name.lower().replace(' ', '_'))
                if not menu_item:
                    # Try to find by name match
                    menu_items = await self.menu_service.get_menu()
                    menu_item = None
                    for mi in menu_items.items:
                        if mi.name.lower() == item_create.name.lower():
                            menu_item = mi
                            break
                
                if not menu_item:
                    raise ValueError(f"Menu item '{item_create.name}' not found")
                
                subtotal = menu_item.price * item_create.quantity
                order_item = OrderItem(
                    name=item_create.name,
                    quantity=item_create.quantity,
                    price=menu_item.price,
                    subtotal=subtotal,
                    cooking_status="not started"
                )
                order_items_with_prices.append(order_item)
                total_amount += subtotal
            
            order = Order(
                customerName=order_data.customerName,
                orderNumber=order_number,
                items=order_items_with_prices,
                paymentMethod=order_data.paymentMethod,
                orderTime=current_time,
                totalItems=sum(item.quantity for item in order_items_with_prices),
                totalAmount=round(total_amount, 2)
            )
            
            order_dict = order.dict()
            # Convert datetime objects to strings for MongoDB
            if order_dict.get('orderTime'):
                order_dict['orderTime'] = order_dict['orderTime'].isoformat()
            if order_dict.get('estimatedDeliveryTime'):
                order_dict['estimatedDeliveryTime'] = order_dict['estimatedDeliveryTime'].isoformat()
            
            result = await self.collection.insert_one(order_dict)
            
            if result.inserted_id:
                order_dict['_id'] = str(result.inserted_id)
                # Convert back to datetime objects for response
                if order_dict.get('orderTime'):
                    order_dict['orderTime'] = datetime.fromisoformat(order_dict['orderTime'])
                if order_dict.get('estimatedDeliveryTime'):
                    order_dict['estimatedDeliveryTime'] = datetime.fromisoformat(order_dict['estimatedDeliveryTime'])
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
                
                # Handle legacy orders without orderNumber field or with non-numeric orderNumber
                if 'orderNumber' not in order_doc:
                    # Skip legacy orders that don't have orderNumber field at all
                    logger.warning(f"Skipping legacy order {order_doc.get('id', 'unknown')} without orderNumber field")
                    continue
                
                order_number = order_doc.get('orderNumber', '')
                if not str(order_number).isdigit():
                    # Skip legacy orders with ORD-ABC123 format
                    logger.warning(f"Skipping legacy order {order_doc.get('id', 'unknown')} with non-numeric orderNumber: {order_number}")
                    continue
                
                # Convert ISO string back to datetime if needed
                if isinstance(order_doc.get('orderTime'), str):
                    order_doc['orderTime'] = datetime.fromisoformat(order_doc['orderTime'])
                if isinstance(order_doc.get('completedTime'), str):
                    order_doc['completedTime'] = datetime.fromisoformat(order_doc['completedTime'])
                if isinstance(order_doc.get('estimatedDeliveryTime'), str):
                    order_doc['estimatedDeliveryTime'] = datetime.fromisoformat(order_doc['estimatedDeliveryTime'])
                if isinstance(order_doc.get('actualDeliveryTime'), str):
                    order_doc['actualDeliveryTime'] = datetime.fromisoformat(order_doc['actualDeliveryTime'])
                
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
                # Convert ISO strings back to datetime if needed
                if isinstance(order_doc.get('orderTime'), str):
                    order_doc['orderTime'] = datetime.fromisoformat(order_doc['orderTime'])
                if isinstance(order_doc.get('completedTime'), str):
                    order_doc['completedTime'] = datetime.fromisoformat(order_doc['completedTime'])
                if isinstance(order_doc.get('estimatedDeliveryTime'), str):
                    order_doc['estimatedDeliveryTime'] = datetime.fromisoformat(order_doc['estimatedDeliveryTime'])
                if isinstance(order_doc.get('actualDeliveryTime'), str):
                    order_doc['actualDeliveryTime'] = datetime.fromisoformat(order_doc['actualDeliveryTime'])
                
                return Order(**order_doc)
            return None
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {str(e)}")
            raise e

    async def get_order_by_number(self, order_number: str) -> Optional[Order]:
        """Get order by order number for customer self-service"""
        try:
            order_doc = await self.collection.find_one({"orderNumber": order_number})
            if order_doc:
                order_doc['_id'] = str(order_doc['_id'])
                # Convert ISO strings back to datetime if needed
                if isinstance(order_doc.get('orderTime'), str):
                    order_doc['orderTime'] = datetime.fromisoformat(order_doc['orderTime'])
                if isinstance(order_doc.get('completedTime'), str):
                    order_doc['completedTime'] = datetime.fromisoformat(order_doc['completedTime'])
                if isinstance(order_doc.get('estimatedDeliveryTime'), str):
                    order_doc['estimatedDeliveryTime'] = datetime.fromisoformat(order_doc['estimatedDeliveryTime'])
                if isinstance(order_doc.get('actualDeliveryTime'), str):
                    order_doc['actualDeliveryTime'] = datetime.fromisoformat(order_doc['actualDeliveryTime'])
                
                return Order(**order_doc)
            return None
        except Exception as e:
            logger.error(f"Error fetching order by number {order_number}: {str(e)}")
            raise e

    async def update_item_cooking_status(self, order_id: str, item_name: str, cooking_status: str) -> dict:
        """Update cooking status of a specific item in an order and auto-complete if all items are finished"""
        try:
            # Find the order first
            order_doc = await self.collection.find_one({"id": order_id})
            if not order_doc:
                return {"success": False, "message": "Order not found"}
            
            # Update the specific item's cooking status
            updated = False
            for item in order_doc.get('items', []):
                if item.get('name') == item_name:
                    item['cooking_status'] = cooking_status
                    updated = True
                    break
            
            if not updated:
                return {"success": False, "message": "Item not found in order"}
            
            # Check if all items are finished
            all_items_finished = True
            for item in order_doc.get('items', []):
                if item.get('cooking_status', 'not started') != 'finished':
                    all_items_finished = False
                    break
            
            # Prepare update data
            update_data = {"items": order_doc['items']}
            
            # If all items are finished, automatically complete the order
            if all_items_finished and order_doc.get('status') == 'pending':
                current_time = self.get_eastern_time()
                update_data.update({
                    "status": "completed",
                    "completedTime": current_time.isoformat(),
                    "actualDeliveryTime": current_time.isoformat()
                })
            
            # Update the order in database
            result = await self.collection.update_one(
                {"id": order_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return {
                    "success": True,
                    "message": f"Item '{item_name}' status updated to '{cooking_status}'",
                    "order_auto_completed": all_items_finished and order_doc.get('status') == 'pending'
                }
            
            return {"success": False, "message": "Failed to update item status"}
            
        except Exception as e:
            logger.error(f"Error updating cooking status for item {item_name} in order {order_id}: {str(e)}")
            return {"success": False, "message": "Internal server error"}

    async def get_orders_by_item(self) -> List[dict]:
        """Get orders grouped by food category for view orders functionality"""
        try:
            # Get all pending orders with numeric orderNumber field (skip legacy orders)
            cursor = self.collection.find({"status": "pending", "orderNumber": {"$exists": True}}).sort("orderTime", -1)
            orders = []
            async for order_doc in cursor:
                order_doc['_id'] = str(order_doc['_id'])
                
                # Skip orders with non-numeric order numbers (legacy format)
                order_number = order_doc.get('orderNumber', '')
                if not str(order_number).isdigit():
                    logger.info(f"Skipping legacy order with non-numeric order number: {order_number}")
                    continue
                
                if isinstance(order_doc.get('orderTime'), str):
                    order_doc['orderTime'] = datetime.fromisoformat(order_doc['orderTime'])
                orders.append(order_doc)
            
            # Get menu items to determine categories
            menu_items = await self.menu_service.get_menu()
            item_category_map = {item.name: item.category for item in menu_items.items}
            
            # Group orders by food category
            category_groups = {}
            for order in orders:
                for item in order.get('items', []):
                    item_name = item.get('name')
                    # Get category from menu service, default to 'Other' if not found
                    category = item_category_map.get(item_name, 'Other')
                    
                    if category not in category_groups:
                        category_groups[category] = {
                            'category_name': category,
                            'items': {}
                        }
                    
                    if item_name not in category_groups[category]['items']:
                        category_groups[category]['items'][item_name] = {
                            'item_name': item_name,
                            'total_quantity': 0,
                            'orders': []
                        }
                    
                    category_groups[category]['items'][item_name]['total_quantity'] += item.get('quantity', 0)
                    
                    # Add order info for this item
                    order_info = {
                        'order_id': order.get('id'),
                        'orderNumber': order.get('orderNumber'),
                        'customerName': order.get('customerName'),
                        'quantity': item.get('quantity'),
                        'cooking_status': item.get('cooking_status', 'not started'),
                        'orderTime': order.get('orderTime').isoformat() if order.get('orderTime') else None,
                        'price': item.get('price', 0),
                        'subtotal': item.get('subtotal', 0)
                    }
                    category_groups[category]['items'][item_name]['orders'].append(order_info)
            
            # Convert to list format for frontend
            result = []
            for category_name, category_data in category_groups.items():
                items_list = list(category_data['items'].values())
                result.append({
                    'category_name': category_name,
                    'items': items_list,
                    'total_items': len(items_list)
                })
            
            return result
        except Exception as e:
            logger.error(f"Error getting orders by category: {str(e)}")
            raise e

    async def get_price_analysis(self) -> dict:
        """Get price analysis for all items and generate Excel data"""
        try:
            # Get all completed orders for analysis
            cursor = self.collection.find({"status": "completed"}).sort("orderTime", -1)
            orders = []
            async for order_doc in cursor:
                order_doc['_id'] = str(order_doc['_id'])
                if isinstance(order_doc.get('orderTime'), str):
                    order_doc['orderTime'] = datetime.fromisoformat(order_doc['orderTime'])
                orders.append(order_doc)
            
            # Get menu items for pricing information
            menu_items = await self.menu_service.get_menu()
            menu_item_map = {item.name: item for item in menu_items.items}
            
            # Analyze items
            item_analysis = {}
            total_revenue = 0.0
            total_items_sold = 0
            
            for order in orders:
                for item in order.get('items', []):
                    item_name = item.get('name')
                    quantity = item.get('quantity', 0)
                    price = item.get('price', 0)
                    subtotal = item.get('subtotal', price * quantity)
                    
                    if item_name not in item_analysis:
                        menu_item = menu_item_map.get(item_name, None)
                        item_analysis[item_name] = {
                            'item_name': item_name,
                            'category': menu_item.category if menu_item else 'Other',
                            'unit_price': price,
                            'total_quantity': 0,
                            'total_revenue': 0.0,
                            'order_count': 0
                        }
                    
                    item_analysis[item_name]['total_quantity'] += quantity
                    item_analysis[item_name]['total_revenue'] += subtotal
                    item_analysis[item_name]['order_count'] += 1
                    
                    total_revenue += subtotal
                    total_items_sold += quantity
            
            # Sort by revenue (highest first)
            sorted_items = sorted(
                item_analysis.values(), 
                key=lambda x: x['total_revenue'], 
                reverse=True
            )
            
            return {
                'items': sorted_items,
                'total_revenue': round(total_revenue, 2),
                'total_items_sold': total_items_sold,
                'total_orders': len(orders),
                'average_order_value': round(total_revenue / len(orders), 2) if orders else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting price analysis: {str(e)}")
            raise e
    
    async def update_order(self, order_id: str, order_data: OrderCreate) -> Optional[Order]:
        """Update order with new items, customer name, phone number, payment method, and recalculated prices"""
        try:
            # Calculate prices for each item
            order_items_with_prices = []
            total_amount = 0.0
            
            for item_create in order_data.items:
                # Find menu item to get price
                menu_item = await self.menu_service.get_menu_item(item_create.name.lower().replace(' ', '_'))
                if not menu_item:
                    # Try to find by name match
                    menu_items = await self.menu_service.get_menu()
                    menu_item = None
                    for mi in menu_items.items:
                        if mi.name.lower() == item_create.name.lower():
                            menu_item = mi
                            break
                
                if not menu_item:
                    raise ValueError(f"Menu item '{item_create.name}' not found")
                
                subtotal = menu_item.price * item_create.quantity
                order_item = OrderItem(
                    name=item_create.name,
                    quantity=item_create.quantity,
                    price=menu_item.price,
                    subtotal=subtotal,
                    cooking_status="not started"
                )
                order_items_with_prices.append(order_item)
                total_amount += subtotal
            
            # Calculate new totals and estimated delivery time
            total_items = sum(item.quantity for item in order_items_with_prices)
            current_time = self.get_eastern_time()
            estimated_delivery = current_time + timedelta(minutes=30)
            
            update_data = {
                "customerName": order_data.customerName,
                "items": [item.dict() for item in order_items_with_prices],
                "paymentMethod": order_data.paymentMethod,
                "totalItems": total_items,
                "totalAmount": round(total_amount, 2),
                "estimatedDeliveryTime": estimated_delivery.isoformat()
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
        """Mark order as completed with completion time and create notification"""
        try:
            completion_time = self.get_eastern_time()
            
            # Get the order first to create notification
            order = await self.get_order_by_id(order_id)
            if not order:
                return None
            
            # Update order status in database
            result = await self.collection.update_one(
                {"id": order_id},
                {"$set": {
                    "status": "completed",
                    "completedTime": completion_time.isoformat(),
                    "actualDeliveryTime": completion_time.isoformat()
                }}
            )
            
            if result.modified_count > 0:
                # Create notification for customer
                try:
                    notification = await self.notification_service.create_order_ready_notification(order)
                    logger.info(f"Created notification for order {order_id}: {notification.id}")
                except Exception as notification_error:
                    logger.error(f"Failed to create notification for order {order_id}: {str(notification_error)}")
                    # Don't fail the order completion if notification fails
                
                return await self.get_order_by_id(order_id)
            return None
        except Exception as e:
            logger.error(f"Error completing order {order_id}: {str(e)}")
            raise e
    
    async def get_order_stats(self) -> OrderStats:
        """Get order statistics with delivery time analysis"""
        try:
            # Get today's date range in Eastern Time
            today = self.get_eastern_time().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            
            # Count orders by status for today
            pending_count = await self.collection.count_documents({
                "status": "pending",
                "orderTime": {"$gte": today.isoformat(), "$lt": tomorrow.isoformat()}
            })
            
            completed_count = await self.collection.count_documents({
                "status": "completed",
                "orderTime": {"$gte": today.isoformat(), "$lt": tomorrow.isoformat()}
            })
            
            total_count = pending_count + completed_count
            
            # Calculate average delivery time for completed orders
            completed_orders = await self.collection.find({
                "status": "completed",
                "orderTime": {"$gte": today.isoformat(), "$lt": tomorrow.isoformat()},
                "completedTime": {"$exists": True}
            }).to_list(None)
            
            avg_delivery_time = None
            if completed_orders:
                delivery_times = []
                for order in completed_orders:
                    if order.get('orderTime') and order.get('completedTime'):
                        order_time = datetime.fromisoformat(order['orderTime'])
                        completed_time = datetime.fromisoformat(order['completedTime'])
                        delivery_minutes = (completed_time - order_time).total_seconds() / 60
                        delivery_times.append(delivery_minutes)
                
                if delivery_times:
                    avg_delivery_time = sum(delivery_times) / len(delivery_times)
            
            return OrderStats(
                pending=pending_count,
                completed=completed_count,
                total=total_count,
                averageDeliveryTime=avg_delivery_time
            )
        except Exception as e:
            logger.error(f"Error getting order stats: {str(e)}")
            raise e
    
    async def get_payment_reports(self) -> List[PaymentReport]:
        """Generate payment method reports"""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$paymentMethod",
                        "orderCount": {"$sum": 1},
                        "totalItems": {"$sum": "$totalItems"},
                        "totalAmount": {"$sum": "$totalAmount"},
                        "pendingOrders": {"$sum": {"$cond": [{"$eq": ["$status", "pending"]}, 1, 0]}},
                        "completedOrders": {"$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}},
                        "orders": {"$push": "$$ROOT"}
                    }
                }
            ]
            
            cursor = self.collection.aggregate(pipeline)
            reports = []
            
            async for result in cursor:
                # Calculate average delivery time for this payment method
                avg_delivery_time = None
                delivery_times = []
                
                for order in result.get('orders', []):
                    if (order.get('status') == 'completed' and 
                        order.get('orderTime') and order.get('completedTime')):
                        order_time = datetime.fromisoformat(order['orderTime'])
                        completed_time = datetime.fromisoformat(order['completedTime'])
                        delivery_minutes = (completed_time - order_time).total_seconds() / 60
                        delivery_times.append(delivery_minutes)
                
                if delivery_times:
                    avg_delivery_time = sum(delivery_times) / len(delivery_times)
                
                reports.append(PaymentReport(
                    paymentMethod=result['_id'] or 'cash',
                    orderCount=result['orderCount'],
                    totalItems=result['totalItems'],
                    pendingOrders=result['pendingOrders'],
                    completedOrders=result['completedOrders'],
                    averageDeliveryTime=avg_delivery_time
                ))
            
            return reports
        except Exception as e:
            logger.error(f"Error getting payment reports: {str(e)}")
            raise e
    
    async def get_item_reports(self) -> List[ItemReport]:
        """Generate item-based reports"""
        try:
            # Get all orders
            orders = await self.get_all_orders()
            
            # Analyze items
            item_stats = defaultdict(lambda: {
                'total_ordered': 0,
                'order_count': 0,
                'customers': [],
                'payment_methods': []
            })
            
            for order in orders:
                for item in order.items:
                    item_stats[item.name]['total_ordered'] += item.quantity
                    item_stats[item.name]['order_count'] += 1
                    item_stats[item.name]['customers'].append(order.customerName)
                    item_stats[item.name]['payment_methods'].append(order.paymentMethod)
            
            # Generate reports
            reports = []
            for item_name, stats in item_stats.items():
                # Find most popular payment method
                payment_counter = Counter(stats['payment_methods'])
                popular_payment = payment_counter.most_common(1)[0][0] if payment_counter else 'cash'
                
                # Get recent customers (last 5)
                recent_customers = list(set(stats['customers'][-5:]))
                
                reports.append(ItemReport(
                    itemName=item_name,
                    totalOrdered=stats['total_ordered'],
                    orderCount=stats['order_count'],
                    averageQuantityPerOrder=stats['total_ordered'] / stats['order_count'],
                    popularPaymentMethod=popular_payment,
                    recentOrders=recent_customers
                ))
            
            # Sort by total ordered (descending)
            reports.sort(key=lambda x: x.totalOrdered, reverse=True)
            return reports
            
        except Exception as e:
            logger.error(f"Error getting item reports: {str(e)}")
            raise e
    
    async def delete_order(self, order_id: str) -> bool:
        """Delete/cancel an order"""
        try:
            result = await self.collection.delete_one({"id": order_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting order {order_id}: {str(e)}")
            raise e