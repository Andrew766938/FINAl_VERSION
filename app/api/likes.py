from fastapi import APIRouter, Depends, status

from app.api.dependencies import DBDep, get_current_user
from app.models.users import UserModel

router = APIRouter(prefix="/likes", tags=["likes"])


@router.get("/")
async def get_all_likes(db: DBDep):
    return {"message": "Likes endpoint"}
