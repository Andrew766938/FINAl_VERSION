from fastapi import APIRouter, Depends
from starlette.responses import Response

from app.api.dependencies import DBDep, get_current_user
from app.exceptions.auth import (
    UserAlreadyExistsError,
    UserAlreadyExistsHTTPError,
    UserNotFoundError,
    UserNotFoundHTTPError,
    InvalidPasswordError,
    InvalidPasswordHTTPError,
)
from app.schemes.users import SUserAddRequest, SUserAuth
from app.services.auth import AuthService
from app.models.users import UserModel

router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/register", summary="Регистрация нового пользователя")
async def register_user(
    db: DBDep,
    user_data: SUserAddRequest,
) -> dict:
    try:
        print(f"[REGISTER] Registering user: {user_data.email}")
        user = await AuthService(db).register_user(user_data)
        print(f"[REGISTER] User created: {user}")
        
        access_token: str = await AuthService(db).login_user(
            SUserAuth(email=user_data.email, password=user_data.password)
        )
        print(f"[REGISTER] Token created: {access_token[:20]}...")
        
        return {
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.name,
                "email": user.email,
            }
        }
    except UserAlreadyExistsError:
        print(f"[REGISTER] User already exists")
        raise UserAlreadyExistsHTTPError
    except Exception as e:
        print(f"[REGISTER] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise UserAlreadyExistsHTTPError


@router.post("/login", summary="Аутентификация пользователя")
async def login_user(
    db: DBDep,
    response: Response,
    user_data: SUserAuth,
) -> dict:
    try:
        print(f"[LOGIN] Login attempt: {user_data.email}")
        
        # Get user
        user = await AuthService(db).get_user_by_email(user_data.email)
        print(f"[LOGIN] User found: {user}")
        
        # Verify password
        is_valid = AuthService.verify_password(user_data.password, user.hashed_password)
        print(f"[LOGIN] Password valid: {is_valid}")
        
        if not is_valid:
            print(f"[LOGIN] Password mismatch")
            raise InvalidPasswordError
        
        # Create token
        access_token: str = await AuthService(db).login_user(user_data)
        print(f"[LOGIN] Token created successfully")
        
        response.set_cookie("access_token", access_token)
        return {
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.name,
                "email": user.email,
            }
        }
    except UserNotFoundError:
        print(f"[LOGIN] User not found")
        raise UserNotFoundHTTPError
    except InvalidPasswordError:
        print(f"[LOGIN] Invalid password")
        raise InvalidPasswordHTTPError
    except Exception as e:
        print(f"[LOGIN] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise UserNotFoundHTTPError


@router.get("/me", summary="Получение текущего пользователя для профиля")
async def get_me(db: DBDep, current_user: UserModel = Depends(get_current_user)) -> dict:
    return {
        "id": current_user.id,
        "username": current_user.name,
        "email": current_user.email,
    }


@router.get("/users/{user_id}", summary="Получение пользователя по ID")
async def get_user(db: DBDep, user_id: int) -> dict:
    try:
        user = await AuthService(db).get_user(user_id)
    except UserNotFoundError:
        raise UserNotFoundHTTPError
    return {
        "id": user.id,
        "username": user.name,
        "email": user.email,
    }


@router.get("/users", summary="Получение списка всех пользователей")
async def get_all_users(db: DBDep) -> list:
    try:
        users = await AuthService(db).get_all_users()
        return [
            {
                "id": user.id,
                "username": user.name,
                "email": user.email,
            }
            for user in users
        ]
    except Exception as e:
        print(f"Get users error: {e}")
        return []


@router.post("/logout", summary="Выход пользователя из системы")
async def logout(response: Response) -> dict[str, str]:
    response.delete_cookie("access_token")
    return {"status": "OK"}
