from app.database.db_manager import DBManager
from app.schemes.posts import PostCreate, PostUpdate, PostResponse
from app.exceptions.exceptions import PostNotFound, Forbidden


class PostService:
    def __init__(self, db: DBManager):
        self.db = db

    async def create_post(self, post_data: PostCreate, user_id: int) -> PostResponse:
        # Fix: pass post_data and user_id to repository
        post = await self.db.posts.create_post(post_data, user_id)
        await self.db.commit()
        
        # Get user info for author fields
        user = await self.db.users.get_one_or_none(id=user_id)
        
        return PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            user_id=post.user_id,
            author_name=user.name if user else None,
            author_email=user.email if user else None,
            created_at=post.created_at,
            updated_at=post.updated_at,
            likes_count=0
        )

    async def get_post(self, post_id: int) -> PostResponse:
        post = await self.db.posts.get_post_by_id(post_id)
        if not post:
            raise PostNotFound()
        
        # Get likes count
        likes = await self.db.likes.get_post_likes(post_id)
        likes_count = len(likes) if likes else 0
        
        # Get user info
        user = await self.db.users.get_one_or_none(id=post.user_id)
        
        return PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            user_id=post.user_id,
            author_name=user.name if user else None,
            author_email=user.email if user else None,
            created_at=post.created_at,
            updated_at=post.updated_at,
            likes_count=likes_count
        )

    async def get_all_posts(self, skip: int = 0, limit: int = 20) -> list[PostResponse]:
        posts = await self.db.posts.get_all_posts(skip, limit)
        result = []
        
        for post in posts:
            likes = await self.db.likes.get_post_likes(post.id)
            likes_count = len(likes) if likes else 0
            user = await self.db.users.get_one_or_none(id=post.user_id)
            
            result.append(PostResponse(
                id=post.id,
                title=post.title,
                content=post.content,
                user_id=post.user_id,
                author_name=user.name if user else None,
                author_email=user.email if user else None,
                created_at=post.created_at,
                updated_at=post.updated_at,
                likes_count=likes_count
            ))
        
        return result

    async def get_user_posts(self, user_id: int, skip: int = 0, limit: int = 20) -> list[PostResponse]:
        posts = await self.db.posts.get_user_posts(user_id, skip, limit)
        result = []
        
        # Get user info once
        user = await self.db.users.get_one_or_none(id=user_id)
        
        for post in posts:
            likes = await self.db.likes.get_post_likes(post.id)
            likes_count = len(likes) if likes else 0
            
            result.append(PostResponse(
                id=post.id,
                title=post.title,
                content=post.content,
                user_id=post.user_id,
                author_name=user.name if user else None,
                author_email=user.email if user else None,
                created_at=post.created_at,
                updated_at=post.updated_at,
                likes_count=likes_count
            ))
        
        return result

    async def update_post(self, post_id: int, post_data: PostUpdate, user_id: int) -> PostResponse:
        post = await self.db.posts.get_post_by_id(post_id)
        if not post:
            raise PostNotFound()
        
        if post.user_id != user_id:
            raise Forbidden()
        
        updated_post = await self.db.posts.update_post(post_id, post_data)
        await self.db.commit()
        
        likes = await self.db.likes.get_post_likes(post_id)
        likes_count = len(likes) if likes else 0
        user = await self.db.users.get_one_or_none(id=user_id)
        
        return PostResponse(
            id=updated_post.id,
            title=updated_post.title,
            content=updated_post.content,
            user_id=updated_post.user_id,
            author_name=user.name if user else None,
            author_email=user.email if user else None,
            created_at=updated_post.created_at,
            updated_at=updated_post.updated_at,
            likes_count=likes_count
        )

    async def delete_post(self, post_id: int, user_id: int, is_admin: bool = False) -> bool:
        """Delete a post. Only author or admin can delete."""
        post = await self.db.posts.get_post_by_id(post_id)
        if not post:
            raise PostNotFound()
        
        # Allow deletion if user is author OR if user is admin
        if post.user_id != user_id and not is_admin:
            raise Forbidden()
        
        success = await self.db.posts.delete_post(post_id)
        if not success:
            raise PostNotFound()
        
        await self.db.commit()
        return True