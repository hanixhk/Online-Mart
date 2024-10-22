from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from unittest.mock import patch
from app.main import app
from app.dependencies import get_session
from app.models import Notification
from app.schemas import NotificationCreate, NotificationUpdate
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

@patch('app.notification_providers.send_email', return_value=True)
@patch('app.notification_providers.send_sms', return_value=True)
def test_create_notification(mock_sms, mock_email):
    notification_data = {
        "user_id": 1,
        "notification_type": "email",
        "message": "Your order has been placed successfully."
    }
    response = client.post("/notifications/", json=notification_data)
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == notification_data["user_id"]
    assert data["notification_type"] == notification_data["notification_type"]
    assert data["message"] == notification_data["message"]
    assert data["status"] == "sent"

def test_read_notifications():
    response = client.get("/notifications/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_read_notification():
    # Create a notification first
    notification_data = {
        "user_id": 2,
        "notification_type": "sms",
        "message": "Your payment was successful."
    }
    with patch('app.notification_providers.send_email', return_value=True), \
         patch('app.notification_providers.send_sms', return_value=True):
        create_response = client.post("/notifications/", json=notification_data)
    assert create_response.status_code == 201
    created_notification = create_response.json()
    notification_id = created_notification["id"]

    # Retrieve the created notification
    response = client.get(f"/notifications/{notification_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == notification_id
    assert data["user_id"] == notification_data["user_id"]

@patch('app.notification_providers.send_email', return_value=True)
@patch('app.notification_providers.send_sms', return_value=True)
def test_update_notification(mock_sms, mock_email):
    # Create a notification first
    notification_data = {
        "user_id": 3,
        "notification_type": "email",
        "message": "Your shipment has been dispatched."
    }
    create_response = client.post("/notifications/", json=notification_data)
    assert create_response.status_code == 201
    created_notification = create_response.json()
    notification_id = created_notification["id"]

    # Update the notification's status
    update_data = {
        "status": "sent",
        "message": "Your shipment is on the way."
    }
    response = client.put(f"/notifications/{notification_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == update_data["status"]
    assert data["message"] == update_data["message"]

def test_delete_notification():
    # Create a notification first
    notification_data = {
        "user_id": 4,
        "notification_type": "sms",
        "message": "Your order has been delivered."
    }
    with patch('app.notification_providers.send_email', return_value=True), \
         patch('app.notification_providers.send_sms', return_value=True):
        create_response = client.post("/notifications/", json=notification_data)
    assert create_response.status_code == 201
    created_notification = create_response.json()
    notification_id = created_notification["id"]

    # Delete the notification
    response = client.delete(f"/notifications/{notification_id}")
    assert response.status_code == 204

    # Attempt to retrieve the deleted notification
    response = client.get(f"/notifications/{notification_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Notification not found"
