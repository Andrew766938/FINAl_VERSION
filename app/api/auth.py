from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from starlette.responses import Response
import traceback

from app.api.dependencies import DBDep, get_current_user
from app.models.users import UserModel
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

# Pydantic моделиы для валидации
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    db: DBDep,
    data: RegisterRequest
) -> dict:
    """
    Registration endpoint - accepts JSON body
    """
    try:
        print(f"\n[API] Register endpoint called")
        print(f"[API] Email: {data.email}, Name: {data.name}")
        
        if not data.email or not data.password or not data.name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email, password, and name are required"
            )
        
        service = AuthService(db)
        user, token = await service.register_and_login(data.email, data.password, data.name)
        
        print(f"[API] ✅ Registration successful")
        return {
            "access_token": token,
            "user": {
                "id": user.id,
                "username": user.name,
                "email": user.email,
            }
        }
    except ValueError as e:
        print(f"[API] ❌ Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
    """
    try:
        print(f"\n[API] Login endpoint called")
        print(f"[API] Email: {data.email}")
        
        if not data.email or not data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        service = AuthService(db)
        user, token = await service.login(data.email, data.password)
        
        print(f"[API] ✅ Login successful for user: {user.email}")
        response.set_cookie("access_token", token, httponly=True)
        return {
            "access_token": token,
            "user": {
                "id": user.id,
                "username": user.name,
                "email": user.email,
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
        return {
            "id": current_user.id,
            "username": current_user.name,
            "email": current_user.email,
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
        service = AuthService(db)
        user = await service.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {
            "id": user.id,
            "username": user.name,
            "email": user.email,
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
        service = AuthService(db)
        users = await service.get_all_users()
        return [
            {
                "id": user.id,
                "username": user.name,
                "email": user.email,
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
        return {"status": "OK", "message": "Logged out successfully"}
    except Exception as e:
        print(f"[API] ❌ Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )
