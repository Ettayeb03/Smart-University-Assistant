
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


DocumentStatus = Literal[
    "pending",
    "processing",
    "processed",
    "failed",
]


class DocumentResponse(BaseModel):
    id: int
    title: str
    filename: str
    file_type: str
    file_size: int
    status: DocumentStatus
    uploaded_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)

class DocumentCreateAdmin(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class DocumentUpdateAdmin(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)