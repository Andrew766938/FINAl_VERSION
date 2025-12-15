from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.posts import PostRepository
from app.repositories.likes import LikeRepository
from app.schemes.posts import PostCreate, PostUpdate, PostResponse
from app.exceptions.exceptions import PostNotFound, Forbidden


class PostService:
    def __init__(self, session: AsyncSession):
        self.post_repo = PostRepository(session)
        self.like_repo = LikeRepository(session)
        self.session = session

    async def create_post(self, post_data: PostCreate, user_id: int) -> PostResponse:
        post = await self.post_repo.create_post(post_data, user_id)
        return PostResponse.from_orm(post)

    async def get_post(self, post_id: int) -> PostResponse:
        post = await self.post_repo.get_post_by_id(post_id)
        if not post:
            raise PostNotFound()
        return PostResponse.from_orm(post)

    async def get_all_posts(self, skip: int = 0, limit: int = 10) -> list[PostResponse]:
        posts = await self.post_repo.get_all_posts(skip, limit)
        return [PostResponse.from_orm(post) for post in posts]

    async def get_user_posts(self, user_id: int, skip: int = 0, limit: int = 10) -> list[PostResponse]:
        posts = await self.post_repo.get_user_posts(user_id, skip, limit)
        return [PostResponse.from_orm(post) for post in posts]

    async def update_post(self, post_id: int, post_data: PostUpdate, current_user_id: int) -> PostResponse:
        post = await self.post_repo.get_post_by_id(post_id)
        if not post:
            raise PostNotFound()
        if post.user_id != current_user_id:
            raise Forbidden()
        
        updated_post = await self.post_repo.update_post(post_id, post_data)
        return PostResponse.from_orm(updated_post)

    async def delete_post(self, post_id: int, current_user_id: int) -> bool:
        post = await self.post_repo.get_post_by_id(post_id)
        if not post:
            raise PostNotFound()
        if post.user_id != current_user_id:
            raise Forbidden()
        
        return await self.post_repo.delete_post(post_id)

    async def increment_likes(self, post_id: int) -> int:
        post = await self.post_repo.increment_likes(post_id)
        if not post:
            raise PostNotFound()
        return post.likes_count

    async def decrement_likes(self, post_id: int) -> int:
        post = await self.post_repo.decrement_likes(post_id)
        if not post:
            raise PostNotFound()
        return post.likes_count
