from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.tenant import Document
from app.schemas.document import DocumentCreate

class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_document(self, data: DocumentCreate) -> Document:
        """Tạo document mới."""
        new_document = Document(
            title=data.title,
            content=data.content,
            file_path=data.file_path,
        )
        self.db.add(new_document)
        await self.db.commit()
        await self.db.refresh(new_document)
        return new_document

    async def get_all_documents(self):
        """Lấy tất cả documents."""
        result = await self.db.execute(select(Document))
        return result.scalars().all()

    async def get_document(self, document_id: int) -> Document:
        """Lấy document theo ID."""
        result = await self.db.execute(select(Document).where(Document.id == document_id))
        document = result.scalar_one_or_none()
        if not document:
            raise HTTPException(status_code=404, detail="Document không tồn tại")
        return document
