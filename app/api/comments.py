from fastapi import APIRouter, Depends, status, HTTPException
import traceback

from app.api.dependencies import DBDep, get_current_user
from app.services.comments import CommentService
from app.schemes.comments import CommentCreate
from app.models.users import UserModel

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get(
    "/{comment_id}",
    response_model=dict,
)
async def get_comment(
    comment_id: int,
    db: DBDep,
):
    """Get a specific comment by ID"""
    try:
        service = CommentService(db)
        comment = await service.get_comment(comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        return {
            "id": comment.id,
            "post_id": comment.post_id,
            "user_id": comment.user_id,
            "content": comment.content,
            "created_at": comment.created_at,
            "author_username": comment.user.name if comment.user else "Unknown"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error getting comment: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get comment"
        )


@router.put(
    "/{comment_id}",
    response_model=dict,
)
async def update_comment(
    comment_id: int,
    comment_data: CommentCreate,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    """Update a comment"""
    try:
        service = CommentService(db)
        comment = await service.update_comment(comment_id, comment_data, current_user.id)
        return {
            "id": comment.id,
            "post_id": comment.post_id,
            "user_id": comment.user_id,
            "content": comment.content,
            "created_at": comment.created_at,
        }
    except Exception as e:
        print(f"[API] Error updating comment: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update comment"
        )


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    comment_id: int,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    """Delete a comment"""
    try:
        service = CommentService(db)
        await service.delete_comment(comment_id, current_user.id)
        return None
    except Exception as e:
        print(f"[API] Error deleting comment: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete comment"
        )
