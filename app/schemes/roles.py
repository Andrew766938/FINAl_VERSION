from pydantic import BaseModel


class SRolesAdd(BaseModel):
    name: str


class SRoleGet(SRolesAdd):
    id: int


class SRoleGetWithRels(SRoleGet):
    users: list["SUserGet"]
