from typing import TYPE_CHECKING

from pydantic import BaseModel, EmailStr

if TYPE_CHECKING:
    from app.schemes.roles import SRoleGet


class SUserAddRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role_id: int | None = 1  # Optional, defaults to 1


class SUserAdd(BaseModel):
    name: str
    email: EmailStr
    hashed_password: str
    role_id: int | None = 1


class SUserAuth(BaseModel):
    email: EmailStr
    password: str


class SUserGet(SUserAdd):
    id: int


class SUserPatch(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    hashed_password: str | None = None
    role_id: int | None = None
