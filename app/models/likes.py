from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.users import UserModel
    from app.models.posts import PostModel


class LikeModel(Base):
    __tablename__ = "likes"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user: Mapped["UserModel"] = relationship(back_populates="likes")
    post: Mapped["PostModel"] = relationship(back_populates="likes")
