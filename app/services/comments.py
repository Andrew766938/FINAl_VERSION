from app.database.db_manager import DBManager
from app.schemes.comments import CommentCreate, CommentUpdate, CommentResponse
from app.exceptions.exceptions import CommentNotFound, Forbidden


class CommentService:
    def __init__(self, db: DBManager):
        self.db = db

    async def create_comment(self, post_id: int, comment_data: CommentCreate, user_id: int):
        """Create a new comment on a post"""
        comment = await self.db.comments.create_comment(comment_data, user_id, post_id)
        await self.db.commit()
        return comment

    async def get_comment(self, comment_id: int):
        """Get a specific comment by ID"""
        comment = await self.db.comments.get_comment_by_id(comment_id)
        if not comment:
            raise CommentNotFound()
        return comment

    async def get_post_comments(self, post_id: int, skip: int = 0, limit: int = 20):
        """Get all comments for a post"""
        comments = await self.db.comments.get_post_comments(post_id, skip, limit)
        return comments or []

    async def get_user_comments(self, user_id: int, skip: int = 0, limit: int = 20):
        """Get all comments by a user"""
        comments = await self.db.comments.get_user_comments(user_id, skip, limit)
        return comments or []

    async def update_comment(self, comment_id: int, comment_data: CommentCreate, current_user_id: int):
        """Update a comment"""
        comment = await self.db.comments.get_comment_by_id(comment_id)
        if not comment:
            raise CommentNotFound()
        if comment.user_id != current_user_id:
            raise Forbidden()
        
        updated_comment = await self.db.comments.update_comment(comment_id, comment_data)
        await self.db.commit()
        return updated_comment

    async def delete_comment(self, comment_id: int, current_user_id: int) -> bool:
        """Delete a comment"""
        comment = await self.db.comments.get_comment_by_id(comment_id)
        if not comment:
            raise CommentNotFound()
        if comment.user_id != current_user_id:
            raise Forbidden()
        
        result = await self.db.comments.delete_comment(comment_id)
        await self.db.commit()
        return result
