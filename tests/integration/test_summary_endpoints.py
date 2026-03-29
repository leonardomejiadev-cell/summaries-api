import pytest
from httpx import AsyncClient

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
SUMMARIES_URL = "/api/v1/summaries/"


async def register_and_login(client: AsyncClient, email: str, password: str) -> str:
    """Registra un usuario y retorna el access token."""
    await client.post(REGISTER_URL, json={"email": email, "password": password})
    response = await client.post(LOGIN_URL, json={"email": email, "password": password})
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_summary_success(client: AsyncClient) -> None:
    token = await register_and_login(client, "create_ok@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        SUMMARIES_URL,
        json={"url": "https://example.com", "title": "Example Title"},
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["url"] == "https://example.com"
    assert data["title"] == "Example Title"
    assert "owner_id" in data


@pytest.mark.asyncio
async def test_create_summary_unauthorized(client: AsyncClient) -> None:
    response = await client.post(
        SUMMARIES_URL,
        json={"url": "https://example.com", "title": "No Auth"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_summaries(client: AsyncClient) -> None:
    token = await register_and_login(client, "list_ok@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    await client.post(
        SUMMARIES_URL,
        json={"url": "https://first.com", "title": "First"},
        headers=headers,
    )
    await client.post(
        SUMMARIES_URL,
        json={"url": "https://second.com", "title": "Second"},
        headers=headers,
    )

    response = await client.get(SUMMARIES_URL, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_summary_success(client: AsyncClient) -> None:
    token = await register_and_login(client, "get_ok@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    create_response = await client.post(
        SUMMARIES_URL,
        json={"url": "https://get-test.com", "title": "Get Test"},
        headers=headers,
    )
    summary_id = create_response.json()["id"]

    response = await client.get(f"{SUMMARIES_URL}{summary_id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == summary_id
    assert data["url"] == "https://get-test.com"
    assert data["title"] == "Get Test"


@pytest.mark.asyncio
async def test_get_summary_not_found(client: AsyncClient) -> None:
    token = await register_and_login(client, "notfound@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(f"{SUMMARIES_URL}999999", headers=headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_summary_wrong_owner(client: AsyncClient) -> None:
    token_a = await register_and_login(client, "owner_a@example.com", "password123")
    token_b = await register_and_login(client, "owner_b@example.com", "password123")

    create_response = await client.post(
        SUMMARIES_URL,
        json={"url": "https://owner-test.com", "title": "Owner Test"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    summary_id = create_response.json()["id"]

    response = await client.get(
        f"{SUMMARIES_URL}{summary_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_summary(client: AsyncClient) -> None:
    token = await register_and_login(client, "update_ok@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    create_response = await client.post(
        SUMMARIES_URL,
        json={"url": "https://update-test.com", "title": "Original Title"},
        headers=headers,
    )
    summary_id = create_response.json()["id"]

    response = await client.put(
        f"{SUMMARIES_URL}{summary_id}",
        json={"title": "Updated Title"},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_delete_summary(client: AsyncClient) -> None:
    token = await register_and_login(client, "delete_ok@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    create_response = await client.post(
        SUMMARIES_URL,
        json={"url": "https://delete-test.com", "title": "To Delete"},
        headers=headers,
    )
    summary_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"{SUMMARIES_URL}{summary_id}", headers=headers
    )
    assert delete_response.status_code == 204

    get_response = await client.get(f"{SUMMARIES_URL}{summary_id}", headers=headers)
    assert get_response.status_code == 404
