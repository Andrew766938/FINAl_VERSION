from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from starlette.responses import Response
import traceback
import json

from app.api.dependencies import DBDep, get_current_user
from app.models.users import UserModel
from app.services.auth import AuthService
from app.schemes.users import SUserAddRequest  # Импортируем валидированную схему

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
                "username": user.name,
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
                "username": user.name,
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
            "username": current_user.name,
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
    """Get user by ID"""
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
        return {
            "id": user.id,
            "username": user.name,
            "email": user.email,
            "is_admin": is_admin_value,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] ❌ Get user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user"
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
                "username": user.name,
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
