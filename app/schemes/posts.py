from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


class PostCreate(BaseModel):
    """Схема для создания поста"""
    title: str
    content: str

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Название: 1-200 символов"""
        if not v or not v.strip():
            raise ValueError('Название не может быть пустым')
        if len(v) > 200:
            raise ValueError('Название не должно превышать 200 символов')
        return v

    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        """Содержание: 1-5000 символов"""
        if not v or not v.strip():
            raise ValueError('Содержание не может быть пустым')
        if len(v) > 5000:
            raise ValueError('Содержание не должно превышать 5000 символов')
        return v


class PostUpdate(BaseModel):
    """Схема для обновления поста"""
    title: Optional[str] = None
    content: Optional[str] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Название: 1-200 символов (если указано)"""
        if v is not None:
            if not v.strip():
                raise ValueError('Название не может быть пустым')
            if len(v) > 200:
                raise ValueError('Название не должно превышать 200 символов')
        return v

    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        """Содержание: 1-5000 символов (если указано)"""
        if v is not None:
            if not v.strip():
                raise ValueError('Содержание не может быть пустым')
            if len(v) > 5000:
                raise ValueError('Содержание не должно превышать 5000 символов')
        return v


class PostResponse(BaseModel):
    """Ответ с информацией о посте"""
    id: int
    title: str
    content: str
    user_id: int
    author_name: Optional[str] = None
    author_email: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    likes_count: int = 0
    
    class Config:
        from_attributes = True


class PostDetailResponse(PostResponse):
    """Детальный ответ с информацией о посте"""
    pass
