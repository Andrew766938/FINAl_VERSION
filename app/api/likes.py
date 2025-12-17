from fastapi import APIRouter, Depends, status, HTTPException
import traceback

from app.api.dependencies import DBDep, get_current_user
from app.services.likes import LikeService
from app.models.users import UserModel

router = APIRouter(prefix="/likes", tags=["likes"])


@router.get(
    "/{like_id}",
    response_model=dict,
)
async def get_like(
    like_id: int,
    db: DBDep,
):
    """Get a specific like by ID"""
    try:
        service = LikeService(db)
        like = await service.get_like(like_id)
        if not like:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Like not found"
            )
        return {
            "id": like.id,
            "post_id": like.post_id,
            "user_id": like.user_id,
            "username": like.user.name if like.user else "Unknown",
            "created_at": like.created_at,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error getting like: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get like"
        )


@router.get(
    "/user/{user_id}",
    response_model=list[dict],
)
async def get_user_likes(
    user_id: int,
    db: DBDep,
):
    """Get all likes by a user"""
    try:
        service = LikeService(db)
        likes = await service.get_user_likes(user_id)
        return [
            {
                "id": like.id,
                "post_id": like.post_id,
                "user_id": like.user_id,
                "created_at": like.created_at,
            }
            for like in likes
        ]
    except Exception as e:
        print(f"[API] Error getting user likes: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user likes"
        )


@router.delete(
    "/{like_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_like(
    like_id: int,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    """Delete a like"""
    try:
        service = LikeService(db)
        await service.delete_like_by_id(like_id, current_user.id)
        return None
    except Exception as e:
        print(f"[API] Error deleting like: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete like"
        )
