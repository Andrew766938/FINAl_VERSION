from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import DBDep, get_current_user
from app.services.friendships import FriendshipService
from app.schemes.friendships import FriendshipResponse
from app.models.users import UserModel

router = APIRouter(prefix="/friends", tags=["friends"])


@router.post(
    "/{friend_id}",
    response_model=FriendshipResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_friend(
    friend_id: int,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    service = FriendshipService(db)
    return await service.add_friend(current_user.id, friend_id)


@router.delete(
    "/{friend_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_friend(
    friend_id: int,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    service = FriendshipService(db)
    await service.remove_friend(current_user.id, friend_id)
    return None


@router.get(
    "/me",
    response_model=list[FriendshipResponse],
)
async def my_friends(
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20,
):
    service = FriendshipService(db)
    return await service.get_user_friends(current_user.id, skip, limit)


@router.get(
    "/followers",
    response_model=list[FriendshipResponse],
)
async def my_followers(
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20,
):
    service = FriendshipService(db)
    return await service.get_user_followers(current_user.id, skip, limit)


@router.get(
    "/{friend_id}/is-friend",
    response_model=bool,
)
async def is_friend(
    friend_id: int,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    service = FriendshipService(db)
    return await service.is_friend(current_user.id, friend_id)
