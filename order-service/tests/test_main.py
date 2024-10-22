from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.main import app
from app.dependencies import get_session
from app.models import Order
from app.schemas import OrderCreate
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

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Service": "Order Service"}

def test_create_order():
    order_data = {
        "user_id": 1,
        "product_id": 2,
        "quantity": 3
    }
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == order_data["user_id"]
    assert data["product_id"] == order_data["product_id"]
    assert data["quantity"] == order_data["quantity"]
    assert data["status"] == "pending"

def test_read_orders():
    response = client.get("/orders/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_read_order():
    # Create an order first
    order_data = {
        "user_id": 1,
        "product_id": 2,
        "quantity": 3
    }
    create_response = client.post("/orders/", json=order_data)
    assert create_response.status_code == 200
    created_order = create_response.json()
    order_id = created_order["id"]

    # Retrieve the created order
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id

def test_update_order_status():
    # Create an order first
    order_data = {
        "user_id": 1,
        "product_id": 2,
        "quantity": 3
    }
    create_response = client.post("/orders/", json=order_data)
    assert create_response.status_code == 200
    created_order = create_response.json()
    order_id = created_order["id"]

    # Update the order status
    new_status = "completed"
    response = client.put(f"/orders/{order_id}?status={new_status}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == new_status
