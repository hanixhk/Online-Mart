from fastapi import FastAPI, Depends, HTTPException, status
from typing import AsyncGenerator
from aiokafka import AIOKafkaConsumer
import asyncio
import json
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, Session
from .dependencies import get_session, engine
from .models import User
from .schemas import UserCreate, UserRead, UserUpdate
from .crud import create_user, get_user, list_users, update_user, authenticate_user
from .events import publish_event
from .settings import BOOTSTRAP_SERVER, KAFKA_USER_TOPIC

# app = FastAPI(
#     title="User Service",
#     version="0.1.0",
#     servers=[
#         {
#             "url": "http://127.0.0.1:8001",
#             "description": "Development Server"
#         }
#     ]
# )
def create_db_and_tables()-> None:
    SQLModel.metadata.create_all(engine)

# async def publish_event(event: dict):
#     producer = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP_SERVER)
#     await producer.start()
#     try:
#         await producer.send_and_wait(KAFKA_USER_TOPIC, json.dumps(event).encode())
#     finally:
#         await producer.stop()


async def consume_messages(topic: str, bootstrap_servers: str):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="user-service-group",
        auto_offset_reset='earliest'
    )
    await consumer.start()
    try:
        async for msg in consumer:
            message = json.loads(msg.value.decode())
            print(f"Received message: {message} on topic {msg.topic}")
            # Process the message 
            if message.get("event") == "user_created":
                user_data = message.get("data")
                with Session(engine) as session:
                    create_user(session, UserCreate(**user_data))
    finally:
        await consumer.stop()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    task = asyncio.create_task(consume_messages(KAFKA_USER_TOPIC, BOOTSTRAP_SERVER))
    yield
    create_db_and_tables()
    task.cancel()

app = FastAPI(lifespan=lifespan, title="User Service", version="0.1.0")

@app.get("/")
def read_root():
    return {"Service": "User Service"}


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.post("/users/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_new_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = create_user(session, user)
    await publish_event({"event": "user_created", "data": db_user.dict(exclude={"hashed_password"})})
    return db_user

@app.get("/users/{user_id}", response_model=UserRead)
def read_user(user_id: int, session: Session = Depends(get_session)):
    db_user = get_user(session, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/", response_model=list[UserRead])
def read_users(session: Session = Depends(get_session)):
    users = list_users(session)
    return users

@app.put("/users/{user_id}", response_model=UserRead)
async def update_existing_user(user_id: int, user_update: UserUpdate, session: Session = Depends(get_session)):
    db_user = update_user(session, user_id, user_update)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    await publish_event({"event": "user_updated", "data": db_user.dict(exclude={"hashed_password"})})
    return db_user

@app.post("/auth/", response_model=UserRead)
async def authenticate(username: str, password: str, session: Session = Depends(get_session)):
    user = authenticate_user(session, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user


