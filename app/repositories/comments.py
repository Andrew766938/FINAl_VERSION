from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.comments import CommentModel
from app.schemes.comments import CommentCreate, CommentUpdate


class CommentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_comment(self, comment_data: CommentCreate, user_id: int, post_id: int) -> CommentModel:
        db_comment = CommentModel(
            content=comment_data.content,
            user_id=user_id,
            post_id=post_id
        )
        self.session.add(db_comment)
        await self.session.commit()
        await self.session.refresh(db_comment)
        return db_comment

    async def get_comment_by_id(self, comment_id: int) -> CommentModel | None:
        result = await self.session.execute(
            select(CommentModel).where(CommentModel.id == comment_id)
        )
        return result.scalar_one_or_none()

    async def get_post_comments(self, post_id: int, skip: int = 0, limit: int = 20) -> list[CommentModel]:
        result = await self.session.execute(
            select(CommentModel)
            .where(CommentModel.post_id == post_id)
            .offset(skip)
            .limit(limit)
            .order_by(CommentModel.created_at.desc())
        )
        return result.scalars().all()

    async def get_user_comments(self, user_id: int, skip: int = 0, limit: int = 20) -> list[CommentModel]:
        result = await self.session.execute(
            select(CommentModel)
            .where(CommentModel.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(CommentModel.created_at.desc())
        )
        return result.scalars().all()

    async def update_comment(self, comment_id: int, comment_data: CommentUpdate) -> CommentModel | None:
        db_comment = await self.get_comment_by_id(comment_id)
        if not db_comment:
            return None
        
        db_comment.content = comment_data.content
        await self.session.commit()
        await self.session.refresh(db_comment)
        return db_comment

    async def delete_comment(self, comment_id: int) -> bool:
        db_comment = await self.get_comment_by_id(comment_id)
        if not db_comment:
            return False
        
        await self.session.delete(db_comment)
        await self.session.commit()
        return True
