import os
from fastapi import FastAPI, HTTPException
from db import database, engine, metadata
from models import orders
from pydantic import BaseModel
from sqlalchemy import select, insert, update

app = FastAPI()

@app.on_event("startup")
async def startup():
    metadata.create_all(engine)
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

class Order(BaseModel):
    token: str
    status: str

@app.post("/orders/")
async def create_order(order: Order):
    query = insert(orders).values(token=order.token, status=order.status)
    await database.execute(query)
    return {"message": "Order created"}

@app.get("/orders/")
async def read_orders():
    query = select(orders)
    rows = await database.fetch_all(query)
    return [dict(r) for r in rows]

@app.put("/orders/{order_id}")
async def update_order(order_id: int, order: Order):
    query = (
        update(orders)
        .where(orders.c.id == order_id)
        .values(token=order.token, status=order.status)
    )
    result = await database.execute(query)
    if result is None:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Updated"}

@app.get("/health")
async def health():
    return {"status": "ok"}
