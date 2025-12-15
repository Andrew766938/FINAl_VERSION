from app.database.db_manager import DBManager
from app.schemes.posts import PostCreate, PostUpdate, PostResponse
from app.exceptions.exceptions import PostNotFound, Forbidden


class PostService:
    def __init__(self, db: DBManager):
        self.db = db

    async def create_post(self, post_data: PostCreate, user_id: int) -> PostResponse:
        post = await self.db.posts.create_post(post_data, user_id)
        await self.db.commit()
        return PostResponse.from_orm(post)

    async def get_post(self, post_id: int) -> PostResponse:
        post = await self.db.posts.get_post_by_id(post_id)
        if not post:
            raise PostNotFound()
        
        # Get likes count
        likes_count = await self.db.likes.get_post_likes_count(post_id)
        post_dict = PostResponse.from_orm(post).dict()
        post_dict['likes_count'] = likes_count
        return PostResponse(**post_dict)

    async def get_all_posts(self, skip: int = 0, limit: int = 10) -> list[PostResponse]:
        posts = await self.db.posts.get_all_posts(skip, limit)
        result = []
        for post in posts:
            likes_count = await self.db.likes.get_post_likes_count(post.id)
            post_dict = PostResponse.from_orm(post).dict()
            post_dict['likes_count'] = likes_count
            result.append(PostResponse(**post_dict))
        return result

    async def get_user_posts(self, user_id: int, skip: int = 0, limit: int = 10) -> list[PostResponse]:
        posts = await self.db.posts.get_user_posts(user_id, skip, limit)
        result = []
        for post in posts:
            likes_count = await self.db.likes.get_post_likes_count(post.id)
            post_dict = PostResponse.from_orm(post).dict()
            post_dict['likes_count'] = likes_count
            result.append(PostResponse(**post_dict))
        return result

    async def update_post(self, post_id: int, post_data: PostUpdate, current_user_id: int) -> PostResponse:
        post = await self.db.posts.get_post_by_id(post_id)
        if not post:
            raise PostNotFound()
        if post.user_id != current_user_id:
            raise Forbidden()
        
        updated_post = await self.db.posts.update_post(post_id, post_data)
        await self.db.commit()
        return PostResponse.from_orm(updated_post)

    async def delete_post(self, post_id: int, current_user_id: int) -> bool:
        post = await self.db.posts.get_post_by_id(post_id)
        if not post:
            raise PostNotFound()
        if post.user_id != current_user_id:
            raise Forbidden()
        
        result = await self.db.posts.delete_post(post_id)
        await self.db.commit()
        return result
