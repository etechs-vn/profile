import pytest
from fastapi import HTTPException
from app.modules.auth.schemas import UserCreate
from app.modules.tenant.service import TenantService


@pytest.mark.asyncio
async def test_create_user(shared_db):
    service = TenantService(shared_db)
    user_data = UserCreate(email="test@example.com", name="Test User")

    user = await service.create_user(user_data)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.name == "Test User"


@pytest.mark.asyncio
async def test_create_user_duplicate_email(shared_db):
    service = TenantService(shared_db)
    user_data = UserCreate(email="dup@example.com", name="Dup User")

    # Create first
    await service.create_user(user_data)

    # Create second
    with pytest.raises(HTTPException) as exc:
        await service.create_user(user_data)

    assert exc.value.status_code == 400
    assert "Email đã tồn tại" in exc.value.detail


@pytest.mark.asyncio
async def test_get_all_users(shared_db):
    service = TenantService(shared_db)
    # Ensure DB is empty or check count increase
    initial_users = await service.get_all_users()
    initial_count = len(initial_users)

    # Create a user
    await service.create_user(UserCreate(email="list@example.com", name="List User"))

    users = await service.get_all_users()
    assert len(users) == initial_count + 1


@pytest.mark.asyncio
async def test_create_multiple_users_null_slug(shared_db):
    service = TenantService(shared_db)
    # Create two users with different emails/names, but both have slug=None (default)
    u1 = await service.create_user(UserCreate(email="u1@example.com", name="U1"))
    u2 = await service.create_user(UserCreate(email="u2@example.com", name="U2"))

    assert u1.id != u2.id
    assert u1.slug is None
    assert u2.slug is None
