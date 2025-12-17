from typing import TYPE_CHECKING

from pydantic import BaseModel, field_validator

if TYPE_CHECKING:
    from app.schemes.roles import SRoleGet


class SUserAddRequest(BaseModel):
    name: str
    email: str  # Changed from EmailStr to str for flexibility
    password: str
    role_id: int | None = 1  # Optional, defaults to 1

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        # Simple email validation - just check for @ symbol
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v


class SUserAdd(BaseModel):
    name: str
    email: str  # Changed from EmailStr to str
    hashed_password: str
    role_id: int | None = 1

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        # Simple email validation
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v


class SUserAuth(BaseModel):
    email: str  # Changed from EmailStr to str
    password: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        # Simple email validation
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v


class SUserGet(BaseModel):
    id: int
    name: str
    email: str
    hashed_password: str
    role_id: int | None = 1

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        # Simple email validation
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v


class SUserPatch(BaseModel):
    name: str | None = None
    email: str | None = None  # Changed from EmailStr to str
    hashed_password: str | None = None
    role_id: int | None = None

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v
