from typing import TYPE_CHECKING

from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.roles import RoleModel
    from app.models.posts import PostModel
    from app.models.comments import CommentModel
    from app.models.likes import LikeModel
    from app.models.friendships import FriendshipModel


class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(300), nullable=False)
            is_admin: Mapped[bool] = mapped_column(default=False, nullable=False)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    role: Mapped["RoleModel"] = relationship(back_populates="users")
    
    posts: Mapped[list["PostModel"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    comments: Mapped[list["CommentModel"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    likes: Mapped[list["LikeModel"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    friendships_initiated: Mapped[list["FriendshipModel"]] = relationship(foreign_keys="FriendshipModel.user_id", back_populates="user", cascade="all, delete-orphan")
    friendships_received: Mapped[list["FriendshipModel"]] = relationship(foreign_keys="FriendshipModel.friend_id", back_populates="friend", cascade="all, delete-orphan")
