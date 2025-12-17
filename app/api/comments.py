from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import DBDep, get_current_user
from app.services.comments import CommentService
from app.schemes.comments import CommentCreate
from app.models.users import UserModel

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/{comment_id}")
async def get_comment(
    comment_id: int,
    db: DBDep,
):
    """Get a specific comment"""
    try:
        service = CommentService(db)
        comment = await service.get_comment(comment_id)
        return {
            "id": comment.id,
            "post_id": comment.post_id,
            "user_id": comment.user_id,
            "content": comment.content,
            "created_at": comment.created_at,
            "author_username": comment.user.name if comment.user else "Unknown"
        }
    except Exception as e:
        print(f"[API] Error getting comment: {e}")
        raise HTTPException(status_code=500, detail="Failed to get comment")


@router.delete("/{comment_id}")
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
        raise HTTPException(status_code=500, detail="Failed to delete comment")
