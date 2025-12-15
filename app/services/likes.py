from app.database.db_manager import DBManager
from app.schemes.posts import PostResponse
from app.exceptions.exceptions import AlreadyLiked, PostNotFound


class LikeService:
    def __init__(self, db: DBManager):
        self.db = db

    async def like_post(self, user_id: int, post_id: int) -> dict:
        post = await self.db.posts.get_post_by_id(post_id)
        if not post:
            raise PostNotFound()
        
        existing_like = await self.db.likes.get_like(user_id, post_id)
        if existing_like:
            raise AlreadyLiked()
        
        await self.db.likes.create_like(user_id, post_id)
        await self.db.commit()
        
        return {"message": "Post liked successfully"}

    async def unlike_post(self, user_id: int, post_id: int) -> dict:
        post = await self.db.posts.get_post_by_id(post_id)
        if not post:
            raise PostNotFound()
        
        await self.db.likes.delete_like_by_user_post(user_id, post_id)
        await self.db.commit()
        
        return {"message": "Post unliked successfully"}

    async def get_post_likes(self, post_id: int) -> list:
        likes = await self.db.likes.get_post_likes(post_id)
        return [{'user_id': like.user_id, 'created_at': like.created_at} for like in likes]

    async def get_user_likes(self, user_id: int) -> list:
        likes = await self.db.likes.get_user_likes(user_id)
        return [{'post_id': like.post_id, 'created_at': like.created_at} for like in likes]

    async def is_liked(self, user_id: int, post_id: int) -> bool:
        like = await self.db.likes.get_like(user_id, post_id)
        return like is not None
