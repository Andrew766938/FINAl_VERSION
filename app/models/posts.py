from typing import TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.users import UserModel
    from app.models.comments import CommentModel
    from app.models.likes import LikeModel


class PostModel(Base):
    __tablename__ = "posts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    
    user: Mapped["UserModel"] = relationship(back_populates="posts")
    comments: Mapped[list["CommentModel"]] = relationship(back_populates="post", cascade="all, delete-orphan")
    likes: Mapped[list["LikeModel"]] = relationship(back_populates="post", cascade="all, delete-orphan")
