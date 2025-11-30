from pydantic import BaseModel, EmailStr

from app.schemes.roles import SRoleGet


class SUserAddRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role_id: int


class SUserAdd(BaseModel):
    name: str
    email: EmailStr
    hashed_password: str
    role_id: int


class SUserAuth(BaseModel):
    email: EmailStr
    password: str


class SUserGet(SUserAdd):
    id: int


class SUserGetWithRels(SUserGet):
    role: "SRoleGet"


class SUserPatch(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    hashed_password: str | None = None
    role_id: int | None = None
