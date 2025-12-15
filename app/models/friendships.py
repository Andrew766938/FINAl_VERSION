from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.users import UserModel


class FriendshipModel(Base):
    __tablename__ = "friendships"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    friend_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user: Mapped["UserModel"] = relationship(foreign_keys=[user_id], back_populates="friendships_initiated")
    friend: Mapped["UserModel"] = relationship(foreign_keys=[friend_id], back_populates="friendships_received")
