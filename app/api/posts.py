from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import DBDep, get_current_user
from app.services.posts import PostService
from app.schemes.posts import PostCreate, PostUpdate, PostResponse
from app.models.users import UserModel

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    post_data: PostCreate,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    service = PostService(db)
    return await service.create_post(post_data, current_user.id)


@router.get(
    "/{post_id}",
    response_model=PostResponse,
)
async def get_post(
    post_id: int,
    db: DBDep,
):
    service = PostService(db)
    return await service.get_post(post_id)


@router.get(
    "/",
    response_model=list[PostResponse],
)
async def get_all_posts(
    skip: int = 0,
    limit: int = 10,
    db: DBDep,
):
    service = PostService(db)
    return await service.get_all_posts(skip, limit)


@router.get(
    "/user/{user_id}",
    response_model=list[PostResponse],
)
async def get_user_posts(
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    db: DBDep,
):
    service = PostService(db)
    return await service.get_user_posts(user_id, skip, limit)


@router.put(
    "/{post_id}",
    response_model=PostResponse,
)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    service = PostService(db)
    return await service.update_post(post_id, post_data, current_user.id)


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_post(
    post_id: int,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    service = PostService(db)
    await service.delete_post(post_id, current_user.id)
    return None
