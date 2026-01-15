from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Updated import to v1 api
from app.api.v1.api import api_router
from app.core.config import settings
from app.db import SharedBase, db_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager để quản lý database engine lifecycle.
    - Startup: Tạo tables tự động cho shared database
    - Shutdown: Đóng và dispose tất cả engines (shared + tenant databases)
    """
    # Startup - Tạo tables cho shared database (chỉ các model kế thừa SharedBase)
    # Tenant databases sẽ tự động tạo schema riêng khi được sử dụng lần đầu
    shared_engine = db_manager.get_shared_engine()
    async with shared_engine.begin() as conn:
        await conn.run_sync(SharedBase.metadata.create_all)

    yield

    # Shutdown - dispose tất cả database engines (shared + tenant)
    await db_manager.dispose_all()


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    description="""
    Profile API với kiến trúc Multi-Tenant:
    - Shared Database: Database chung chứa thông tin cơ bản
    - Tenant Databases: Database riêng cho từng cá thể (SQLite)
    
    ## Endpoints:
    - `/shared/*`: Routes cho shared database
    - `/tenants/*`: Routes cho tenant databases
    """,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hoặc cấu hình domain cụ thể tại đây
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router)


@app.get("/")
def read_root():
    return {
        "message": settings.app_name,
        "docs": "/docs",
        "shared_database": "/shared",
        "tenant_databases": "/tenants",
    }