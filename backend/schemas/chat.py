from pydantic import BaseModel, Field


class ChatAskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    top_k: int = Field(default=4, ge=1, le=10)
    conversation_id: int | None = Field(default=None, gt=0)


class ChatSource(BaseModel):
    source: str
    chunk_index: int
    distance: float


class ChatAskResponse(BaseModel):
    answer: str
    sources: list[ChatSource]
    conversation_id: int
