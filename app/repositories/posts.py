from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.posts import PostModel
from app.schemes.posts import PostCreate, PostUpdate


class PostRepository:
    def __init__(self, session: AsyncSession):
        self.session = session.session

    async def create_post(self, post_data: PostCreate, user_id: int) -> PostModel:
        db_post = PostModel(
            title=post_data.title,
            content=post_data.content,
            user_id=user_id
        )
        self.session.add(db_post)
        await self.session.commit()
        await self.session.refresh(db_post)
        return db_post

    async def get_post_by_id(self, post_id: int) -> PostModel | None:
        result = await self.session.execute(
            select(PostModel).where(PostModel.id == post_id)
        )
        return result.scalar_one_or_none()

    async def get_all_posts(self, skip: int = 0, limit: int = 10) -> list[PostModel]:
        result = await self.session.execute(
            select(PostModel).offset(skip).limit(limit).order_by(PostModel.created_at.desc())
        )
        return result.scalars().all()

    async def get_user_posts(self, user_id: int, skip: int = 0, limit: int = 10) -> list[PostModel]:
        result = await self.session.execute(
            select(PostModel)
            .where(PostModel.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(PostModel.created_at.desc())
        )
        return result.scalars().all()

    async def update_post(self, post_id: int, post_data: PostUpdate) -> PostModel | None:
        db_post = await self.get_post_by_id(post_id)
        if not db_post:
            return None
        
        if post_data.title:
            db_post.title = post_data.title
        if post_data.content:
            db_post.content = post_data.content
            
        await self.session.commit()
        await self.session.refresh(db_post)
        return db_post

    async def delete_post(self, post_id: int) -> bool:
        db_post = await self.get_post_by_id(post_id)
        if not db_post:
            return False
        
        await self.session.delete(db_post)
        await self.session.commit()
        return True

    async def increment_likes(self, post_id: int) -> PostModel | None:
        db_post = await self.get_post_by_id(post_id)
        if db_post:
            db_post.likes_count += 1
            await self.session.commit()
            await self.session.refresh(db_post)
        return db_post

    async def decrement_likes(self, post_id: int) -> PostModel | None:
        db_post = await self.get_post_by_id(post_id)
        if db_post and db_post.likes_count > 0:
            db_post.likes_count -= 1
            await self.session.commit()
            await self.session.refresh(db_post)
        return db_post
