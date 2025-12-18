from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


class CommentCreate(BaseModel):
    """Схема для создания комментария"""
    content: str

    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        """Комментарий: 1-1000 символов"""
        if not v or not v.strip():
            raise ValueError('Комментарий не может быть пустым')
        if len(v) > 1000:
            raise ValueError('Комментарий не должен превышать 1000 символов')
        return v


class CommentUpdate(BaseModel):
    """Схема для обновления комментария"""
    content: str

    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        """Комментарий: 1-1000 символов"""
        if not v or not v.strip():
            raise ValueError('Комментарий не может быть пустым')
        if len(v) > 1000:
            raise ValueError('Комментарий не должен превышать 1000 символов')
        return v


class CommentResponse(BaseModel):
    """Ответ с информацией о комментарии"""
    id: int
    content: str
    user_id: int
    post_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
