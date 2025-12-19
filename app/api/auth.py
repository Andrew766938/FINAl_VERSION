from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from starlette.responses import Response
import traceback
import json
from sqlalchemy import func

from app.api.dependencies import DBDep, get_current_user
from app.models.users import UserModel
from app.services.auth import AuthService
from app.schemes.users import SUserAddRequest  # Импортируем валидированную схему
from app.models.posts import PostModel
from app.models.friendships import FriendshipModel
from app.models.likes import LikeModel

router = APIRouter(prefix="/auth", tags=["auth"])

# Pydantic модели для валидации
class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    db: DBDep,
    data: SUserAddRequest  # Используем валидированную схему
) -> dict:
    """
    Registration endpoint - accepts JSON body
    Валидация:
    - email: standard email format (user@domain.com)
    - password: 6-10 символов
    - name: 4-15 символов
    """
    try:
        print(f"\n[API] 🇖 Register endpoint called")
        print(f"[API] Email: {data.email}, Name: {data.name}")
        
        if not data.email or not data.password or not data.name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email, password, and name are required"
            )
        
        service = AuthService(db)
        user, token = await service.register_and_login(data.email, data.password, data.name)
        
        print(f"[API] ✅ Registration successful for {user.email}")
        print(f"[API] User is_admin (DB): {user.is_admin} (type: {type(user.is_admin)})")
        
        is_admin_value = bool(user.is_admin) if user.is_admin is not None else False
        print(f"[API] User is_admin (converted): {is_admin_value}")
        
        return {
            "access_token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "is_admin": is_admin_value,
            }
        }
    except ValueError as e:
        print(f"[API] ❌ Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] ❌ Registration error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed: " + str(e)
        )


@router.post("/login")
async def login_user(
    db: DBDep,
    response: Response,
    data: LoginRequest
) -> dict:
    """
    Login endpoint - accepts JSON body
    Returns access_token in response
    FIXED: Explicitly convert is_admin to boolean
    """
    try:
        print(f"\n[API] 🚨 Login endpoint called")
        print(f"[API] Email: {data.email}")
        
        if not data.email or not data.password:
            print(f"[API] ❌ Missing email or password")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        service = AuthService(db)
        user, token = await service.login(data.email, data.password)
        
        print(f"[API] ✅ Login successful for {user.email}")
        print(f"[API] User is_admin (DB): {user.is_admin} (type: {type(user.is_admin)})")
        
        # FIXED: Explicitly convert is_admin to boolean
        # If is_admin is None or False, return False
        # If is_admin is True (1 in SQLite), return True
        is_admin_value = bool(user.is_admin) if user.is_admin is not None else False
        print(f"[API] User is_admin (converted): {is_admin_value}")
        
        # Set cookie as backup
        response.set_cookie("access_token", token, httponly=True, max_age=1800)
        
        return {
            "access_token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "is_admin": is_admin_value,
            }
        }
    except ValueError as e:
        print(f"[API] ❌ Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] ❌ Login error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed: " + str(e)
        )


@router.get("/me")
async def get_me(db: DBDep, current_user: UserModel = Depends(get_current_user)) -> dict:
    """Get current authenticated user"""
    try:
        print(f"[API] 📁 Getting current user")
        is_admin_value = bool(current_user.is_admin) if current_user.is_admin is not None else False
        return {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "is_admin": is_admin_value,
        }
    except Exception as e:
        print(f"[API] ❌ Get me error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get current user"
        )


@router.get("/users/{user_id}")
async def get_user(db: DBDep, user_id: int) -> dict:
    """Get user by ID with profile statistics"""
    try:
        print(f"[API] 👤 Getting user {user_id}")
        service = AuthService(db)
        user = await service.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        is_admin_value = bool(user.is_admin) if user.is_admin is not None else False
        
        # Get user statistics
        posts_count = db.query(func.count(PostModel.id)).filter(PostModel.user_id == user_id).scalar() or 0
        friends_count = db.query(func.count(FriendshipModel.id)).filter(
            ((FriendshipModel.user_id == user_id) | (FriendshipModel.friend_id == user_id))
        ).scalar() or 0
        likes_count = db.query(func.count(LikeModel.id)).filter(LikeModel.user_id == user_id).scalar() or 0
        
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_admin": is_admin_value,
            "posts_count": posts_count,
            "friends_count": friends_count,
            "likes_count": likes_count,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] ❌ Get user error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user: " + str(e)
        )


@router.get("/users")
async def get_all_users(db: DBDep) -> list:
    """Get all users"""
    try:
        print(f"[API] 👫 Getting all users")
        service = AuthService(db)
        users = await service.get_all_users()
        return [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "is_admin": bool(user.is_admin) if user.is_admin is not None else False,
            }
            for user in (users or [])
        ]
    except Exception as e:
        print(f"[API] ❌ Get users error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )


@router.get("/friends")
async def get_friends(db: DBDep, current_user: UserModel = Depends(get_current_user)) -> list:
    """Get list of friends for current user"""
    try:
        print(f"[API] 👫 Getting friends for user {current_user.id}")
        
        # Get all friendships where current user is involved
        friendships = db.query(FriendshipModel).filter(
            (FriendshipModel.user_id == current_user.id) | (FriendshipModel.friend_id == current_user.id)
        ).all()
        
        friends = []
        for friendship in friendships:
            # Get the friend's ID (the other person in the friendship)
            friend_id = friendship.friend_id if friendship.user_id == current_user.id else friendship.user_id
            friend = db.query(UserModel).filter(UserModel.id == friend_id).first()
            if friend:
                friends.append({
                    "id": friend.id,
                    "name": friend.name,
                    "email": friend.email,
                    "is_admin": bool(friend.is_admin) if friend.is_admin is not None else False,
                })
        
        return friends
    except Exception as e:
        print(f"[API] ❌ Get friends error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get friends"
        )


@router.post("/users/{user_id}/friend")
async def add_friend(db: DBDep, user_id: int, current_user: UserModel = Depends(get_current_user)) -> dict:
    """Add a friend"""
    try:
        print(f"[API] ➕ Adding friend {user_id} for user {current_user.id}")
        
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot add yourself as a friend"
            )
        
        # Check if user exists
        friend = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not friend:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if friendship already exists
        existing = db.query(FriendshipModel).filter(
            ((FriendshipModel.user_id == current_user.id) & (FriendshipModel.friend_id == user_id)) |
            ((FriendshipModel.user_id == user_id) & (FriendshipModel.friend_id == current_user.id))
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already friends"
            )
        
        # Create friendship
        friendship = FriendshipModel(user_id=current_user.id, friend_id=user_id)
        db.add(friendship)
        db.commit()
        
        return {"status": "OK", "message": "Friend added successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"[API] ❌ Add friend error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add friend"
        )


@router.delete("/users/{user_id}/friend")
async def remove_friend(db: DBDep, user_id: int, current_user: UserModel = Depends(get_current_user)) -> dict:
    """Remove a friend"""
    try:
        print(f"[API] ➖ Removing friend {user_id} for user {current_user.id}")
        
        # Find and delete friendship
        friendship = db.query(FriendshipModel).filter(
            ((FriendshipModel.user_id == current_user.id) & (FriendshipModel.friend_id == user_id)) |
            ((FriendshipModel.user_id == user_id) & (FriendshipModel.friend_id == current_user.id))
        ).first()
        
        if not friendship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Friendship not found"
            )
        
        db.delete(friendship)
        db.commit()
        
        return {"status": "OK", "message": "Friend removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"[API] ❌ Remove friend error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove friend"
        )


@router.post("/logout")
async def logout(response: Response) -> dict:
    """Logout and clear authentication cookie"""
    try:
        response.delete_cookie("access_token")
        print(f"[API] 🚴 User logged out")
        return {"status": "OK", "message": "Logged out successfully"}
    except Exception as e:
        print(f"[API] ❌ Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )
