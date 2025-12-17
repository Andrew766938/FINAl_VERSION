from app.database.db_manager import DBManager
from app.schemes.posts import PostResponse
from app.exceptions.exceptions import AlreadyLiked, PostNotFound


class LikeService:
    def __init__(self, db: DBManager):
        self.db = db

    async def create_like(self, post_id: int, user_id: int):
        """Create a like on a post"""
        post = await self.db.posts.get_post_by_id(post_id)
        if not post:
            raise PostNotFound()
        
        existing_like = await self.db.likes.get_like(user_id, post_id)
        if existing_like:
            raise AlreadyLiked()
        
        like = await self.db.likes.create_like(user_id, post_id)
        await self.db.commit()
        
        return like

    async def like_post(self, user_id: int, post_id: int) -> dict:
        """Like a post (legacy method)"""
        post = await self.db.posts.get_post_by_id(post_id)
        if not post:
            raise PostNotFound()
        
        existing_like = await self.db.likes.get_like(user_id, post_id)
        if existing_like:
            raise AlreadyLiked()
        
        await self.db.likes.create_like(user_id, post_id)
        await self.db.commit()
        
        return {"message": "Post liked successfully"}

    async def delete_like(self, post_id: int, user_id: int):
        """Remove a like from a post"""
        post = await self.db.posts.get_post_by_id(post_id)
        if not post:
            raise PostNotFound()
        
        await self.db.likes.delete_like_by_user_post(user_id, post_id)
        await self.db.commit()

    async def delete_like_by_id(self, like_id: int, user_id: int):
        """Delete a like by its ID"""
        like = await self.db.likes.get_like_by_id(like_id)
        if not like:
            raise Exception("Like not found")
        
        if like.user_id != user_id:
            raise Exception("Unauthorized: can only delete your own likes")
        
        await self.db.likes.delete_like(like_id)
        await self.db.commit()

    async def unlike_post(self, user_id: int, post_id: int) -> dict:
        """Unlike a post (legacy method)"""
        post = await self.db.posts.get_post_by_id(post_id)
        if not post:
            raise PostNotFound()
        
        await self.db.likes.delete_like_by_user_post(user_id, post_id)
        await self.db.commit()
        
        return {"message": "Post unliked successfully"}

    async def get_post_likes(self, post_id: int) -> list:
        """Get all likes for a post"""
        likes = await self.db.likes.get_post_likes(post_id)
        return likes or []

    async def get_user_likes(self, user_id: int) -> list:
        """Get all likes by a user"""
        likes = await self.db.likes.get_user_likes(user_id)
        return likes or []

    async def get_like(self, like_id: int):
        """Get a specific like by ID"""
        like = await self.db.likes.get_like_by_id(like_id)
        return like

    async def is_liked(self, user_id: int, post_id: int) -> bool:
        """Check if a post is liked by a user"""
        like = await self.db.likes.get_like(user_id, post_id)
        return like is not None
