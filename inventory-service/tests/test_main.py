from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.main import app
from app.dependencies import get_session
from app.models import Inventory
from app.schemas import InventoryCreate
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
    assert response.json() == {"Service": "Inventory Service"}

def test_create_inventory():
    inventory_data = {
        "product_id": 1,
        "quantity": 50
    }
    response = client.post("/inventory/", json=inventory_data)
    assert response.status_code == 201
    data = response.json()
    assert data["product_id"] == inventory_data["product_id"]
    assert data["quantity"] == inventory_data["quantity"]
    assert data["is_available"] == True

def test_read_inventories():
    response = client.get("/inventory/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_read_inventory():
    # Create an inventory item first
    inventory_data = {
        "product_id": 2,
        "quantity": 30
    }
    create_response = client.post("/inventory/", json=inventory_data)
    assert create_response.status_code == 201
    created_inventory = create_response.json()
    inventory_id = created_inventory["id"]

    # Retrieve the created inventory
    response = client.get(f"/inventory/{inventory_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == inventory_id
    assert data["product_id"] == inventory_data["product_id"]

def test_update_inventory():
    # Create an inventory item first
    inventory_data = {
        "product_id": 3,
        "quantity": 20
    }
    create_response = client.post("/inventory/", json=inventory_data)
    assert create_response.status_code == 201
    created_inventory = create_response.json()
    inventory_id = created_inventory["id"]

    # Update the inventory's quantity and availability
    update_data = {
        "quantity": 25,
        "is_available": True
    }
    response = client.put(f"/inventory/{inventory_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == update_data["quantity"]
    assert data["is_available"] == update_data["is_available"]

def test_delete_inventory():
    # Create an inventory item first
    inventory_data = {
        "product_id": 4,
        "quantity": 15
    }
    create_response = client.post("/inventory/", json=inventory_data)
    assert create_response.status_code == 201
    created_inventory = create_response.json()
    inventory_id = created_inventory["id"]

    # Delete the inventory
    response = client.delete(f"/inventory/{inventory_id}")
    assert response.status_code == 204

    # Attempt to retrieve the deleted inventory
    response = client.get(f"/inventory/{inventory_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Inventory item not found"

def test_decrease_inventory():
    # Create an inventory item first
    inventory_data = {
        "product_id": 5,
        "quantity": 100
    }
    create_response = client.post("/inventory/", json=inventory_data)
    assert create_response.status_code == 201

    # Decrease inventory
    decrease_data = {
        "product_id": 5,
        "quantity": 20
    }
    response = client.post("/inventory/decrease/", params=decrease_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Inventory decreased successfully"
    assert data["inventory"]["quantity"] == 80

def test_increase_inventory():
    # Create an inventory item first
    inventory_data = {
        "product_id": 6,
        "quantity": 40
    }
    create_response = client.post("/inventory/", json=inventory_data)
    assert create_response.status_code == 201

    # Increase inventory
    increase_data = {
        "product_id": 6,
        "quantity": 10
    }
    response = client.post("/inventory/increase/", params=increase_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Inventory increased successfully"
    assert data["inventory"]["quantity"] == 50
