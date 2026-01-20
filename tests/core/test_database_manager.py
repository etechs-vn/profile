import pytest
from sqlalchemy import text
from app.db.database_manager import DatabaseManager
from app.modules.auth.models import Tenant


@pytest.mark.asyncio
async def test_shared_engine_initialization(db_manager: DatabaseManager):
    """Test that shared engine is initialized correctly."""
    engine = db_manager.get_shared_engine()
    assert engine is not None

    # Check connection
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_get_tenant_config_not_found(db_manager: DatabaseManager):
    """Test getting config for non-existent tenant."""
    # Access private provider for testing
    config = await db_manager.config_provider.get_config("non_existent")
    assert config is None


@pytest.mark.asyncio
async def test_get_tenant_engine_default(
    db_manager: DatabaseManager, sample_tenant: Tenant
):
    """Test getting engine for a tenant using default strategy (SQLite/Local)."""
    # 1. First call - should create new engine
    engine1 = await db_manager.get_tenant_engine(sample_tenant.tenant_id)
    assert engine1 is not None
    assert sample_tenant.tenant_id in db_manager._tenant_engines

    # 2. Verify connection works
    async with engine1.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1

    # 3. Second call - should return cached engine
    engine2 = await db_manager.get_tenant_engine(sample_tenant.tenant_id)
    assert engine1 is engine2  # Same instance


@pytest.mark.asyncio
async def test_ensure_tenant_tables(db_manager: DatabaseManager, sample_tenant: Tenant):
    """Test table creation for tenant."""
    await db_manager.ensure_tenant_tables(sample_tenant.tenant_id)

    assert sample_tenant.tenant_id in db_manager._tenant_tables_created

    engine = await db_manager.get_tenant_engine(sample_tenant.tenant_id)

    # Verify profiles table exists
    async with engine.connect() as conn:
        # Check SQLite system tables
        result = await conn.execute(
            text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='profiles'"
            )
        )
        table_name = result.scalar()
        assert table_name == "profiles", "Table 'profiles' was not created"


@pytest.mark.asyncio
async def test_lru_cache_eviction(db_manager: DatabaseManager):
    """Test that oldest connections are evicted when limit is reached."""
    # Reduce limit for testing
    setattr(db_manager, "MAX_TENANT_CONNECTIONS", 2)

    # Create 3 connections
    await db_manager.get_tenant_engine("t1")
    await db_manager.get_tenant_engine("t2")

    assert len(db_manager._tenant_engines) == 2
    assert "t1" in db_manager._tenant_engines
    assert "t2" in db_manager._tenant_engines

    # Access t1 again to make it "recently used"
    await db_manager.get_tenant_engine("t1")

    # Create t3 -> should evict t2 (LRU) because t1 was just used
    await db_manager.get_tenant_engine("t3")

    assert len(db_manager._tenant_engines) == 2
    assert "t1" in db_manager._tenant_engines
    assert "t3" in db_manager._tenant_engines
    assert "t2" not in db_manager._tenant_engines
