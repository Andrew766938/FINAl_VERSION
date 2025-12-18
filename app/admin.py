from sqladmin import Admin, ModelView
from sqlalchemy.ext.asyncio import AsyncEngine
from fastapi import FastAPI
import logging

from app.models.users import UserModel
from app.models.posts import PostModel
from app.models.comments import CommentModel
from app.models.likes import LikeModel
from app.models.roles import RoleModel
from app.models.friendships import FriendshipModel

logger = logging.getLogger(__name__)


class UserAdmin(ModelView, model=UserModel):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    column_list = [UserModel.id, UserModel.email, UserModel.name, UserModel.is_admin]
    column_details_exclude_list = [UserModel.hashed_password]
    column_searchable_list = [UserModel.email, UserModel.name]
    column_sortable_list = [UserModel.id, UserModel.email, UserModel.is_admin]


class PostAdmin(ModelView, model=PostModel):
    name = "Post"
    name_plural = "Posts"
    icon = "fa-solid fa-file"
    column_list = [PostModel.id, PostModel.title, PostModel.user_id, PostModel.created_at]
    column_searchable_list = [PostModel.title]
    column_sortable_list = [PostModel.id, PostModel.created_at]


class CommentAdmin(ModelView, model=CommentModel):
    name = "Comment"
    name_plural = "Comments"
    icon = "fa-solid fa-comment"
    column_list = [CommentModel.id, CommentModel.content, CommentModel.user_id, CommentModel.created_at]
    column_searchable_list = [CommentModel.content]
    column_sortable_list = [CommentModel.id, CommentModel.created_at]


class LikeAdmin(ModelView, model=LikeModel):
    name = "Like"
    name_plural = "Likes"
    icon = "fa-solid fa-heart"
    column_list = [LikeModel.id, LikeModel.user_id, LikeModel.post_id, LikeModel.created_at]
    column_sortable_list = [LikeModel.id, LikeModel.created_at]


class RoleAdmin(ModelView, model=RoleModel):
    name = "Role"
    name_plural = "Roles"
    icon = "fa-solid fa-shield"
    column_list = [RoleModel.id, RoleModel.name, RoleModel.description]
    column_searchable_list = [RoleModel.name]


class FriendshipAdmin(ModelView, model=FriendshipModel):
    name = "Friendship"
    name_plural = "Friendships"
    icon = "fa-solid fa-handshake"
    column_list = [FriendshipModel.id, FriendshipModel.user_id, FriendshipModel.friend_id, FriendshipModel.created_at]
    column_sortable_list = [FriendshipModel.id, FriendshipModel.created_at]


def setup_admin(app: FastAPI, engine: AsyncEngine):
    """
    Setup SQLAdmin with the FastAPI app
    Access at: http://localhost:8000/admin
    """
    try:
        admin = Admin(
            app=app,
            engine=engine,
            title="🌿 Betony Admin",
            authentication_backend=None,  # No auth required
        )
        
        # Register all model views
        admin.add_view(RoleAdmin)
        admin.add_view(UserAdmin)
        admin.add_view(PostAdmin)
        admin.add_view(CommentAdmin)
        admin.add_view(LikeAdmin)
        admin.add_view(FriendshipAdmin)
        
        logger.info("✅ SQLAdmin initialized successfully")
        print("✅ SQLAdmin models registered")
        return admin
    except Exception as e:
        logger.error(f"❌ SQLAdmin error: {e}")
        print(f"❌ SQLAdmin error: {e}")
        import traceback
        traceback.print_exc()
        raise
