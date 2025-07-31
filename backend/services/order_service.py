from typing import List, Optional
from models.order import Order, OrderCreate, OrderItem, OrderStats, PaymentReport, ItemReport, EASTERN_TZ
from services.notification_service import NotificationService
from services.menu_service import MenuService
from datetime import datetime, timedelta
import logging
import json
import pytz
from collections import defaultdict, Counter
from asyncpg import Pool

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self, pool: Pool):
        self.pool = pool
        self.menu_service = MenuService()
        self.notification_service = None  # Initialize later if needed
    
    def get_eastern_time(self):
        """Get current Eastern time"""
        return datetime.now(EASTERN_TZ)
    
    async def get_next_order_number(self) -> str:
        """Get the next sequential order number using PostgreSQL sequence"""
        try:
            async with self.pool.acquire() as conn:
                # Use nextval to get the next value from the sequence
                # Create sequence if it doesn't exist
                await conn.execute("""
                    CREATE SEQUENCE IF NOT EXISTS order_number_seq
                    START WITH 1
                    INCREMENT BY 1
                    NO MINVALUE
                    NO MAXVALUE
                    CACHE 1
                """)
                
                sequence_value = await conn.fetchval("SELECT nextval('order_number_seq')")
                return str(sequence_value)
        except Exception as e:
            logger.error(f"Error getting next order number: {str(e)}")
            # Fallback to counting existing orders + 1
            count = await conn.fetchval("SELECT COUNT(*) FROM orders")
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
            
            # Convert order items to JSON-compatible format
            items_json = [
                {
                    "name": item.name,
                    "quantity": item.quantity,
                    "price": float(item.price),
                    "subtotal": float(item.subtotal),
                    "cooking_status": item.cooking_status
                }
                for item in order_items_with_prices
            ]

            estimated_delivery = current_time + timedelta(minutes=30)
            
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    INSERT INTO orders (
                        status,
                        order_number,
                        customer_name,
                        payment_method,
                        order_time,
                        estimated_delivery_time,
                        total_items,
                        total_amount,
                        items
                    ) VALUES (
                        'pending',
                        $1,
                        $2,
                        $3,
                        $4,
                        $5,
                        $6,
                        $7,
                        $8
                    ) RETURNING *
                """,
                order_number,
                order_data.customerName,
                order_data.paymentMethod,
                current_time,
                estimated_delivery,
                sum(item.quantity for item in order_items_with_prices),
                round(total_amount, 2),
                items_json
                )
            
            if result:
                # Convert row to dictionary
                order_dict = dict(result)
                return Order(**order_dict)
            else:
                raise Exception("Failed to create order")
                
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            raise e
    
    async def get_all_orders(self) -> List[Order]:
        """Get all orders"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM orders 
                    ORDER BY order_time DESC
                """)
                
                orders = []
                for row in rows:
                    order_dict = dict(row)
                    # Map column names to model field names
                    if 'order_number' in order_dict:
                        order_dict['orderNumber'] = order_dict.pop('order_number')
                    if 'customer_name' in order_dict:
                        order_dict['customerName'] = order_dict.pop('customer_name')
                    if 'payment_method' in order_dict:
                        order_dict['paymentMethod'] = order_dict.pop('payment_method')
                    if 'order_time' in order_dict:
                        order_dict['orderTime'] = order_dict.pop('order_time')
                    if 'completed_time' in order_dict:
                        order_dict['completedTime'] = order_dict.pop('completed_time')
                    if 'estimated_delivery_time' in order_dict:
                        order_dict['estimatedDeliveryTime'] = order_dict.pop('estimated_delivery_time')
                    if 'actual_delivery_time' in order_dict:
                        order_dict['actualDeliveryTime'] = order_dict.pop('actual_delivery_time')
                    if 'delivery_minutes' in order_dict:
                        order_dict['deliveryMinutes'] = order_dict.pop('delivery_minutes')
                    if 'total_items' in order_dict:
                        order_dict['totalItems'] = order_dict.pop('total_items')
                    if 'total_amount' in order_dict:
                        order_dict['totalAmount'] = order_dict.pop('total_amount')
                    
                    # Ensure items is properly converted from JSON string if needed
                    if isinstance(order_dict.get('items'), str):
                        try:
                            order_dict['items'] = json.loads(order_dict['items'])
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse items JSON for order {order_dict.get('id')}")
                            order_dict['items'] = []
                    
                    # Convert items to OrderItem objects
                    if 'items' in order_dict and isinstance(order_dict['items'], list):
                        order_dict['items'] = [OrderItem(**item) for item in order_dict['items']]
                    
                    # Timestamps are automatically handled by asyncpg
                    orders.append(Order(**order_dict))
                return orders
        except Exception as e:
            logger.error(f"Error fetching orders: {str(e)}")
            raise e
    
    async def get_order_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM orders WHERE id = $1",
                    str(order_id)  # Ensure ID is string
                )
                if row:
                    order_dict = dict(row)
                    # Map column names to model field names
                    if 'order_number' in order_dict:
                        order_dict['orderNumber'] = order_dict.pop('order_number')
                    if 'customer_name' in order_dict:
                        order_dict['customerName'] = order_dict.pop('customer_name')
                    if 'payment_method' in order_dict:
                        order_dict['paymentMethod'] = order_dict.pop('payment_method')
                    if 'order_time' in order_dict:
                        order_dict['orderTime'] = order_dict.pop('order_time')
                    if 'completed_time' in order_dict:
                        order_dict['completedTime'] = order_dict.pop('completed_time')
                    if 'estimated_delivery_time' in order_dict:
                        order_dict['estimatedDeliveryTime'] = order_dict.pop('estimated_delivery_time')
                    if 'actual_delivery_time' in order_dict:
                        order_dict['actualDeliveryTime'] = order_dict.pop('actual_delivery_time')
                    if 'delivery_minutes' in order_dict:
                        order_dict['deliveryMinutes'] = order_dict.pop('delivery_minutes')
                    if 'total_items' in order_dict:
                        order_dict['totalItems'] = order_dict.pop('total_items')
                    if 'total_amount' in order_dict:
                        order_dict['totalAmount'] = order_dict.pop('total_amount')
                    
                    # Ensure items is properly converted from JSON string if needed
                    if isinstance(order_dict.get('items'), str):
                        order_dict['items'] = json.loads(order_dict['items'])
                    
                    # Convert items to OrderItem objects
                    if 'items' in order_dict and isinstance(order_dict['items'], list):
                        order_dict['items'] = [OrderItem(**item) for item in order_dict['items']]
                    
                    return Order(**order_dict)
                return None
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {str(e)}")
            raise e

    async def get_order_by_number(self, order_number: str) -> Optional[Order]:
        """Get order by order number for customer self-service"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM orders WHERE order_number = $1",
                    order_number
                )
                if row:
                    return Order(**dict(row))
                return None
        except Exception as e:
            logger.error(f"Error fetching order by number {order_number}: {str(e)}")
            raise e

    async def get_orders_by_status(self, status: str) -> List[Order]:
        """Get all orders with specified status"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT * FROM orders WHERE status = $1",
                    status
                )
                return [Order(**dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error getting orders by status {status}: {str(e)}")
            return []

    async def update_item_cooking_status(self, order_id: str, item_name: str, cooking_status: str) -> dict:
        """Update cooking status of a specific item in an order and auto-complete if all items are finished"""
        try:
            async with self.pool.acquire() as conn:
                # Get the order first
                row = await conn.fetchrow("SELECT * FROM orders WHERE id = $1", order_id)
                if not row:
                    return {"success": False, "message": "Order not found"}
                
                # Convert row to dict and get items
                order_data = dict(row)
                items = order_data.get('items', [])
                
                # Update the specific item's cooking status
                updated = False
                for item in items:
                    if item['name'] == item_name:
                        item['cooking_status'] = cooking_status
                        updated = True
                        break
                
                if not updated:
                    return {"success": False, "message": "Item not found in order"}
                
                # Check if all items are finished
                all_items_finished = all(
                    item.get('cooking_status', 'not started') == 'finished'
                    for item in items
                )
                
                # If all items are finished and order is pending, automatically complete it
                update_fields = []
                params = [items, order_id]  # $1 = items, $2 = order_id
                param_index = 3
                
                if all_items_finished and order_data.get('status') == 'pending':
                    current_time = self.get_eastern_time()
                    update_fields.extend([
                        "status = $" + str(param_index),
                        "completed_time = $" + str(param_index + 1),
                        "actual_delivery_time = $" + str(param_index + 2)
                    ])
                    params.extend(["completed", current_time, current_time])
                
                # Build update query
                update_sql = "UPDATE orders SET items = $1"
                if update_fields:
                    update_sql += ", " + ", ".join(update_fields)
                update_sql += " WHERE id = $2"
                
                # Execute update
                result = await conn.execute(update_sql, *params)
                
                if result == "UPDATE 1":
                    return {
                        "success": True,
                        "message": f"Item '{item_name}' status updated to '{cooking_status}'",
                        "order_auto_completed": all_items_finished and order_data.get('status') == 'pending'
                    }
                
                return {"success": False, "message": "Failed to update item status"}
                
        except Exception as e:
            logger.error(f"Error updating cooking status for item {item_name} in order {order_id}: {str(e)}")
            return {"success": False, "message": "Internal server error"}

    async def get_orders_by_item(self) -> List[dict]:
        """Get orders grouped by food category for view orders functionality"""
        try:
            async with self.pool.acquire() as conn:
                # Get all pending orders
                rows = await conn.fetch("""
                    SELECT * FROM orders 
                    WHERE status = 'pending' 
                    ORDER BY order_time DESC
                """)
                
                # Get menu items to determine categories
                menu_items = await self.menu_service.get_menu()
                item_category_map = {item.name: item.category for item in menu_items.items}
                
                # Group orders by food category
                category_groups = {}
                for row in rows:
                    order = dict(row)
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
                            'orderNumber': order.get('order_number'),
                            'customerName': order.get('customer_name'),
                            'quantity': item.get('quantity'),
                            'cooking_status': item.get('cooking_status', 'not started'),
                            'orderTime': order.get('order_time').isoformat() if order.get('order_time') else None,
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
            async with self.pool.acquire() as conn:
                # Get all completed orders for analysis
                rows = await conn.fetch("""
                    SELECT * FROM orders 
                    WHERE status = 'completed' 
                    ORDER BY order_time DESC
                """)
                
                # Get menu items for pricing information
                menu_items = await self.menu_service.get_menu()
                menu_item_map = {item.name: item for item in menu_items.items}
                
                # Analyze items
                item_analysis = {}
                total_revenue = 0.0
                total_items_sold = 0
                
                for row in rows:
                    order = dict(row)
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
                    'total_orders': len(rows),
                    'average_order_value': round(total_revenue / len(rows), 2) if rows else 0
                }
                
        except Exception as e:
            logger.error(f"Error getting price analysis: {str(e)}")
            raise e
    
    async def update_order(self, order_id: str, order_update: dict) -> Optional[Order]:
        """Update order with given fields"""
        try:
            # Build SET clause and parameters for dynamic updates
            set_items = []
            params = [order_id]  # First parameter is order_id
            param_index = 2  # Start from $2 since $1 is order_id
            
            for key, value in order_update.items():
                set_items.append(f"{key} = ${param_index}")
                params.append(value)
                param_index += 1
            
            set_clause = ", ".join(set_items)
            
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    f"UPDATE orders SET {set_clause} WHERE id = $1 RETURNING *",
                    *params
                )
                if row:
                    return Order(**dict(row))
                return None
        except Exception as e:
            logger.error(f"Error updating order {order_id}: {str(e)}")
            raise
    
    async def complete_order(self, order_id: str) -> Optional[Order]:
        """Mark order as completed with completion time and create notification"""
        try:
            completion_time = self.get_eastern_time()
            
            # Get the order first to create notification
            order = await self.get_order_by_id(order_id)
            if not order:
                return None
            
            async with self.pool.acquire() as conn:
                # Update order status in database
                row = await conn.fetchrow("""
                    UPDATE orders 
                    SET status = $1, 
                        completed_time = $2, 
                        actual_delivery_time = $3 
                    WHERE id = $4 
                    RETURNING *
                """, 
                'completed', 
                completion_time,
                completion_time,
                order_id
                )
                
                if row:
                    # Create notification for customer
                    try:
                        notification = await self.notification_service.create_order_ready_notification(order)
                        logger.info(f"Created notification for order {order_id}: {notification.id}")
                    except Exception as notification_error:
                        logger.error(f"Failed to create notification for order {order_id}: {str(notification_error)}")
                        # Don't fail the order completion if notification fails
                    
                    return Order(**dict(row))
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
            
            async with self.pool.acquire() as conn:
                # Count orders by status for today
                pending_count = await conn.fetchval("""
                    SELECT COUNT(*) FROM orders 
                    WHERE status = 'pending' 
                    AND order_time >= $1 AND order_time < $2
                """, today, tomorrow)
                
                completed_count = await conn.fetchval("""
                    SELECT COUNT(*) FROM orders 
                    WHERE status = 'completed' 
                    AND order_time >= $1 AND order_time < $2
                """, today, tomorrow)
                
                total_count = pending_count + completed_count
                
                # Calculate average delivery time for completed orders
                avg_delivery_time = await conn.fetchval("""
                    SELECT AVG(EXTRACT(EPOCH FROM (completed_time - order_time))/60) 
                    FROM orders 
                    WHERE status = 'completed' 
                    AND order_time >= $1 AND order_time < $2
                    AND completed_time IS NOT NULL
                """, today, tomorrow)
                
                return OrderStats(
                    pending=pending_count,
                    completed=completed_count,
                    total=total_count,
                    averageDeliveryTime=avg_delivery_time
                )
        except Exception as e:
            logger.error(f"Error getting order stats: {str(e)}")
            raise e
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
        """Delete order by ID"""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute(
                    "DELETE FROM orders WHERE id = $1",
                    order_id
                )
                return result == "DELETE 1"
        except Exception as e:
            logger.error(f"Error deleting order {order_id}: {str(e)}")
            return False