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
    data = ProfileCreate(nickname="Nguyen Van A", bio="Developer")

    profile = await service.create_profile(sample_user.id, data)

    assert profile.profile_id is not None
    assert profile.user_id == sample_user.id
    assert profile.nickname == "Nguyen Van A"
    assert profile.bio == "Developer"


@pytest.mark.asyncio
async def test_create_profile_duplicate(tenant_db, shared_db, sample_user):
    service = ProfileService(tenant_db, shared_db)
    data = ProfileCreate(nickname="First Profile")

    # Create first time
    await service.create_profile(sample_user.id, data)

    # Create second time
    with pytest.raises(HTTPException) as exc:
        await service.create_profile(sample_user.id, data)

    assert exc.value.status_code == 400
    assert "Profile đã tồn tại" in exc.value.detail


@pytest.mark.asyncio
async def test_update_profile(tenant_db, shared_db, sample_user):
    # Setup
    service = ProfileService(tenant_db, shared_db)
    create_data = ProfileCreate(nickname="Old Name")
    profile = await service.create_profile(sample_user.id, create_data)

    # Update
    update_data = ProfileUpdate(nickname="New Name", bio="New Bio")
    updated_profile = await service.update_profile(profile.profile_id, update_data)

    assert updated_profile.nickname == "New Name"
    assert updated_profile.bio == "New Bio"

    # Verify persistence
    db_profile = await service.get_profile_by_id(profile.profile_id)
    assert db_profile.nickname == "New Name"


@pytest.mark.asyncio
async def test_get_profile_by_user_id(tenant_db, shared_db, sample_user):
    service = ProfileService(tenant_db, shared_db)
    create_data = ProfileCreate(nickname="Test User")
    await service.create_profile(sample_user.id, create_data)

    profile = await service.get_profile_by_user_id(sample_user.id)

    assert profile.nickname == "Test User"


@pytest.mark.asyncio
async def test_get_profile_by_user_id_not_found(tenant_db, shared_db):
    service = ProfileService(tenant_db, shared_db)

    with pytest.raises(HTTPException) as exc:
        await service.get_profile_by_user_id(9999)

    assert exc.value.status_code == 404
    assert "Profile chưa được tạo cho user này" in exc.value.detail
