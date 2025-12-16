from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.schemes.users import SUserGet


class SRoleAdd(BaseModel):
    name: str
    description: str | None = None


class SRoleGet(SRoleAdd):
    id: int
