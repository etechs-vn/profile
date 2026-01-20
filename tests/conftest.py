import pytest
import asyncio
import shutil
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.base import SharedBase
from app.db.database_manager import DatabaseManager
from app.modules.auth.models import Tenant
from app.core.graph import GraphManager


# --- Asyncio Fixture ---
@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ... (imports)


@pytest.fixture(scope="function", autouse=True)
def mock_neo4j():
    """Mock Neo4j driver for all tests."""
    # driver.session() is a sync method that returns an async context manager
    mock_session = AsyncMock()

    mock_driver = MagicMock()
    mock_driver.session.return_value.__aenter__.return_value = mock_session
    mock_driver.session.return_value.__aexit__.return_value = None

    # Mock close as async
    mock_driver.close = AsyncMock()

    # Mock the singleton
    original_driver = GraphManager._driver
    GraphManager._driver = mock_driver

    yield mock_driver

    # Restore
    GraphManager._driver = original_driver


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_tenants():
    """Cleanup test tenants directory after session."""
    yield
    tenant_dir = Path("./test_tenants")
    if tenant_dir.exists():
        shutil.rmtree(tenant_dir)


@pytest.fixture(scope="session", autouse=True)
def override_settings():
    """Force settings to use SQLite for testing."""
    settings.postgres_server = None  # Disable Postgres logic
    settings.shared_database_url = "sqlite+aiosqlite:///:memory:"
    # Use in-memory for default tenant strategy in tests
    settings.database_url = "sqlite+aiosqlite:///:memory:"
    # Mock database dir for file-based tenants
    settings.tenant_database_dir = "./test_tenants"


@pytest.fixture(scope="function", autouse=True)
def cleanup_tenant_db_file():
    """Cleanup tenant db file before each test to ensure fresh state."""
    tenant_dir = Path("./test_tenants")
    if tenant_dir.exists():
        shutil.rmtree(tenant_dir)
    yield


# --- Database Manager Fixture ---
@pytest.fixture(scope="function")
async def db_manager() -> AsyncGenerator[DatabaseManager, None]:
    """
    Returns a fresh DatabaseManager instance for each test.
    We do NOT use the global 'db_manager' to avoid shared state.
    """
    manager = DatabaseManager()

    # Setup Shared DB Schema
    engine = manager.get_shared_engine()
    async with engine.begin() as conn:
        await conn.run_sync(SharedBase.metadata.create_all)

    yield manager

    # Teardown
    await manager.dispose_all()


# --- Shared DB Session Fixture ---
@pytest.fixture(scope="function")
async def shared_db(db_manager: DatabaseManager) -> AsyncGenerator[AsyncSession, None]:
    """Returns a session for the shared database."""
    factory = db_manager.get_shared_session_factory()
    async with factory() as session:
        yield session


# --- Populate Data Fixture ---
@pytest.fixture(scope="function")
async def sample_tenant(shared_db: AsyncSession) -> Tenant:
    """Create a sample tenant in the shared database."""
    tenant = Tenant(
        tenant_id="test_tenant_1",
        name="Test Tenant",
        # Default strategy (no specific host)
        db_name="test_tenant_1_db",
    )
    shared_db.add(tenant)
    await shared_db.commit()
    await shared_db.refresh(tenant)
    return tenant


# --- API Client Fixture ---
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import get_shared_db


@pytest.fixture(scope="function")
async def client(shared_db) -> AsyncGenerator[AsyncClient, None]:
    """
    Returns an async client with database dependency overridden.
    """

    # Override dependency to use the test session
    async def override_get_shared_db():
        yield shared_db

    app.dependency_overrides[get_shared_db] = override_get_shared_db

    # Create client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    # Clean up
    app.dependency_overrides.clear()
