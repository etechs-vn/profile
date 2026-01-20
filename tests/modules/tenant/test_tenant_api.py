import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_user_api(client: AsyncClient):
    payload = {
        "email": "api@example.com",
        "name": "API User",
        "full_name": "Full API User",
        "slug": "api-user-slug",
        "avatar_url": "http://example.com/avatar.png",
    }
    response = await client.post("/shared/users", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "api@example.com"
    assert data["name"] == "API User"
    assert data["full_name"] == "Full API User"
    assert data["slug"] == "api-user-slug"
    assert data["avatar_url"] == "http://example.com/avatar.png"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_user_duplicate_email_api(client: AsyncClient):
    payload = {"email": "dup_api@example.com", "name": "Dup User"}

    # First creation
    resp1 = await client.post("/shared/users", json=payload)
    assert resp1.status_code == 200

    # Second creation (Duplicate)
    resp2 = await client.post("/shared/users", json=payload)
    assert resp2.status_code == 400
    assert "Email đã tồn tại" in resp2.json()["detail"]


@pytest.mark.asyncio
async def test_get_users_api(client: AsyncClient):
    # Ensure clean state or just check structural correctness
    # Create one via API first
    await client.post(
        "/shared/users", json={"email": "get@example.com", "name": "Get User"}
    )

    response = await client.get("/shared/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Check that new fields are present in list response even if None
    first_user = data[0]
    assert "full_name" in first_user
    assert "slug" in first_user
    assert "avatar_url" in first_user


@pytest.mark.asyncio
async def test_get_user_by_id_api(client: AsyncClient):
    # Create user
    create_resp = await client.post(
        "/shared/users",
        json={"email": "id_test@example.com", "name": "ID Test", "slug": "id-test"},
    )
    user_id = create_resp.json()["id"]

    # Get by ID
    get_resp = await client.get(f"/shared/users/{user_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == user_id
    assert data["email"] == "id_test@example.com"
    assert data["slug"] == "id-test"


@pytest.mark.asyncio
async def test_get_user_not_found_api(client: AsyncClient):
    get_resp = await client.get("/shared/users/999999")
    assert get_resp.status_code == 404
    assert "User không tồn tại" in get_resp.json()["detail"]
