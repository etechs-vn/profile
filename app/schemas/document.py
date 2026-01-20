from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    title: str
    content: Optional[str] = None
    file_path: Optional[str] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
