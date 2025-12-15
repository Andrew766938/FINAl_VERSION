from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.comments import CommentRepository
from app.schemes.comments import CommentCreate, CommentUpdate, CommentResponse
from app.exceptions.exceptions import CommentNotFound, Forbidden


class CommentService:
    def __init__(self, session: AsyncSession):
        self.comment_repo = CommentRepository(session)
        self.session = session

    async def create_comment(self, comment_data: CommentCreate, user_id: int, post_id: int) -> CommentResponse:
        comment = await self.comment_repo.create_comment(comment_data, user_id, post_id)
        return CommentResponse.from_orm(comment)

    async def get_comment(self, comment_id: int) -> CommentResponse:
        comment = await self.comment_repo.get_comment_by_id(comment_id)
        if not comment:
            raise CommentNotFound()
        return CommentResponse.from_orm(comment)

    async def get_post_comments(self, post_id: int, skip: int = 0, limit: int = 20) -> list[CommentResponse]:
        comments = await self.comment_repo.get_post_comments(post_id, skip, limit)
        return [CommentResponse.from_orm(comment) for comment in comments]

    async def get_user_comments(self, user_id: int, skip: int = 0, limit: int = 20) -> list[CommentResponse]:
        comments = await self.comment_repo.get_user_comments(user_id, skip, limit)
        return [CommentResponse.from_orm(comment) for comment in comments]

    async def update_comment(self, comment_id: int, comment_data: CommentUpdate, current_user_id: int) -> CommentResponse:
        comment = await self.comment_repo.get_comment_by_id(comment_id)
        if not comment:
            raise CommentNotFound()
        if comment.user_id != current_user_id:
            raise Forbidden()
        
        updated_comment = await self.comment_repo.update_comment(comment_id, comment_data)
        return CommentResponse.from_orm(updated_comment)

    async def delete_comment(self, comment_id: int, current_user_id: int) -> bool:
        comment = await self.comment_repo.get_comment_by_id(comment_id)
        if not comment:
            raise CommentNotFound()
        if comment.user_id != current_user_id:
            raise Forbidden()
        
        return await self.comment_repo.delete_comment(comment_id)
