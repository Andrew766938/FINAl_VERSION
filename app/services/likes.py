from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.likes import LikeRepository
from app.repositories.posts import PostRepository
from app.schemes.posts import PostResponse
from app.exceptions.exceptions import AlreadyLiked, PostNotFound


class LikeService:
    def __init__(self, session: AsyncSession):
        self.like_repo = LikeRepository(session)
        self.post_repo = PostRepository(session)
        self.session = session

    async def like_post(self, user_id: int, post_id: int) -> PostResponse:
        post = await self.post_repo.get_post_by_id(post_id)
        if not post:
            raise PostNotFound()
        
        existing_like = await self.like_repo.get_like(user_id, post_id)
        if existing_like:
            raise AlreadyLiked()
        
        await self.like_repo.create_like(user_id, post_id)
        await self.post_repo.increment_likes(post_id)
        
        updated_post = await self.post_repo.get_post_by_id(post_id)
        return PostResponse.from_orm(updated_post)

    async def unlike_post(self, user_id: int, post_id: int) -> PostResponse:
        post = await self.post_repo.get_post_by_id(post_id)
        if not post:
            raise PostNotFound()
        
        await self.like_repo.delete_like_by_user_post(user_id, post_id)
        await self.post_repo.decrement_likes(post_id)
        
        updated_post = await self.post_repo.get_post_by_id(post_id)
        return PostResponse.from_orm(updated_post)

    async def get_post_likes(self, post_id: int) -> list:
        likes = await self.like_repo.get_post_likes(post_id)
        return [{'user_id': like.user_id, 'created_at': like.created_at} for like in likes]

    async def get_user_likes(self, user_id: int) -> list:
        likes = await self.like_repo.get_user_likes(user_id)
        return [{'post_id': like.post_id, 'created_at': like.created_at} for like in likes]

    async def is_liked(self, user_id: int, post_id: int) -> bool:
        like = await self.like_repo.get_like(user_id, post_id)
        return like is not None
