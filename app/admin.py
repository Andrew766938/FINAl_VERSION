from sqladmin import Admin, ModelView
from sqlalchemy.ext.asyncio import AsyncEngine
import logging

from app.models.users import UserModel
from app.models.posts import PostModel
from app.models.comments import CommentModel
from app.models.likes import LikeModel
from app.models.roles import RoleModel
from app.models.friendships import FriendshipModel

logger = logging.getLogger(__name__)


class UserAdmin(ModelView, model=UserModel):
    """Admin panel for Users"""
    column_list = [UserModel.id, UserModel.name, UserModel.email, UserModel.is_admin, UserModel.role_id]
    column_searchable_list = [UserModel.name, UserModel.email]
    column_sortable_list = [UserModel.id, UserModel.name, UserModel.email, UserModel.is_admin]
    form_columns = [UserModel.name, UserModel.email, UserModel.is_admin, UserModel.role_id]
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"


class PostAdmin(ModelView, model=PostModel):
    """Admin panel for Posts"""
    column_list = [PostModel.id, PostModel.title, PostModel.user_id, PostModel.created_at]
    column_searchable_list = [PostModel.title]
    column_sortable_list = [PostModel.id, PostModel.created_at]
    form_columns = [PostModel.title, PostModel.content, PostModel.user_id]
    name = "Post"
    name_plural = "Posts"
    icon = "fa-solid fa-file"


class CommentAdmin(ModelView, model=CommentModel):
    """Admin panel for Comments"""
    column_list = [CommentModel.id, CommentModel.content, CommentModel.user_id, CommentModel.post_id, CommentModel.created_at]
    column_searchable_list = [CommentModel.content]
    column_sortable_list = [CommentModel.id, CommentModel.created_at]
    form_columns = [CommentModel.content, CommentModel.user_id, CommentModel.post_id]
    name = "Comment"
    name_plural = "Comments"
    icon = "fa-solid fa-comment"


class LikeAdmin(ModelView, model=LikeModel):
    """Admin panel for Likes"""
    column_list = [LikeModel.id, LikeModel.user_id, LikeModel.post_id, LikeModel.created_at]
    column_sortable_list = [LikeModel.id, LikeModel.created_at]
    form_columns = [LikeModel.user_id, LikeModel.post_id]
    name = "Like"
    name_plural = "Likes"
    icon = "fa-solid fa-heart"


class RoleAdmin(ModelView, model=RoleModel):
    """Admin panel for Roles"""
    column_list = [RoleModel.id, RoleModel.name, RoleModel.description]
    column_searchable_list = [RoleModel.name]
    form_columns = [RoleModel.name, RoleModel.description]
    name = "Role"
    name_plural = "Roles"
    icon = "fa-solid fa-shield"


class FriendshipAdmin(ModelView, model=FriendshipModel):
    """Admin panel for Friendships"""
    column_list = [FriendshipModel.id, FriendshipModel.user_id, FriendshipModel.friend_id, FriendshipModel.created_at]
    column_sortable_list = [FriendshipModel.id, FriendshipModel.created_at]
    form_columns = [FriendshipModel.user_id, FriendshipModel.friend_id]
    name = "Friendship"
    name_plural = "Friendships"
    icon = "fa-solid fa-handshake"


def setup_admin(app, engine: AsyncEngine):
    """
    Setup SQLAdmin with the FastAPI app
    Access at: http://localhost:8000/admin
    """
    try:
        admin = Admin(
            app,
            engine,
            title="🌿 Betony Admin Panel",
        )
        
        logger.info("✅ SQLAdmin panel initialized at /admin")
        return admin
    except Exception as e:
        logger.error(f"❌ Error initializing SQLAdmin: {e}")
        import traceback
        traceback.print_exc()
        raise
