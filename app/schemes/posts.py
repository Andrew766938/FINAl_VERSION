from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PostCreate(BaseModel):
    title: str
    content: str


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    likes_count: int
    
    class Config:
        from_attributes = True


class PostDetailResponse(PostResponse):
    pass
