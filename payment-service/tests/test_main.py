from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from unittest.mock import patch
from app.main import app
from app.dependencies import get_session
from app.models import Transaction
from app.schemas import TransactionCreate, TransactionUpdate
from app import settings

import pytest

# Setup test database
test_engine = create_engine(
    settings.TEST_DATABASE_URL,
    connect_args={"sslmode": "require"},
    pool_recycle=300
)
SQLModel.metadata.create_all(test_engine)

def get_session_override():
    with Session(test_engine) as session:
        yield session

app.dependency_overrides[get_session] = get_session_override

client = TestClient(app)

@patch('app.payment_providers.process_payfast_payment', return_value=True)
@patch('app.payment_providers.process_stripe_payment', return_value=True)
def test_create_transaction(mock_stripe, mock_payfast):
    transaction_data = {
        "order_id": 1,
        "user_id": 1,
        "amount": 100.00,
        "currency": "USD",
        "payment_method": "PayFast"
    }
    response = client.post("/transactions/", json=transaction_data)
    assert response.status_code == 201
    data = response.json()
    assert data["order_id"] == transaction_data["order_id"]
    assert data["user_id"] == transaction_data["user_id"]
    assert data["amount"] == float(transaction_data["amount"])
    assert data["currency"] == transaction_data["currency"]
    assert data["payment_method"] == transaction_data["payment_method"]
    assert data["status"] == "completed"

def test_read_transactions():
    response = client.get("/transactions/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_read_transaction():
    # Create a transaction first
    transaction_data = {
        "order_id": 2,
        "user_id": 2,
        "amount": 200.00,
        "currency": "EUR",
        "payment_method": "Stripe"
    }
    with patch('app.payment_providers.process_payfast_payment', return_value=True), \
         patch('app.payment_providers.process_stripe_payment', return_value=True):
        create_response = client.post("/transactions/", json=transaction_data)
    assert create_response.status_code == 201
    created_transaction = create_response.json()
    transaction_id = created_transaction["id"]

    # Retrieve the created transaction
    response = client.get(f"/transactions/{transaction_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == transaction_id
    assert data["order_id"] == transaction_data["order_id"]

@patch('app.payment_providers.process_payfast_payment', return_value=False)
def test_create_transaction_failed_payment(mock_payfast):
    transaction_data = {
        "order_id": 3,
        "user_id": 3,
        "amount": 300.00,
        "currency": "GBP",
        "payment_method": "PayFast"
    }
    response = client.post("/transactions/", json=transaction_data)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "failed"

def test_update_transaction():
    # Create a transaction first
    transaction_data = {
        "order_id": 4,
        "user_id": 4,
        "amount": 400.00,
        "currency": "USD",
        "payment_method": "Stripe"
    }
    with patch('app.payment_providers.process_payfast_payment', return_value=True), \
         patch('app.payment_providers.process_stripe_payment', return_value=True):
        create_response = client.post("/transactions/", json=transaction_data)
    assert create_response.status_code == 201
    created_transaction = create_response.json()
    transaction_id = created_transaction["id"]

    # Update the transaction status
    update_data = {
        "status": "completed"
    }
    response = client.put(f"/transactions/{transaction_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"

def test_delete_transaction():
    # Create a transaction first
    transaction_data = {
        "order_id": 5,
        "user_id": 5,
        "amount": 500.00,
        "currency": "AUD",
        "payment_method": "PayFast"
    }
    with patch('app.payment_providers.process_payfast_payment', return_value=True), \
         patch('app.payment_providers.process_stripe_payment', return_value=True):
        create_response = client.post("/transactions/", json=transaction_data)
    assert create_response.status_code == 201
    created_transaction = create_response.json()
    transaction_id = created_transaction["id"]

    # Delete the transaction
    response = client.delete(f"/transactions/{transaction_id}")
    assert response.status_code == 204

    # Attempt to retrieve the deleted transaction
    response = client.get(f"/transactions/{transaction_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Transaction not found"
