from typing import Annotated

from fastapi import Depends, Request
from pydantic import BaseModel, Field

from app.database.database import async_session_maker
from app.exceptions.auth import (
    InvalidJWTTokenError,
    InvalidTokenHTTPError,
    NoAccessTokenHTTPError,
)
from app.services.auth import AuthService
from app.database.db_manager import DBManager
from app.models.users import UserModel


class PaginationParams(BaseModel):
    page: int | None = Field(default=1, ge=1)
    per_page: int | None = Field(default=5, ge=1, le=30)


PaginationDep = Annotated[PaginationParams, Depends()]


def get_token(request: Request) -> str:
    """Get token from Authorization header or cookies"""
    # Извлекаем токен из Authorization header (приоритет)
    auth_header = request.headers.get("Authorization")
    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
            print(f"[AUTH] ✅ Token from Authorization header: {token[:20]}...")
            return token
    
    # Извлекаем токен из cookies
    token = request.cookies.get("access_token")
    if token:
        print(f"[AUTH] ✅ Token from cookies: {token[:20]}...")
        return token
    
    print(f"[AUTH] ❌ No token found in Authorization header or cookies")
    raise NoAccessTokenHTTPError


def get_current_user_id(token: str = Depends(get_token)) -> int:
    """Extract user ID from token"""
    try:
        print(f"[AUTH] Decoding token...")
        user_id = AuthService.verify_token(token)
        if not user_id:
            print(f"[AUTH] ❌ Token verification failed")
            raise InvalidTokenHTTPError
        print(f"[AUTH] ✅ Token decoded successfully, user_id: {user_id}")
        return user_id
    except InvalidJWTTokenError as e:
        print(f"[AUTH] ❌ Invalid token: {e}")
        raise InvalidTokenHTTPError
    except Exception as e:
        print(f"[AUTH] ❌ Token error: {e}")
        import traceback
        traceback.print_exc()
        raise InvalidTokenHTTPError


UserIdDep = Annotated[int, Depends(get_current_user_id)]


async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


async def get_current_user(
    db: DBDep,
    user_id: int = Depends(get_current_user_id),
) -> UserModel:
    """Get current authenticated user from database"""
    try:
        print(f"[AUTH] Getting user with ID: {user_id}")
        user = await db.users.get_one_or_none(id=user_id)
        if not user:
            print(f"[AUTH] ❌ User not found with ID: {user_id}")
            raise InvalidTokenHTTPError
        print(f"[AUTH] ✅ User found: {user.email}")
        return user
    except Exception as e:
        print(f"[AUTH] ❌ Error getting user: {e}")
        import traceback
        traceback.print_exc()
        raise InvalidTokenHTTPError