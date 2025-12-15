from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_session
from app.api.dependencies import get_current_user
from app.services.posts import PostService
from app.schemes.posts import PostCreate, PostUpdate, PostResponse
from app.models.users import UserModel

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    session: AsyncSession = Depends(get_session),
    current_user: UserModel = Depends(get_current_user)
):
    service = PostService(session)
    return await service.create_post(post_data, current_user.id)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = PostService(session)
    return await service.get_post(post_id)


@router.get("/", response_model=list[PostResponse])
async def get_all_posts(
    skip: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_session)
):
    service = PostService(session)
    return await service.get_all_posts(skip, limit)


@router.get("/user/{user_id}", response_model=list[PostResponse])
async def get_user_posts(
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_session)
):
    service = PostService(session)
    return await service.get_user_posts(user_id, skip, limit)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: UserModel = Depends(get_current_user)
):
    service = PostService(session)
    return await service.update_post(post_id, post_data, current_user.id)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserModel = Depends(get_current_user)
):
    service = PostService(session)
    await service.delete_post(post_id, current_user.id)
    return None
