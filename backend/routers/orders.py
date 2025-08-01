from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.order import Order, OrderCreate, OrderStats, OrderItemCookingUpdate
from services.order_service import OrderService
from routers.auth import get_current_user
from motor.motor_asyncio import AsyncIOMotorDatabase
import os
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

router = APIRouter(prefix="/orders", tags=["orders"])

def get_order_service() -> OrderService:
    return OrderService(db)

@router.post("/", response_model=Order, status_code=201)
async def create_order(
    order_data: OrderCreate,
    order_service: OrderService = Depends(get_order_service),
    current_user: str = Depends(get_current_user)
):
    """Create a new order (requires authentication)"""
    try:
        order = await order_service.create_order(order_data)
        return order
    except Exception as e:
        logger.error(f"Error in create_order endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create order")

@router.get("/", response_model=List[Order])
async def get_orders(
    order_service: OrderService = Depends(get_order_service),
    current_user: str = Depends(get_current_user)
):
    """Get all orders (requires authentication)"""
    try:
        orders = await order_service.get_all_orders()
        return orders
    except Exception as e:
        logger.error(f"Error in get_orders endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch orders")

@router.get("/stats/summary", response_model=OrderStats)
async def get_order_stats(
    order_service: OrderService = Depends(get_order_service),
    current_user: str = Depends(get_current_user)
):
    """Get order statistics (requires authentication)"""
    try:
        stats = await order_service.get_order_stats()
        return stats
    except Exception as e:
        logger.error(f"Error in get_order_stats endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch order statistics")

@router.get("/view-orders", response_model=List[dict])
async def get_orders_by_item(
    order_service: OrderService = Depends(get_order_service),
    current_user: str = Depends(get_current_user)
):
    """Get orders grouped by menu item (requires authentication)"""
    try:
        item_orders = await order_service.get_orders_by_item()
        return item_orders
    except Exception as e:
        logger.error(f"Error in get_orders_by_item endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch orders by item")

@router.get("/myorder/{order_number}", response_model=Order)
async def get_order_by_number(
    order_number: str,
    order_service: OrderService = Depends(get_order_service)
):
    """Get order by order number (no authentication required - customer self-service)"""
    try:
        # Validate order number format (should be a simple number like 1, 2, 3...)
        if not order_number or not order_number.strip() or not order_number.isdigit() or int(order_number) <= 0:
            raise HTTPException(status_code=400, detail="Invalid order number format")
        
        order = await order_service.get_order_by_number(order_number)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_order_by_number endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch order")

@router.patch("/cooking-status")
async def update_cooking_status(
    update_data: OrderItemCookingUpdate,
    order_service: OrderService = Depends(get_order_service),
    current_user: str = Depends(get_current_user)
):
    """Update cooking status of an item in an order (requires authentication)"""
    try:
        result = await order_service.update_item_cooking_status(
            update_data.order_id, 
            update_data.item_name, 
            update_data.cooking_status
        )
        
        if not result["success"]:
            if "not found" in result["message"]:
                raise HTTPException(status_code=404, detail=result["message"])
            else:
                raise HTTPException(status_code=400, detail=result["message"])
        
        response = {
            "message": result["message"],
            "status": update_data.cooking_status
        }
        
        if result.get("order_auto_completed"):
            response["order_auto_completed"] = True
            response["message"] += " - Order automatically completed!"
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_cooking_status endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update cooking status")

@router.get("/price-analysis", response_model=dict)
async def get_price_analysis(
    order_service: OrderService = Depends(get_order_service),
    current_user: str = Depends(get_current_user)
):
    """Get price analysis for all items (requires authentication)"""
    try:
        analysis = await order_service.get_price_analysis()
        return analysis
    except Exception as e:
        logger.error(f"Error in get_price_analysis endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch price analysis")

@router.get("/search/{query}", response_model=List[Order])
async def search_orders(
    query: str,
    order_service: OrderService = Depends(get_order_service),
    current_user: str = Depends(get_current_user)
):
    """Search orders by customer name (requires authentication)"""
    try:
        orders = await order_service.search_orders_by_customer(query)
        return orders
    except Exception as e:
        logger.error(f"Error in search_orders endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search orders")

@router.put("/{order_id}/complete", response_model=Order)
async def complete_order(
    order_id: str,
    order_service: OrderService = Depends(get_order_service),
    current_user: str = Depends(get_current_user)
):
    """Mark order as completed (requires authentication)"""
    try:
        order = await order_service.complete_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in complete_order endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to complete order")

@router.put("/{order_id}", response_model=Order)
async def update_order(
    order_id: str,
    order_data: OrderCreate,
    order_service: OrderService = Depends(get_order_service),
    current_user: str = Depends(get_current_user)
):
    """Update order items and customer name (requires authentication)"""
    try:
        order = await order_service.update_order(order_id, order_data)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_order endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update order")

@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: str,
    order_service: OrderService = Depends(get_order_service),
    current_user: str = Depends(get_current_user)
):
    """Get order by ID (requires authentication)"""
    try:
        order = await order_service.get_order_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_order endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch order")

@router.delete("/{order_id}")
async def cancel_order(
    order_id: str,
    order_service: OrderService = Depends(get_order_service),
    current_user: str = Depends(get_current_user)
):
    """Cancel/delete an order (requires authentication)"""
    try:
        deleted = await order_service.delete_order(order_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Order not found")
        return {"message": "Order cancelled successfully", "order_id": order_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in cancel_order endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cancel order")