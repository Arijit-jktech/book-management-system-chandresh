import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_signup_and_login(client: AsyncClient):
    # Signup
    user_data = {"email": "test@example.com", "password": "password123"}
    response = await client.post("/api/v1/auth/signup", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data

    # Login
    login_data = {"username": "test@example.com", "password": "password123"}
    response = await client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
