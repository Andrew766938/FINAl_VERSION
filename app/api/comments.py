from fastapi import APIRouter, Depends, status

from app.api.dependencies import DBDep, get_current_user
from app.models.users import UserModel

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/")
async def get_all_comments(db: DBDep):
    return {"message": "Comments endpoint"}
