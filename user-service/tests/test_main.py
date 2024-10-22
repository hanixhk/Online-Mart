from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.main import app
from app.dependencies import get_session
from app.models import User
from app.schemas import UserCreate
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
    assert response.json() == {"Service": "User Service"}

def test_create_user():
    user_data = {
        "username": "johndoe",
        "email": "johndoe@example.com",
        "password": "securepassword",
        "full_name": "John Doe"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert data["is_active"] == True

def test_read_users():
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_read_user():
    # Create a user first
    user_data = {
        "username": "janedoe",
        "email": "janedoe@example.com",
        "password": "anothersecurepassword",
        "full_name": "Jane Doe"
    }
    create_response = client.post("/users/", json=user_data)
    assert create_response.status_code == 201
    created_user = create_response.json()
    user_id = created_user["id"]

    # Retrieve the created user
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == user_data["username"]

def test_update_user():
    # Create a user first
    user_data = {
        "username": "marksmith",
        "email": "marksmith@example.com",
        "password": "yetanotherpassword",
        "full_name": "Mark Smith"
    }
    create_response = client.post("/users/", json=user_data)
    assert create_response.status_code == 201
    created_user = create_response.json()
    user_id = created_user["id"]

    # Update the user's email and status
    update_data = {
        "email": "mark.smith@newdomain.com",
        "is_active": False
    }
    response = client.put(f"/users/{user_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == update_data["email"]
    assert data["is_active"] == update_data["is_active"]

def test_authenticate_user():
    # Create a user first
    user_data = {
        "username": "authuser",
        "email": "authuser@example.com",
        "password": "authpassword",
        "full_name": "Auth User"
    }
    create_response = client.post("/users/", json=user_data)
    assert create_response.status_code == 201

    # Attempt to authenticate with correct credentials
    response = client.post("/auth/", data={"username": "authuser", "password": "authpassword"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "authuser"

    # Attempt to authenticate with incorrect credentials
    response = client.post("/auth/", data={"username": "authuser", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
