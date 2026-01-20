from typing import List

from fastapi import APIRouter, Path

from app.api.deps import TenantDBPath
from app.schemas.document import DocumentCreate, DocumentResponse
from app.services.document_service import DocumentService

router = APIRouter()


@router.post("/{tenant_id}/documents", response_model=DocumentResponse)
async def create_document(
    document_data: DocumentCreate,
    tenant_db: TenantDBPath,
    tenant_id: str = Path(...),
):
    """Tạo document mới trong tenant database."""
    service = DocumentService(tenant_db)
    return await service.create_document(document_data)


@router.get("/{tenant_id}/documents", response_model=List[DocumentResponse])
async def get_documents(
    tenant_db: TenantDBPath,
    tenant_id: str = Path(...),
):
    """Lấy danh sách tất cả documents từ tenant database."""
    service = DocumentService(tenant_db)
    return await service.get_all_documents()


@router.get("/{tenant_id}/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    tenant_db: TenantDBPath,
    tenant_id: str = Path(...),
    document_id: int = Path(...),
):
    """Lấy thông tin document theo ID từ tenant database."""
    service = DocumentService(tenant_db)
    return await service.get_document(document_id)
