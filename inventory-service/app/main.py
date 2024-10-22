from fastapi import FastAPI, Depends, HTTPException, status
from typing import AsyncGenerator
from aiokafka import AIOKafkaConsumer
import asyncio
import json
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, Session, create_engine
from .dependencies import get_session, engine
from .models import Inventory
from .schemas import InventoryCreate, InventoryRead, InventoryUpdate
from .crud import create_inventory, get_inventory, list_inventories, update_inventory, delete_inventory, decrease_inventory, increase_inventory
from .events import publish_event
from .settings import BOOTSTRAP_SERVER, KAFKA_INVENTORY_TOPIC

def create_db_and_tables() ->None:
    SQLModel.metadata.create_all(engine)
    print("Database and tables created successfully.")  


async def consume_messages(topic: str, bootstrap_servers: str):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="inventory-service-group",
        auto_offset_reset='earliest'
    )
    await consumer.start()
    try:
        async for msg in consumer:
            message = json.loads(msg.value.decode())
            print(f"Received message: {message} on topic {msg.topic}")
            # Process the message as needed
            # Example: If an order is created, decrease inventory
            if message.get("event") == "order_created":
                data = message.get("data", {})
                product_id = data.get("product_id")
                quantity = data.get("quantity")
                if product_id and quantity:
                    with Session(engine) as session:
                        result = decrease_inventory(session, product_id, quantity)
                        if result:
                            await publish_event({"event": "inventory_decreased", "data": result.dict()})
                        else:
                            print(f"Insufficient inventory for product_id: {product_id}")
    finally:
        await consumer.stop()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    create_db_and_tables()
    task = asyncio.create_task(consume_messages(KAFKA_INVENTORY_TOPIC, BOOTSTRAP_SERVER))
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan, title="Inventory Service", version="0.1.0")

@app.get("/")
def read_root():
    return {"Service": "Inventory Service"}

@app.post("/inventory/", response_model=InventoryRead, status_code=status.HTTP_201_CREATED)
async def create_new_inventory(inventory: InventoryCreate, session: Session = Depends(get_session)):
    db_inventory = create_inventory(session, inventory)
    await publish_event({"event": "inventory_created", "data": db_inventory.dict()})
    return db_inventory

@app.get("/inventory/{inventory_id}", response_model=InventoryRead)
def read_inventory(inventory_id: int, session: Session = Depends(get_session)):
    db_inventory = get_inventory(session, inventory_id)
    if not db_inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return db_inventory

@app.get("/inventory/", response_model=list[InventoryRead])
def read_inventories(session: Session = Depends(get_session)):
    inventories = list_inventories(session)
    return inventories

@app.put("/inventory/{inventory_id}", response_model=InventoryRead)
async def update_existing_inventory(inventory_id: int, inventory_update: InventoryUpdate, session: Session = Depends(get_session)):
    db_inventory = update_inventory(session, inventory_id, inventory_update)
    if not db_inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    await publish_event({"event": "inventory_updated", "data": db_inventory.dict()})
    return db_inventory

@app.delete("/inventory/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_inventory(inventory_id: int, session: Session = Depends(get_session)):
    success = delete_inventory(session, inventory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    await publish_event({"event": "inventory_deleted", "data": {"id": inventory_id}})
    return

@app.post("/inventory/decrease/", status_code=status.HTTP_200_OK)
async def decrease_inventory_endpoint(product_id: int, quantity: int, session: Session = Depends(get_session)):
    db_inventory = decrease_inventory(session, product_id, quantity)
    if not db_inventory:
        raise HTTPException(status_code=400, detail="Insufficient inventory or product not found")
    await publish_event({"event": "inventory_decreased", "data": db_inventory.dict()})
    return {"message": "Inventory decreased successfully", "inventory": db_inventory.dict()}

@app.post("/inventory/increase/", status_code=status.HTTP_200_OK)
async def increase_inventory_endpoint(product_id: int, quantity: int, session: Session = Depends(get_session)):
    db_inventory = increase_inventory(session, product_id, quantity)
    if not db_inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    await publish_event({"event": "inventory_increased", "data": db_inventory.dict()})
    return {"message": "Inventory increased successfully", "inventory": db_inventory.dict()}

