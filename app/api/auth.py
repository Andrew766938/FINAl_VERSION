from fastapi import APIRouter, Depends
from starlette.responses import Response
import traceback

from app.api.dependencies import DBDep, get_current_user
from app.models.users import UserModel
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register_user(db: DBDep, email: str, password: str, name: str) -> dict:
    """
    Simple registration endpoint
    """
    try:
        print(f"\n[API] Register endpoint called")
        print(f"[API] Email: {email}, Name: {name}")
        
        service = AuthService(db)
        user, token = await service.register_and_login(email, password, name)
        
        print(f"[API] Registration successful, returning token")
        return {
            "access_token": token,
            "user": {
                "id": user.id,
                "username": user.name,
                "email": user.email,
            }
        }
    except ValueError as e:
        print(f"[API] Validation error: {e}")
        return {"error": str(e)}, 400
    except Exception as e:
        print(f"[API] Registration error: {e}")
        traceback.print_exc()
        return {"error": "Registration failed"}, 500


@router.post("/login")
async def login_user(db: DBDep, response: Response, email: str, password: str) -> dict:
    """
    Simple login endpoint
    """
    try:
        print(f"\n[API] Login endpoint called")
        print(f"[API] Email: {email}")
        
        service = AuthService(db)
        user, token = await service.login(email, password)
        
        print(f"[API] Login successful")
        response.set_cookie("access_token", token)
        return {
            "access_token": token,
            "user": {
                "id": user.id,
                "username": user.name,
                "email": user.email,
            }
        }
    except ValueError as e:
        print(f"[API] Validation error: {e}")
        return {"error": str(e)}, 401
    except Exception as e:
        print(f"[API] Login error: {e}")
        traceback.print_exc()
        return {"error": "Login failed"}, 500


@router.get("/me")
async def get_me(db: DBDep, current_user: UserModel = Depends(get_current_user)) -> dict:
    return {
        "id": current_user.id,
        "username": current_user.name,
        "email": current_user.email,
    }


@router.get("/users/{user_id}")
async def get_user(db: DBDep, user_id: int) -> dict:
    try:
        service = AuthService(db)
        user = await service.get_user(user_id)
        return {
            "id": user.id,
            "username": user.name,
            "email": user.email,
        }
    except:
        return {"error": "User not found"}, 404


@router.get("/users")
async def get_all_users(db: DBDep) -> list:
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
        print(f"[API] Get users error: {e}")
        return []


@router.post("/logout")
async def logout(response: Response) -> dict:
    response.delete_cookie("access_token")
    return {"status": "OK"}
