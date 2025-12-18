from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import traceback

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
    """Create a new post"""
    try:
        print(f"\n[API] Create post endpoint called by user {current_user.id}")
        print(f"[API] Post data: title='{post_data.title}', content_length={len(post_data.content)}")
        service = PostService(db)
        post = await service.create_post(post_data, current_user.id)
        print(f"[API] Post created successfully with ID {post.id}")
        return post
    except Exception as e:
        print(f"[API] Error creating post: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create post: {str(e)}"
        )


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
    """Get all posts by a specific user"""
    try:
        service = PostService(db)
        posts = await service.get_user_posts(user_id, skip, limit)
        return posts or []
    except Exception as e:
        print(f"[API] Error getting user posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user posts"
        )


@router.get(
    "/{post_id}",
    response_model=PostResponse,
)
async def get_post(
    post_id: int,
    db: DBDep,
):
    """Get a specific post by ID"""
    try:
        service = PostService(db)
        post = await service.get_post(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        return post
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error getting post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get post"
        )


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
    """Get all posts with optional filtering by user"""
    try:
        service = PostService(db)
        if user_id:
            return await service.get_user_posts(user_id, skip, limit)
        posts = await service.get_all_posts(skip, limit)
        return posts or []
    except Exception as e:
        print(f"[API] Error getting posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get posts"
        )


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
    """Update an existing post"""
    try:
        service = PostService(db)
        updated_post = await service.update_post(post_id, post_data, current_user.id)
        return updated_post
    except Exception as e:
        print(f"[API] Error updating post: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update post"
        )


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_post(
    post_id: int,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    """Delete a post (author or admin)"""
    try:
        print(f"\n[API] Delete post {post_id} by user {current_user.id}")
        print(f"[API] User is_admin: {current_user.is_admin}")
        service = PostService(db)
        # Ensure is_admin is bool, not None
        is_admin = bool(current_user.is_admin) if current_user.is_admin is not None else False
        await service.delete_post(
            post_id=post_id,
            user_id=current_user.id,
            is_admin=is_admin,
        )
        print(f"[API] Post {post_id} deleted successfully")
        return None
    except Exception as e:
        print(f"[API] Error deleting post: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete post: {str(e)}"
        )


# ===== COMMENTS =====
@router.get(
    "/{post_id}/comments",
    response_model=list[dict],
)
async def get_post_comments(
    post_id: int,
    db: DBDep,
):
    """Get all comments for a post"""
    try:
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
    except Exception as e:
        print(f"[API] Error getting comments: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get comments"
        )


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
    """Create a comment on a post"""
    try:
        service = CommentService(db)
        comment = await service.create_comment(post_id, comment_data, current_user.id)
        return {
            "id": comment.id,
            "post_id": comment.post_id,
            "user_id": comment.user_id,
            "content": comment.content,
            "created_at": comment.created_at,
            "author_username": current_user.name,
        }
    except Exception as e:
        print(f"[API] Error creating comment: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create comment"
        )


@router.delete(
    "/{post_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    post_id: int,
    comment_id: int,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    """Delete a comment (author or admin)"""
    try:
        print(f"\n[API] Delete comment {comment_id} from post {post_id} by user {current_user.id}")
        print(f"[API] User is_admin: {current_user.is_admin}")
        service = CommentService(db)
        # Ensure is_admin is bool, not None
        is_admin = bool(current_user.is_admin) if current_user.is_admin is not None else False
        await service.delete_comment(
            comment_id=comment_id,
            current_user_id=current_user.id,
            is_admin=is_admin,
        )
        print(f"[API] Comment {comment_id} deleted successfully")
        return None
    except Exception as e:
        print(f"[API] Error deleting comment: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete comment: {str(e)}"
        )


# ===== LIKES =====
@router.post(
    "/{post_id}/like",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
async def like_post(
    post_id: int,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    """Like a post"""
    try:
        service = LikeService(db)
        like = await service.create_like(post_id, current_user.id)
        return {
            "id": like.id,
            "post_id": like.post_id,
            "user_id": like.user_id,
            "created_at": like.created_at,
        }
    except Exception as e:
        print(f"[API] Error liking post: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to like post"
        )


@router.delete(
    "/{post_id}/like",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def unlike_post(
    post_id: int,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user),
):
    """Unlike a post"""
    try:
        service = LikeService(db)
        await service.delete_like(post_id, current_user.id)
        return None
    except Exception as e:
        print(f"[API] Error unliking post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unlike post"
        )


@router.get(
    "/{post_id}/likes",
    response_model=list[dict],
)
async def get_post_likes(
    post_id: int,
    db: DBDep,
):
    """Get all likes for a post"""
    try:
        service = LikeService(db)
        likes = await service.get_post_likes(post_id)
        return [
            {
                "id": like.id,
                "user_id": like.user_id,
                "username": like.user.name if like.user else "Unknown",
                "created_at": like.created_at,
            }
            for like in likes
        ]
    except Exception as e:
        print(f"[API] Error getting likes: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get likes"
        )