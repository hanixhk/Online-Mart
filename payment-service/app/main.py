from fastapi import FastAPI, Depends, HTTPException, status
from typing import AsyncGenerator
from aiokafka import AIOKafkaConsumer
import asyncio
import json
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, Session, create_engine
from .dependencies import get_session, engine
from .models import Transaction
from .schemas import TransactionCreate, TransactionRead, TransactionUpdate
from .crud import create_transaction, get_transaction, list_transactions, update_transaction, delete_transaction
from .events import publish_event
from .settings import BOOTSTRAP_SERVER, KAFKA_PAYMENT_TOPIC
from .payment_providers import  process_stripe_payment

# app = FastAPI(
#     title="Payment Service",
#     version="0.1.0",
#     servers=[
#         {
#             "url": "http://127.0.0.1:8006",
#             "description": "Development Server"
#         }
#     ]
# )

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
    print("Database and tables created successfully.")

async def consume_messages(topic: str, bootstrap_servers: str):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="payment-service-group",
        auto_offset_reset='earliest'
    )
    await consumer.start()
    try:
        async for msg in consumer:
            message = json.loads(msg.value.decode())
            print(f"Received message: {message} on topic {msg.topic}")
            # Process the message as needed
            # Example: Handle order-related events to initiate payments
            if message.get("event") == "order_created":
                data = message.get("data", {})
                order_id = data.get("id")
                user_id = data.get("user_id")
                amount = data.get("total_amount")
                currency = data.get("currency", "USD")
                payment_method = data.get("payment_method", "Stripe")
                
                if order_id and user_id and amount:
                    transaction_data = TransactionCreate(
                        order_id=order_id,
                        user_id=user_id,
                        amount=amount,
                        currency=currency,
                        payment_method=payment_method
                    )
                    with Session(engine) as session:
                        db_transaction = create_transaction(session, transaction_data)
                        asyncio.create_task(
                            handle_payment(db_transaction, session)
                        )
    finally:
        await consumer.stop()
async def handle_payment(db_transaction: Transaction, session: Session):
    """
    Handle payment processing based on transaction data.
    """
    # if db_transaction.payment_method.lower() == "payfast":
        # payment_success = await process_payfast_payment(db_transaction.order_id, db_transaction.amount, db_transaction.currency)
    if db_transaction.payment_method.lower() == "stripe":
        payment_success = await process_stripe_payment(db_transaction.order_id, db_transaction.amount, db_transaction.currency)
    else:
        payment_success = False
    
    # Update transaction status based on payment success
    new_status = "completed" if payment_success else "failed"
    updated_transaction = update_transaction(session, db_transaction.id, TransactionUpdate(status=new_status))
    
    if updated_transaction is None:
        raise HTTPException(status_code=500, detail="Failed to update transaction status")

    await publish_event({"event": "transaction_updated", "data": updated_transaction.dict()})

    # Update transaction status based on payment success
    new_status = "completed" if payment_success else "failed"
    updated_transaction = update_transaction(session, db_transaction.id, TransactionUpdate(status=new_status))
    await publish_event({"event": "transaction_updated", "data": updated_transaction.dict()})

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    create_db_and_tables()
    print("Starting Kafka consumer")
    task = asyncio.create_task(consume_messages(KAFKA_PAYMENT_TOPIC, BOOTSTRAP_SERVER))
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan, title="Payment Service", version="0.1.0")

@app.get("/")
def read_root():
    return {"Service": "Payment Service"}

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# @app.post("/transactions/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
@app.post("/transactions/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_new_transaction(transaction: TransactionCreate, session: Session = Depends(get_session)):
    db_transaction = create_transaction(session, transaction)
    
    if db_transaction is None:
        raise HTTPException(status_code=500, detail="Failed to create transaction")

    await publish_event({"event": "transaction_created", "data": db_transaction.dict()})
    
    # Process payment asynchronously
    # if transaction.payment_method.lower() == "payfast":
        # payment_success = await process_payfast_payment(transaction.order_id, transaction.amount, transaction.currency)
    if transaction.payment_method.lower() == "stripe":
        payment_success = await process_stripe_payment(transaction.order_id, transaction.amount, transaction.currency)
    else:
        raise HTTPException(status_code=400, detail="Unsupported payment method")
    
    # Update transaction status based on payment success
    new_status = "completed" if payment_success else "failed"
    db_transaction = update_transaction(session, db_transaction.id, TransactionUpdate(status=new_status))
    
    if db_transaction is None:
        raise HTTPException(status_code=500, detail="Failed to update transaction")

    await publish_event({"event": "transaction_updated", "data": db_transaction.dict()})
    
    return db_transaction

@app.get("/transactions/{transaction_id}", response_model=TransactionRead)
def read_transaction(transaction_id: int, session: Session = Depends(get_session)):
    db_transaction = get_transaction(session, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@app.get("/transactions/", response_model=list[TransactionRead])
def read_transactions(session: Session = Depends(get_session)):
    transactions = list_transactions(session)
    return transactions

# @app.put("/transactions/{transaction_id}", response_model=TransactionRead)
@app.put("/transactions/{transaction_id}", response_model=TransactionRead)
async def update_existing_transaction(transaction_id: int, transaction_update: TransactionUpdate, session: Session = Depends(get_session)):
    db_transaction = update_transaction(session, transaction_id, transaction_update)
    
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    await publish_event({"event": "transaction_updated", "data": db_transaction.dict()})
    return db_transaction

@app.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_transaction(transaction_id: int, session: Session = Depends(get_session)):
    success = delete_transaction(session, transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    await publish_event({"event": "transaction_deleted", "data": {"id": transaction_id}})
    return


