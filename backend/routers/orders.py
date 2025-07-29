from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.order import Order, OrderCreate, OrderStats
from services.order_service import OrderService
from motor.motor_asyncio import AsyncIOMotorDatabase
import os
from motor.motor_asyncio import AsyncIOMotorClient
import logging

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
    order_service: OrderService = Depends(get_order_service)
):
    """Create a new order"""
    try:
        order = await order_service.create_order(order_data)
        return order
    except Exception as e:
        logger.error(f"Error in create_order endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create order")

@router.get("/", response_model=List[Order])
async def get_orders(
    order_service: OrderService = Depends(get_order_service)
):
    """Get all orders"""
    try:
        orders = await order_service.get_all_orders()
        return orders
    except Exception as e:
        logger.error(f"Error in get_orders endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch orders")

@router.put("/{order_id}/complete", response_model=Order)
async def complete_order(
    order_id: str,
    order_service: OrderService = Depends(get_order_service)
):
    """Mark order as completed"""
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

@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: str,
    order_service: OrderService = Depends(get_order_service)
):
    """Get order by ID"""
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

@router.get("/stats/summary", response_model=OrderStats)
async def get_order_stats(
    order_service: OrderService = Depends(get_order_service)
):
    """Get order statistics"""
    try:
        stats = await order_service.get_order_stats()
        return stats
    except Exception as e:
        logger.error(f"Error in get_order_stats endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch order statistics")

@router.delete("/{order_id}")
async def delete_order(
    order_id: str,
    order_service: OrderService = Depends(get_order_service)
):
    """Delete an order (for testing purposes)"""
    try:
        deleted = await order_service.delete_order(order_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Order not found")
        return {"message": "Order deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_order endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete order")