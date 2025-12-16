from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import DBDep, get_current_user
from app.services.friendships import FriendshipService
from app.schemes.friendships import FriendshipResponse
from app.models.users import UserModel

router = APIRouter(prefix="/friendships", tags=["friendships"])


@router.post(
    "/",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
async def add_friend(
    data: dict,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    friend_id = data.get('friend_id')
    service = FriendshipService(db)
    friendship = await service.add_friend(current_user.id, friend_id)
    return {
        "id": friendship.id,
        "user_id": friendship.user_id,
        "friend_id": friendship.friend_id,
        "user": {"id": friendship.user.id, "username": friendship.user.username, "email": friendship.user.email},
        "friend": {"id": friendship.friend.id, "username": friendship.friend.username, "email": friendship.friend.email},
    }


@router.delete(
    "/{friendship_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_friend_by_id(
    friendship_id: int,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    service = FriendshipService(db)
    await service.remove_friend_by_id(friendship_id, current_user.id)
    return None


@router.get(
    "/user/{user_id}",
    response_model=list[dict],
)
async def get_user_friendships(
    user_id: int,
    db: DBDep,
    skip: int = 0,
    limit: int = 100,
):
    service = FriendshipService(db)
    friendships = await service.get_user_friends(user_id, skip, limit)
    return [
        {
            "id": f.id,
            "user_id": f.user_id,
            "friend_id": f.friend_id,
            "user": {"id": f.user.id, "username": f.user.username, "email": f.user.email} if f.user else None,
            "friend": {"id": f.friend.id, "username": f.friend.username, "email": f.friend.email} if f.friend else None,
        }
        for f in friendships
    ]


@router.get(
    "/{friend_id}/old",
    response_model=bool,
)
async def is_friend(
    friend_id: int,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    service = FriendshipService(db)
    return await service.is_friend(current_user.id, friend_id)
