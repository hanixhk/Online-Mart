from fastapi import FastAPI, Depends, HTTPException, status
from typing import AsyncGenerator
from aiokafka import AIOKafkaConsumer
import asyncio
import json
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, Session
from .dependencies import get_session, engine
from .models import Product
from .schemas import ProductCreate, ProductRead, ProductUpdate
from .crud import create_product, get_product, list_products, update_product, delete_product
from .events import publish_event
from .settings import BOOTSTRAP_SERVER, KAFKA_PRODUCT_TOPIC

# app = FastAPI(
#     title="Product Service",
#     version="0.1.0",
#     servers=[
#         {
#             "url": "http://127.0.0.1:8005",
#             "description": "Development Server"
#         }
#     ]
# )
def create_db_and_tables() ->None:
    SQLModel.metadata.create_all(engine)


async def consume_messages(topic: str, bootstrap_servers: str):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="product-service-group",
        auto_offset_reset='earliest'
    )
    await consumer.start()
    try:
        async for msg in consumer:
            message = json.loads(msg.value.decode())
            print(f"Received message: {message} on topic {msg.topic}")
            # Process the message as needed
            if message.get("event") == "product_created":
                product_data = message.get("data")
                with Session(engine) as session:
                    create_product(session, ProductCreate(**product_data))
    finally:
        await consumer.stop()



@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    create_db_and_tables()
    task = asyncio.create_task(consume_messages(KAFKA_PRODUCT_TOPIC, BOOTSTRAP_SERVER))
    try:
        yield
    finally:
        task.cancel()

app = FastAPI(lifespan=lifespan, title="Product Service", version="0.1.0")

@app.get("/")
def read_root():
    return {"Service": "Product Service"}


# @app.on_event("startup")
# def on_startup():
#     SQLModel.metadata.create_all(engine)

@app.post("/products/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_new_product(product: ProductCreate, session: Session = Depends(get_session)):
    db_product = create_product(session, product)
    await publish_event({"event": "product_created", "data": db_product.dict()})
    return db_product

@app.get("/products/{product_id}", response_model=ProductRead)
def read_product(product_id: int, session: Session = Depends(get_session)):
    db_product = get_product(session, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.get("/products/", response_model=list[ProductRead])
def read_products(session: Session = Depends(get_session)):
    products = list_products(session)
    return products

@app.put("/products/{product_id}", response_model=ProductRead)
async def update_existing_product(product_id: int, product_update: ProductUpdate, session: Session = Depends(get_session)):
    db_product = update_product(session, product_id, product_update)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    await publish_event({"event": "product_updated", "data": db_product.dict()})
    return db_product

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_product(product_id: int, session: Session = Depends(get_session)):
    success = delete_product(session, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    await publish_event({"event": "product_deleted", "data": {"id": product_id}})
    return

