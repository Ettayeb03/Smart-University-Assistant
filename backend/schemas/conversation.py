from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    title: str = Field(default="Nouvelle conversation", min_length=1, max_length=200)


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    sources: list[dict] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
