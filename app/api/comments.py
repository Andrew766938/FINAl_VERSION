from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import DBDep, get_current_user
from app.services.comments import CommentService
from app.schemes.comments import CommentCreate, CommentUpdate, CommentResponse
from app.models.users import UserModel

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post(
    "/posts/{post_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    service = CommentService(db)
    return await service.create_comment(comment_data, current_user.id, post_id)


@router.get(
    "/{comment_id}",
    response_model=CommentResponse,
)
async def get_comment(
    comment_id: int,
    db: DBDep,
):
    service = CommentService(db)
    return await service.get_comment(comment_id)


@router.get(
    "/posts/{post_id}",
    response_model=list[CommentResponse],
)
async def get_post_comments(
    post_id: int,
    skip: int = 0,
    limit: int = 20,
    db: DBDep,
):
    service = CommentService(db)
    return await service.get_post_comments(post_id, skip, limit)


@router.put(
    "/{comment_id}",
    response_model=CommentResponse,
)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    service = CommentService(db)
    return await service.update_comment(comment_id, comment_data, current_user.id)


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    comment_id: int,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    service = CommentService(db)
    await service.delete_comment(comment_id, current_user.id)
    return None
