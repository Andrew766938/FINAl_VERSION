from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import DBDep, get_current_user
from app.services.likes import LikeService
from app.schemes.posts import PostResponse
from app.models.users import UserModel

router = APIRouter(prefix="/likes", tags=["likes"])


@router.post(
    "/posts/{post_id}",
    response_model=PostResponse,
    status_code=status.HTTP_200_OK,
)
async def like_post(
    post_id: int,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    service = LikeService(db)
    return await service.like_post(current_user.id, post_id)


@router.delete(
    "/posts/{post_id}",
    response_model=PostResponse,
    status_code=status.HTTP_200_OK,
)
async def unlike_post(
    post_id: int,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    service = LikeService(db)
    return await service.unlike_post(current_user.id, post_id)


@router.get(
    "/posts/{post_id}",
    response_model=list[dict],
)
async def get_post_likes(
    post_id: int,
    db: DBDep,
):
    service = LikeService(db)
    return await service.get_post_likes(post_id)


@router.get(
    "/users/{user_id}",
    response_model=list[dict],
)
async def get_user_likes(
    user_id: int,
    db: DBDep,
):
    service = LikeService(db)
    return await service.get_user_likes(user_id)
