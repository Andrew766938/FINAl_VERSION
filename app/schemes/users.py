from typing import TYPE_CHECKING

from pydantic import BaseModel, field_validator

if TYPE_CHECKING:
    from app.schemes.roles import SRoleGet


class SUserAddRequest(BaseModel):
    """Схема для регистрации пользователя"""
    name: str
    email: str
    password: str
    role_id: int | None = 1

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Имя: 4-15 символов"""
        if not v or not v.strip():
            raise ValueError('Имя не может быть пустым')
        if len(v) < 4:
            raise ValueError('Имя должно быть минимум 4 символа')
        if len(v) > 15:
            raise ValueError('Имя должно быть максимум 15 символов')
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Email должен содержать @"""
        if not v or not v.strip():
            raise ValueError('Email не может быть пустым')
        if '@' not in v:
            raise ValueError('Email должен содержать @')
        if '.' not in v.split('@')[1]:
            raise ValueError('Email должен содержать домен с точкой')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Пароль: 6-10 символов"""
        if not v:
            raise ValueError('Пароль не может быть пустым')
        if len(v) < 6:
            raise ValueError('Пароль должен быть минимум 6 символов')
        if len(v) > 10:
            raise ValueError('Пароль должен быть максимум 10 символов')
        return v


class SUserAdd(BaseModel):
    """Схема для добавления пользователя в БД"""
    name: str
    email: str
    hashed_password: str
    role_id: int | None = 1

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Имя: 4-15 символов"""
        if not v or not v.strip():
            raise ValueError('Имя не может быть пустым')
        if len(v) < 4:
            raise ValueError('Имя должно быть минимум 4 символа')
        if len(v) > 15:
            raise ValueError('Имя должно быть максимум 15 символов')
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Email должен содержать @"""
        if not v or not v.strip():
            raise ValueError('Email не может быть пустым')
        if '@' not in v:
            raise ValueError('Email должен содержать @')
        if '.' not in v.split('@')[1]:
            raise ValueError('Email должен содержать домен с точкой')
        return v


class SUserAuth(BaseModel):
    """Схема для логина"""
    email: str
    password: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Email должен содержать @"""
        if not v or not v.strip():
            raise ValueError('Email не может быть пустым')
        if '@' not in v:
            raise ValueError('Email должен содержать @')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Пароль не может быть пустым"""
        if not v:
            raise ValueError('Пароль не может быть пустым')
        return v


class SUserGet(BaseModel):
    """Схема для получения информации о пользователе"""
    id: int
    name: str
    email: str
    hashed_password: str
    role_id: int | None = 1

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Email должен содержать @"""
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v


class SUserPatch(BaseModel):
    """Схема для обновления пользователя"""
    name: str | None = None
    email: str | None = None
    hashed_password: str | None = None
    role_id: int | None = None
    is_admin: bool | None = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Имя: 4-15 символов (если указано)"""
        if v is not None:
            if not v.strip():
                raise ValueError('Имя не может быть пустым')
            if len(v) < 4:
                raise ValueError('Имя должно быть минимум 4 символа')
            if len(v) > 15:
                raise ValueError('Имя должно быть максимум 15 символов')
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Email должен быть в правильном формате (если указан)"""
        if v is not None:
            if not v.strip():
                raise ValueError('Email не может быть пустым')
            if '@' not in v:
                raise ValueError('Email должен содержать @')
            if '.' not in v.split('@')[1]:
                raise ValueError('Email должен содержать домен с точкой')
        return v
