import pytest
from httpx import AsyncClient

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient) -> None:
    payload = {"email": "register_ok@example.com", "password": "validpass123"}
    response = await client.post(REGISTER_URL, json=payload)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == payload["email"]
    assert data["is_active"] is True
    assert "password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    payload = {"email": "duplicate@example.com", "password": "secret123"}
    first = await client.post(REGISTER_URL, json=payload)
    assert first.status_code == 201

    second = await client.post(REGISTER_URL, json=payload)
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    email = "login_ok@example.com"
    password = "mypassword456"
    await client.post(REGISTER_URL, json={"email": email, "password": password})

    response = await client.post(LOGIN_URL, json={"email": email, "password": password})

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data and data["access_token"]
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient) -> None:
    email = "wrong_pass@example.com"
    await client.post(
        REGISTER_URL,
        json={"email": email, "password": "correctpassword"},
    )

    response = await client.post(
        LOGIN_URL,
        json={"email": email, "password": "wrongpassword"},
    )

    assert response.status_code == 401
