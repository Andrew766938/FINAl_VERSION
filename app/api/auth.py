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
        user = await AuthService(db).register_user(user_data)
        access_token: str = await AuthService(db).login_user(
            SUserAuth(email=user_data.email, password=user_data.password)
        )
        return {
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.name,
                "email": user.email,
            }
        }
    except UserAlreadyExistsError:
        raise UserAlreadyExistsHTTPError
    except Exception as e:
        print(f"Register error: {e}")
        raise UserAlreadyExistsHTTPError


@router.post("/login", summary="Аутентификация пользователя")
async def login_user(
    db: DBDep,
    response: Response,
    user_data: SUserAuth,
) -> dict:
    try:
        access_token: str = await AuthService(db).login_user(user_data)
        user = await AuthService(db).get_user_by_email(user_data.email)
    except UserNotFoundError:
        raise UserNotFoundHTTPError
    except InvalidPasswordError:
        raise InvalidPasswordHTTPError
    except Exception as e:
        print(f"Login error: {e}")
        raise UserNotFoundHTTPError
    
    response.set_cookie("access_token", access_token)
    return {
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.name,
            "email": user.email,
        }
    }


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
