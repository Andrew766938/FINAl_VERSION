from app.database.database import async_session_maker
from app.repositories.roles import RolesRepository
from app.repositories.users import UsersRepository
from app.repositories.posts import PostRepository
from app.repositories.comments import CommentRepository
from app.repositories.likes import LikeRepository
from app.repositories.friendships import FriendshipRepository


class DBManager:
    def __init__(self, session_factory: async_session_maker):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        
        # Initialize all repositories
        self.users = UsersRepository(self.session)
        self.roles = RolesRepository(self.session)
        self.posts = PostRepository(self.session)
        self.comments = CommentRepository(self.session)
        self.likes = LikeRepository(self.session)
        self.friendships = FriendshipRepository(self.session)
        
        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()
