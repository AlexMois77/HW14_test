import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from main import app
from src.contacts.models import Contact

client = TestClient(app)

def test_create_contact(test_user, auth_headers, override_get_db):
    response = client.post(
        "/contacts/",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "123456789",
            "birthday": "1990-01-01",
            "additional_info": "Some info",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"


def test_get_contact(override_get_db, test_user_contact: Contact, auth_headers):
    response = client.get(f"/contacts/{test_user_contact.id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == test_user_contact.first_name
    assert data["last_name"] == test_user_contact.last_name
