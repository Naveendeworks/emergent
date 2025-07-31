from fastapi import FastAPI, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
import asyncio
from db import get_pg_pool
from models.order import Order, OrderCreate, OrderItemCookingUpdate, OrderItem
from services.order_service import OrderService

import os
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Order Management API",
    description="API for managing orders with real-time updates and cooking status tracking",
    version="1.0.0"
)

pg_pool = None
order_service = None

async def run_migrations(pool):
    try:
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        for file in sorted(os.listdir(migrations_dir)):
            if file.endswith('.sql'):
                migration_path = os.path.join(migrations_dir, file)
                logger.info(f"Running migration: {file}")
                
                with open(migration_path, 'r') as f:
                    migration_sql = f.read()
                
                async with pool.acquire() as conn:
                    async with conn.transaction():
                        await conn.execute(migration_sql)
                        
        logger.info("All migrations completed successfully")
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise

@app.on_event("startup")
async def startup():
    global pg_pool, order_service
    try:
        # Initialize database connection pool
        pg_pool = await get_pg_pool()
        
        # Run database migrations
        await run_migrations(pg_pool)
        
        # Initialize order service
        order_service = OrderService(pg_pool)
        
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown():
    from db import close_pg_pool
    await close_pg_pool()

@app.on_event("shutdown")
async def shutdown():
    await pg_pool.close()

def get_order_service():
    if not order_service:
        raise HTTPException(status_code=503, detail="Order service not initialized")
    return order_service

@app.post("/orders/", response_model=Order, tags=["orders"],
    summary="Create a new order",
    description="Create a new order with items, customer details, and payment method")
async def create_order(
    order: OrderCreate,
    service: OrderService = Depends(get_order_service)
):
    return await service.create_order(order)

@app.get("/orders/", response_model=List[Order], tags=["orders"],
    summary="Get all orders",
    description="Retrieve all orders, optionally filtered by status")
async def get_orders(
    status: Optional[str] = Query(None, description="Filter orders by status (pending/completed)"),
    service: OrderService = Depends(get_order_service)
):
    orders = await service.get_all_orders()
    if status:
        return [order for order in orders if order.status == status]
    return orders

@app.get("/orders/{order_id}", response_model=Order, tags=["orders"],
    summary="Get order by ID",
    description="Retrieve a specific order by its ID")
async def get_order(
    order_id: str,
    service: OrderService = Depends(get_order_service)
):
    order = await service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.put("/orders/{order_id}/cooking-status", tags=["orders"],
    summary="Update cooking status",
    description="Update the cooking status of a specific item in an order")
async def update_cooking_status(
    update: OrderItemCookingUpdate,
    service: OrderService = Depends(get_order_service)
):
    result = await service.update_item_cooking_status(
        update.order_id,
        update.item_name,
        update.cooking_status
    )
    if not result:
        raise HTTPException(status_code=404, detail="Order or item not found")
    return result

@app.get("/orders/by-number/{order_number}", response_model=Order, tags=["orders"],
    summary="Get order by number",
    description="Retrieve a specific order by its order number")
async def get_order_by_number(
    order_number: str,
    service: OrderService = Depends(get_order_service)
):
    order = await service.get_order_by_number(order_number)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/orders/summary/items", tags=["reports"],
    summary="Get orders by item",
    description="Get a summary of orders grouped by menu items")
async def get_orders_by_item(
    service: OrderService = Depends(get_order_service)
):
    return await service.get_orders_by_item()

@app.get("/orders/analysis/price", tags=["reports"],
    summary="Get price analysis",
    description="Get price-related analytics for all orders")
async def get_price_analysis(
    service: OrderService = Depends(get_order_service)
):
    return await service.get_price_analysis()

@app.get("/health", tags=["health"],
    summary="Health check",
    description="Verify the API is running and database is accessible")
async def health():
    async with pg_pool.acquire() as conn:
        await conn.execute("SELECT 1")
    return {"status": "ok"}