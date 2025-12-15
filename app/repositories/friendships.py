from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.friendships import FriendshipModel
from app.schemes.friendships import FriendshipCreate


class FriendshipRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_friendship(self, user_id: int, friend_id: int) -> FriendshipModel:
        db_friendship = FriendshipModel(
            user_id=user_id,
            friend_id=friend_id
        )
        self.session.add(db_friendship)
        await self.session.commit()
        await self.session.refresh(db_friendship)
        return db_friendship

    async def get_friendship(self, user_id: int, friend_id: int) -> FriendshipModel | None:
        result = await self.session.execute(
            select(FriendshipModel)
            .where(FriendshipModel.user_id == user_id)
            .where(FriendshipModel.friend_id == friend_id)
        )
        return result.scalar_one_or_none()

    async def get_user_friends(self, user_id: int, skip: int = 0, limit: int = 20) -> list[FriendshipModel]:
        result = await self.session.execute(
            select(FriendshipModel)
            .where(FriendshipModel.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(FriendshipModel.created_at.desc())
        )
        return result.scalars().all()

    async def get_user_incoming_friendships(self, friend_id: int, skip: int = 0, limit: int = 20) -> list[FriendshipModel]:
        result = await self.session.execute(
            select(FriendshipModel)
            .where(FriendshipModel.friend_id == friend_id)
            .offset(skip)
            .limit(limit)
            .order_by(FriendshipModel.created_at.desc())
        )
        return result.scalars().all()

    async def delete_friendship(self, friendship_id: int) -> bool:
        friendship = await self.session.get(FriendshipModel, friendship_id)
        if not friendship:
            return False
        
        await self.session.delete(friendship)
        await self.session.commit()
        return True

    async def delete_friendship_by_users(self, user_id: int, friend_id: int) -> bool:
        friendship = await self.get_friendship(user_id, friend_id)
        if not friendship:
            return False
        
        await self.session.delete(friendship)
        await self.session.commit()
        return True
