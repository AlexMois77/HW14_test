import pytest
from fastapi.testclient import TestClient
from main import app
from src.contacts.models import Contact

client = TestClient(app)


def test_create_contact(override_get_db, auth_headers, test_user):
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
    assert response.status_code == 201
    data = response.json()
    assert data["owner_id"] == test_user.id
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["email"] == "john.doe@example.com"
    assert data["phone_number"] == "123456789"
    assert data["birthday"] == "1990-01-01"
    assert data["additional_info"] == "Some info"

def test_get_contact(override_get_db, test_user_contact: Contact, auth_headers):
    response = client.get(f"/contacts/{test_user_contact.id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user_contact.id
    assert data["first_name"] == test_user_contact.first_name
    assert data["last_name"] == test_user_contact.last_name
    assert data["email"] == test_user_contact.email
    assert data["phone_number"] == test_user_contact.phone_number
    assert data["birthday"] == test_user_contact.birthday
    assert data["additional_info"] == test_user_contact.additional_info
