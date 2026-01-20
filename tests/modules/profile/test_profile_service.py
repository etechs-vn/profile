import pytest
from fastapi import HTTPException

from app.modules.auth.models import User
from app.modules.profile.schemas import ProfileCreate, ProfileUpdate
from app.modules.profile.service import ProfileService


@pytest.fixture
async def sample_user(shared_db):
    """Create a sample user in shared DB."""
    user = User(email="test@example.com", name="Test User")
    shared_db.add(user)
    await shared_db.commit()
    await shared_db.refresh(user)
    return user


@pytest.fixture
async def tenant_db(db_manager, sample_tenant):
    """Get a tenant DB session with tables created."""
    # Ensure schema exists
    await db_manager.ensure_tenant_tables(sample_tenant.tenant_id)

    # Get session
    factory = await db_manager.get_tenant_session_factory(sample_tenant.tenant_id)
    async with factory() as session:
        yield session


@pytest.mark.asyncio
async def test_create_profile(tenant_db, shared_db, sample_user):
    service = ProfileService(tenant_db, shared_db)
    data = ProfileCreate(
        user_id=sample_user.id, full_name="Nguyen Van A", bio="Developer"
    )

    profile = await service.create_profile(data)

    assert profile.id is not None
    assert profile.user_id == sample_user.id
    assert profile.full_name == "Nguyen Van A"
    assert profile.bio == "Developer"
    assert profile.role == "unspecified"


@pytest.mark.asyncio
async def test_create_profile_user_not_found(tenant_db, shared_db):
    service = ProfileService(tenant_db, shared_db)
    data = ProfileCreate(
        user_id=9999,  # Non-existent ID
        full_name="Ghost User",
    )

    with pytest.raises(HTTPException) as exc:
        await service.create_profile(data)

    assert exc.value.status_code == 404
    assert "User không tồn tại" in exc.value.detail


@pytest.mark.asyncio
async def test_create_profile_duplicate(tenant_db, shared_db, sample_user):
    service = ProfileService(tenant_db, shared_db)
    data = ProfileCreate(user_id=sample_user.id, full_name="First Profile")

    # Create first time
    await service.create_profile(data)

    # Create second time
    with pytest.raises(HTTPException) as exc:
        await service.create_profile(data)

    assert exc.value.status_code == 400
    assert "Profile đã tồn tại" in exc.value.detail


@pytest.mark.asyncio
async def test_update_general_info(tenant_db, shared_db, sample_user):
    # Setup
    service = ProfileService(tenant_db, shared_db)
    create_data = ProfileCreate(user_id=sample_user.id, full_name="Old Name")
    await service.create_profile(create_data)

    # Update
    update_data = ProfileUpdate(full_name="New Name", bio="New Bio")
    updated_profile = await service.update_general_info(sample_user.id, update_data)

    assert updated_profile.full_name == "New Name"
    assert updated_profile.bio == "New Bio"

    # Verify persistence
    db_profile = await service.get_profile_by_id(updated_profile.id)
    assert db_profile.full_name == "New Name"
