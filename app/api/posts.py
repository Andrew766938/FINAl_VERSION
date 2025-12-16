from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import DBDep, get_current_user
from app.services.posts import PostService
from app.services.comments import CommentService
from app.services.likes import LikeService
from app.schemes.posts import PostCreate, PostUpdate, PostResponse
from app.schemes.comments import CommentCreate, CommentResponse
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
    db: DBDep,
    skip: int = 0,
    limit: int = 100,
    user_id: int = Query(None),
):
    service = PostService(db)
    if user_id:
        return await service.get_user_posts(user_id, skip, limit)
    return await service.get_all_posts(skip, limit)


@router.get(
    "/user/{user_id}",
    response_model=list[PostResponse],
)
async def get_user_posts(
    user_id: int,
    db: DBDep,
    skip: int = 0,
    limit: int = 100,
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
    user_id: int = Query(None),
    current_user: UserModel = Depends(get_current_user),
):
    service = PostService(db)
    await service.delete_post(post_id, current_user.id)
    return None


# ===== COMMENTS =====
@router.get(
    "/{post_id}/comments",
    response_model=list[dict],
)
async def get_post_comments(
    post_id: int,
    db: DBDep,
):
    service = CommentService(db)
    comments = await service.get_post_comments(post_id)
    return [
        {
            "id": c.id,
            "post_id": c.post_id,
            "user_id": c.user_id,
            "content": c.content,
            "created_at": c.created_at,
            "author_username": c.user.name if c.user else "Unknown"
        }
        for c in comments
    ]


@router.post(
    "/{post_id}/comments",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    service = CommentService(db)
    comment = await service.create_comment(post_id, comment_data, current_user.id)
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "user_id": comment.user_id,
        "content": comment.content,
        "created_at": comment.created_at,
    }


# ===== LIKES =====
@router.post(
    "/{post_id}/like",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
async def like_post(
    post_id: int,
    like_data: dict,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    service = LikeService(db)
    like = await service.create_like(post_id, current_user.id)
    return {
        "id": like.id,
        "post_id": like.post_id,
        "user_id": like.user_id,
        "created_at": like.created_at,
    }


@router.delete(
    "/{post_id}/like",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def unlike_post(
    post_id: int,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    service = LikeService(db)
    await service.delete_like(post_id, current_user.id)
    return None
