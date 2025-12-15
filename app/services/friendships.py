from app.database.db_manager import DBManager
from app.schemes.friendships import FriendshipResponse
from app.exceptions.exceptions import AlreadyFriends, FriendshipNotFound


class FriendshipService:
    def __init__(self, db: DBManager):
        self.db = db

    async def add_friend(self, user_id: int, friend_id: int) -> FriendshipResponse:
        if user_id == friend_id:
            raise Exception("Cannot add yourself as friend")
        
        existing_friendship = await self.db.friendships.get_friendship(user_id, friend_id)
        if existing_friendship:
            raise AlreadyFriends()
        
        friendship = await self.db.friendships.create_friendship(user_id, friend_id)
        await self.db.commit()
        return FriendshipResponse.from_orm(friendship)

    async def remove_friend(self, user_id: int, friend_id: int) -> bool:
        success = await self.db.friendships.delete_friendship_by_users(user_id, friend_id)
        if not success:
            raise FriendshipNotFound()
        await self.db.commit()
        return True

    async def get_user_friends(self, user_id: int, skip: int = 0, limit: int = 20) -> list[FriendshipResponse]:
        friendships = await self.db.friendships.get_user_friends(user_id, skip, limit)
        return [FriendshipResponse.from_orm(f) for f in friendships]

    async def get_user_followers(self, user_id: int, skip: int = 0, limit: int = 20) -> list[FriendshipResponse]:
        friendships = await self.db.friendships.get_user_incoming_friendships(user_id, skip, limit)
        return [FriendshipResponse.from_orm(f) for f in friendships]

    async def is_friend(self, user_id: int, friend_id: int) -> bool:
        friendship = await self.db.friendships.get_friendship(user_id, friend_id)
        return friendship is not None
