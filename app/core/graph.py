from neo4j import AsyncGraphDatabase, AsyncDriver
from app.core.config import settings


class GraphManager:
    _driver: AsyncDriver | None = None

    @classmethod
    def get_driver(cls) -> AsyncDriver:
        if cls._driver is None:
            cls._driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
            )
        return cls._driver

    @classmethod
    async def close(cls):
        if cls._driver:
            await cls._driver.close()
            cls._driver = None


async def get_neo4j_driver() -> AsyncDriver:
    """Dependency injection helper"""
    return GraphManager.get_driver()
