from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.likes import LikeModel


class LikeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_like(self, user_id: int, post_id: int) -> LikeModel:
        db_like = LikeModel(
            user_id=user_id,
            post_id=post_id
        )
        self.session.add(db_like)
        await self.session.commit()
        await self.session.refresh(db_like)
        return db_like

    async def get_like(self, user_id: int, post_id: int) -> LikeModel | None:
        result = await self.session.execute(
            select(LikeModel)
            .where(LikeModel.user_id == user_id)
            .where(LikeModel.post_id == post_id)
        )
        return result.scalar_one_or_none()

    async def get_post_likes(self, post_id: int) -> list[LikeModel]:
        result = await self.session.execute(
            select(LikeModel).where(LikeModel.post_id == post_id)
        )
        return result.scalars().all()

    async def get_user_likes(self, user_id: int) -> list[LikeModel]:
        result = await self.session.execute(
            select(LikeModel).where(LikeModel.user_id == user_id)
        )
        return result.scalars().all()

    async def delete_like(self, like_id: int) -> bool:
        like = await self.session.get(LikeModel, like_id)
        if not like:
            return False
        
        await self.session.delete(like)
        await self.session.commit()
        return True

    async def delete_like_by_user_post(self, user_id: int, post_id: int) -> bool:
        like = await self.get_like(user_id, post_id)
        if not like:
            return False
        
        await self.session.delete(like)
        await self.session.commit()
        return True
