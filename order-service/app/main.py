from fastapi import FastAPI, Depends, HTTPException
from typing import AsyncGenerator
from aiokafka import AIOKafkaConsumer
import asyncio
import json
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, Session
from .dependencies import get_session, engine
from .models import Order
from .schemas import OrderCreate, OrderRead
from .crud import create_order, get_order, list_orders, update_order_status,delete_orders
from .events import publish_event
# app = FastAPI(
#     title="Order Service",
#     version="0.1.0",
#     # servers=[
#     #     {
#     #         "url": "http://127.0.0.1:8004",
#     #         "description": "Development Server"
#     #     }
#     # ]
# )


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


async def consume_messages(topic: str, bootstrap_servers: str):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="createorder-service-group",
        auto_offset_reset='earliest'
    )
    await consumer.start()
    try:
        async for msg in consumer:
            message = json.loads(msg.value.decode())
            print(f"Received message: {message} on topic {msg.topic}")
            # Process the message 
            if message.get("event") == "order_created":
                order_data = message.get("data")
                with Session(engine) as session:
                    create_order(session, OrderCreate(**order_data))

    finally:
        await consumer.stop()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    task = asyncio.create_task(consume_messages('createorder-topic', 'broker:19092'))
    yield
    create_db_and_tables()
    task.cancel()

app = FastAPI(lifespan=lifespan, title="Order Service", version="0.1.0")


# def create_db_and_tables() -> None:
#     SQLModel.metadata.create_all(engine)


# # The first part of the function, before the yield, will
# @asynccontextmanager
# async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
#     print("Creating tabl...")

#     task = asyncio.create_task(consume_messages(
#         "createorder-response", 'broker:19093'))
#     create_db_and_tables()
#     print("\n\n LIFESPAN created!! \n\n")
#     yield





# @app.on_event("startup")
# def on_startup():
#     SQLModel.metadata.create_all(engine)
#     print("creating tables")




@app.get("/")
def read_root():
    return {"Service": "Order Service"}


@app.post("/orders/", response_model=OrderRead)
async def create_new_order(createorder: OrderCreate, session: Session = Depends(get_session)):
    db_order = create_order(session, createorder)
    await publish_event({"event": "order_created", "data": db_order.dict()})
    return db_order

@app.get("/orders/{order_id}", response_model=OrderRead)
def read_order(order_id: int, session: Session = Depends(get_session)):
    db_order = get_order(session, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@app.get("/orders/", response_model=list[OrderRead])
def read_orders(session: Session = Depends(get_session)):
    orders = list_orders(session)
    return orders

@app.put("/orders/{order_id}", response_model=OrderRead)
async def update_order(order_id: int, status: str, session: Session = Depends(get_session)):
    db_order = update_order_status(session, order_id, status)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    await publish_event({"event": "order_updated", "data": db_order.dict()})
    return db_order

@app.delete("/orders/{order_id}")
async def delete_order(order_id: int, session: Session = Depends(get_session)):
    order_deleted = delete_orders(session, order_id)

    if not order_deleted:
        raise HTTPException(status_code=404, detail="Order not found")

    await publish_event({"event": "order_deleted", "data": {"order_id": order_id}})
    return {"message": "Order deleted successfully"}

