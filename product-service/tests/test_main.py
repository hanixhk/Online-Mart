from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.main import app
from app.dependencies import get_session
from app.models import Product
from app.schemas import ProductCreate
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
    assert response.json() == {"Service": "Product Service"}

def test_create_product():
    product_data = {
        "name": "Laptop",
        "description": "A high-performance laptop.",
        "price": 1500.00,
        "quantity": 10
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["description"] == product_data["description"]
    assert data["price"] == product_data["price"]
    assert data["quantity"] == product_data["quantity"]
    assert data["is_active"] == True

def test_read_products():
    response = client.get("/products/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_read_product():
    # Create a product first
    product_data = {
        "name": "Smartphone",
        "description": "A latest model smartphone.",
        "price": 800.00,
        "quantity": 20
    }
    create_response = client.post("/products/", json=product_data)
    assert create_response.status_code == 201
    created_product = create_response.json()
    product_id = created_product["id"]

    # Retrieve the created product
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == product_data["name"]

def test_update_product():
    # Create a product first
    product_data = {
        "name": "Tablet",
        "description": "A lightweight tablet.",
        "price": 300.00,
        "quantity": 15
    }
    create_response = client.post("/products/", json=product_data)
    assert create_response.status_code == 201
    created_product = create_response.json()
    product_id = created_product["id"]

    # Update the product's price and quantity
    update_data = {
        "price": 350.00,
        "quantity": 12
    }
    response = client.put(f"/products/{product_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == update_data["price"]
    assert data["quantity"] == update_data["quantity"]

def test_delete_product():
    # Create a product first
    product_data = {
        "name": "Headphones",
        "description": "Noise-cancelling headphones.",
        "price": 200.00,
        "quantity": 25
    }
    create_response = client.post("/products/", json=product_data)
    assert create_response.status_code == 201
    created_product = create_response.json()
    product_id = created_product["id"]

    # Delete the product
    response = client.delete(f"/products/{product_id}")
    assert response.status_code == 204

    # Attempt to retrieve the deleted product
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"
