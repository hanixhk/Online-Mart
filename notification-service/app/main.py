from fastapi import FastAPI, Depends, HTTPException, status
from typing import AsyncGenerator
from aiokafka import AIOKafkaConsumer
import asyncio
import json
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, Session, create_engine

from .dependencies import get_session, engine
from .models import Notification
from .schemas import NotificationCreate, NotificationRead, NotificationUpdate
from .crud import create_notification, get_notification, list_notifications, update_notification, delete_notification
from .events import publish_event
from .settings import BOOTSTRAP_SERVER, KAFKA_NOTIFICATION_TOPIC
from .notification_providers import send_email, send_sms

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
    print("Database and tables created")
    

async def consume_messages(topic: str, bootstrap_servers: str):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="notification-service-group",
        auto_offset_reset='earliest'
    )
    await consumer.start()
    try:
        async for msg in consumer:
            message = json.loads(msg.value.decode())
            print(f"Received message: {message} on topic {msg.topic}")
            await handle_event(message)
    finally:
        await consumer.stop()

async def handle_event(message: dict):
    event_type = message.get("event")
    data = message.get("data", {})
    
    if event_type == "order_created":
        user_id = data.get("user_id")
        order_id = data.get("id")
        # Fetch user details from User Service (assuming an API is available)
        # For simplicity, we'll mock user email and phone
        user_email = f"user{user_id}@example.com"
        user_phone = f"+1234567890"
        subject = f"Order Confirmation - Order #{order_id}"
        body = f"Thank you for your order #{order_id}. Your order is being processed."
        
        email_sent = await send_email(user_email, subject, body)
        sms_sent = send_sms(user_phone, f"Your order #{order_id} has been received.")
        
        if email_sent and sms_sent:
            # Optionally, create a notification record
            # Skipping for brevity
            pass
        else:
            # Handle failures
            pass
    
    elif event_type == "payment_completed":
        user_id = data.get("user_id")
        order_id = data.get("order_id")
        # Similar to above, send confirmation notifications
        user_email = f"user{user_id}@example.com"
        user_phone = f"+1234567890"
        subject = f"Payment Received - Order #{order_id}"
        body = f"Your payment for order #{order_id} has been successfully processed."
        
        email_sent = await send_email(user_email, subject, body)
        sms_sent = send_sms(user_phone, f"Your payment for order #{order_id} was successful.")
        
        if email_sent and sms_sent:
            pass
        else:
            pass
    
    # Handle other event types as needed

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    create_db_and_tables()
    task = asyncio.create_task(consume_messages(KAFKA_NOTIFICATION_TOPIC, BOOTSTRAP_SERVER))
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan, title="Notification Service", version="0.1.0")

@app.get("/")
def read_root():
    return {"Service": "Notification Service"}



@app.post("/notifications/", response_model=NotificationRead, status_code=status.HTTP_201_CREATED)
async def create_new_notification(notification: NotificationCreate, session: Session = Depends(get_session)):
    db_notification = create_notification(session, notification)
    await publish_event({"event": "notification_created", "data": db_notification.dict()})
    return db_notification

@app.get("/notifications/{notification_id}", response_model=NotificationRead)
def read_notification(notification_id: int, session: Session = Depends(get_session)):
    db_notification = get_notification(session, notification_id)
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return db_notification

@app.get("/notifications/", response_model=list[NotificationRead])
def read_notifications(session: Session = Depends(get_session)):
    notifications = list_notifications(session)
    return notifications

@app.put("/notifications/{notification_id}", response_model=NotificationRead)
async def update_existing_notification(notification_id: int, notification_update: NotificationUpdate, session: Session = Depends(get_session)):
    db_notification = update_notification(session, notification_id, notification_update)
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    await publish_event({"event": "notification_updated", "data": db_notification.dict()})
    return db_notification

@app.delete("/notifications/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_notification(notification_id: int, session: Session = Depends(get_session)):
    success = delete_notification(session, notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    await publish_event({"event": "notification_deleted", "data": {"id": notification_id}})
    return
