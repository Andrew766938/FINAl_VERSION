"""Friends API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func

from app.api.dependencies import DBDep, get_current_user
from app.models.users import UserModel
from app.models.friendships import FriendshipModel

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/users/{user_id}/friend", status_code=status.HTTP_201_CREATED)
async def add_friend(
    user_id: int,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
) -> dict:
    """
    Add a user as a friend
    """
    try:
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot add yourself as a friend"
            )
        
        # Check if user exists
        result = await db.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        friend = result.scalars().first()
        if not friend:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if already friends
        result = await db.session.execute(
            select(FriendshipModel).where(
                (FriendshipModel.user_id == current_user.id) &
                (FriendshipModel.friend_id == user_id)
            )
        )
        existing = result.scalars().first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Already friends with this user"
            )
        
        # Create friendship
        friendship = FriendshipModel(
            user_id=current_user.id,
            friend_id=user_id
        )
        db.session.add(friendship)
        await db.session.commit()
        
        return {
            "status": "OK",
            "message": f"Added {friend.name} as friend",
            "friend": {
                "id": friend.id,
                "name": friend.name,
                "email": friend.email,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error adding friend: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add friend"
        )


@router.delete("/users/{user_id}/friend", status_code=status.HTTP_204_NO_CONTENT)
async def remove_friend(
    user_id: int,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Remove a user from friends
    """
    try:
        result = await db.session.execute(
            select(FriendshipModel).where(
                (FriendshipModel.user_id == current_user.id) &
                (FriendshipModel.friend_id == user_id)
            )
        )
        friendship = result.scalars().first()
        if not friendship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not friends with this user"
            )
        
        # Delete friendship
        await db.session.delete(friendship)
        await db.session.commit()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error removing friend: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove friend"
        )


@router.get("/friends", response_model=list[dict])
async def get_my_friends(
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
) -> list:
    """
    Get all my friends
    """
    try:
        result = await db.session.execute(
            select(FriendshipModel).where(
                FriendshipModel.user_id == current_user.id
            )
        )
        friendships = result.scalars().all()
        
        friends = []
        for friendship in friendships:
            # Get friend details
            friend_result = await db.session.execute(
                select(UserModel).where(UserModel.id == friendship.friend_id)
            )
            friend = friend_result.scalars().first()
            if friend:
                friends.append({
                    "id": friend.id,
                    "name": friend.name,
                    "email": friend.email,
                    "added_at": friendship.created_at.isoformat(),
                })
        
        return friends
    except Exception as e:
        print(f"[API] Error getting friends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get friends"
        )


@router.get("/users/{user_id}", response_model=dict)
async def get_user_profile(
    user_id: int,
    db: DBDep,
):
    """
    Get user profile with statistics
    FIXED: Correctly count posts, friends, and likes using func.count()
    """
    try:
        result = await db.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Count posts - FIXED: Use func.count() for accurate count
        from app.models.posts import PostModel
        posts_result = await db.session.execute(
            select(func.count(PostModel.id)).where(PostModel.user_id == user_id)
        )
        posts_count = posts_result.scalar() or 0
        
        # Count friends - FIXED: Use func.count() for accurate count
        friends_result = await db.session.execute(
            select(func.count(FriendshipModel.id)).where(FriendshipModel.user_id == user_id)
        )
        friends_count = friends_result.scalar() or 0
        
        # Count likes - FIXED: Use func.count() for accurate count
        from app.models.likes import LikeModel
        likes_result = await db.session.execute(
            select(func.count(LikeModel.id)).where(LikeModel.user_id == user_id)
        )
        likes_count = likes_result.scalar() or 0
        
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_admin": user.is_admin or False,
            "posts_count": posts_count,
            "friends_count": friends_count,
            "likes_count": likes_count,
            "joined_at": user.created_at.isoformat() if hasattr(user, 'created_at') else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error getting user profile: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )
