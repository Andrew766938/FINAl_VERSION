from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import DBDep, get_current_user
from app.services.friendships import FriendshipService
from app.schemes.friendships import FriendshipResponse
from app.models.users import UserModel

router = APIRouter(prefix="/friendships", tags=["friendships"])


@router.get(
    "/",
    response_model=list[dict],
)
async def get_my_friendships(
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    """Get all friendships for current user"""
    service = FriendshipService(db)
    friendships = await service.get_user_friends(current_user.id, 0, 100)
    return [
        {
            "id": f.id,
            "user_id": f.user_id,
            "friend_id": f.friend_id,
        }
        for f in friendships
    ]


@router.post(
    "/{friend_id}",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
async def add_friend(
    friend_id: int,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    """Add a friend (bidirectional)"""
    try:
        service = FriendshipService(db)
        
        # Check if user exists
        friend = await db.users.get_user_by_id(friend_id)
        if not friend:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if already friends
        is_already_friend = await service.is_friend(current_user.id, friend_id)
        if is_already_friend:
            raise HTTPException(status_code=400, detail="Already friends")
        
        # Add friendship both ways
        friendship = await service.add_friend(current_user.id, friend_id)
        await service.add_friend(friend_id, current_user.id)
        await db.commit()
        
        return {
            "id": friendship.id,
            "user_id": friendship.user_id,
            "friend_id": friendship.friend_id,
            "message": "Friend added successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error adding friend: {e}")
        raise HTTPException(status_code=500, detail="Failed to add friend")


@router.delete(
    "/{friendship_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_friend_by_id(
    friendship_id: int,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    """Remove a friendship"""
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
    """Get friendships for a specific user"""
    service = FriendshipService(db)
    friendships = await service.get_user_friends(user_id, skip, limit)
    return [
        {
            "id": f.id,
            "user_id": f.user_id,
            "friend_id": f.friend_id,
        }
        for f in friendships
    ]


@router.get(
    "/check/{friend_id}",
    response_model=bool,
)
async def is_friend(
    friend_id: int,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    """Check if user is a friend"""
    service = FriendshipService(db)
    return await service.is_friend(current_user.id, friend_id)
