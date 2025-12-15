from pydantic import BaseModel
from datetime import datetime


class FriendshipCreate(BaseModel):
    friend_id: int


class FriendshipResponse(BaseModel):
    id: int
    user_id: int
    friend_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
