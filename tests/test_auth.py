from fastapi import BackgroundTasks
from fastapi.testclient import TestClient
from httpx import ASGITransport
import pytest
from unittest.mock import patch

from main import app


client = TestClient(app)

def test_user_register(override_get_db, user_role, faker):
    with patch.object(BackgroundTasks, "add_task"):
        payload = {
            "email": faker.email(),
            "username": faker.user_name(),
            "password": faker.password(),
        }
        response = client.post(
            "/auth/register",
            json=payload,
        )

    assert response.status_code == 201  # Убедитесь, что статус код соответствует ожидаемому
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["id"] == user_role.id



def test_user_login(override_get_db, test_user, user_password):
    response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": user_password},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data