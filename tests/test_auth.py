from fastapi import BackgroundTasks
from fastapi.testclient import TestClient
from httpx import ASGITransport
import pytest
from unittest.mock import patch

from main import app


client = TestClient(app)

def test_user_register(override_get_db, user_role):
    with patch.object(BackgroundTasks, "add_task"):
        payload = {
            "email": "tests@gmail.com",
            "username": "testuser",
            "password": "1234111",
        }
        response = client.post(
            "/auth/register",
            json=payload,
        )

    assert response.status_code == 201
    data = response.json()
    print(data)
    assert data["email"] == payload["email"]
    assert data["id"] == user_role.id



def test_user_login(override_get_db):
    response = client.post(
        "/auth/token",
        data={"username": "tests@gmail.com", "password": "1234111"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


    