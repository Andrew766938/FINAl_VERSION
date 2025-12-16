from datetime import datetime, timezone, timedelta

from app.config import settings
from app.exceptions.auth import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidPasswordError,
    InvalidJWTTokenError,
    JWTTokenExpiredError,
)
from app.exceptions.base import ObjectAlreadyExistsError
from app.schemes.users import (
    SUserAdd,
    SUserAddRequest,
    SUserAuth,
)
from app.schemes.roles import SRoleAdd
from app.schemes.relations_users_roles import SUserGetWithRels
from app.services.base import BaseService
import jwt
from passlib.context import CryptContext


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def create_access_token(cls, data: dict) -> str:
        to_encode = data.copy()
        expire: datetime = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode |= {"exp": expire}
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
        return encoded_jwt

    @classmethod
    def verify_password(cls, plain_password, hashed_password) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def hash_password(cls, plain_password) -> str:
        return cls.pwd_context.hash(plain_password)

    @classmethod
    def decode_token(cls, token: str) -> dict:
        try:
            return jwt.decode(token, settings.SECRET_KEY, [settings.ALGORITHM])
        except jwt.exceptions.DecodeError as ex:
            raise InvalidJWTTokenError from ex
        except jwt.exceptions.ExpiredSignatureError as ex:
            raise JWTTokenExpiredError from ex

    async def ensure_default_role(self):
        """Ensure default role exists"""
        try:
            existing_role = await self.db.roles.get_one_or_none(id=1)
            if not existing_role:
                role_data = SRoleAdd(name="user", description="Default user role")
                await self.db.roles.add(role_data)
                await self.db.commit()
        except Exception as e:
            print(f"Error ensuring default role: {e}")

    async def register_user(self, user_data: SUserAddRequest):
        try:
            # Ensure default role exists
            await self.ensure_default_role()
            
            hashed_password: str = self.hash_password(user_data.password)
            role_id = user_data.role_id if user_data.role_id else 1
            
            new_user_data = SUserAdd(
                email=user_data.email,
                hashed_password=hashed_password,
                name=user_data.name,
                role_id=role_id,
            )
            user = await self.db.users.add(new_user_data)
            await self.db.commit()
            return user
        except Exception as e:
            print(f"Registration error: {e}")
            raise UserAlreadyExistsError

    async def login_user(self, user_data: SUserAuth):
        try:
            user = await self.db.users.get_one_or_none(email=user_data.email)
        except:
            # Fallback if get_one_or_none_with_role doesn't exist
            user = await self.db.users.get_one_or_none(email=user_data.email)
        
        if not user:
            raise UserNotFoundError
        if not self.verify_password(user_data.password, user.hashed_password):
            raise InvalidPasswordError
        access_token: str = self.create_access_token(
            {"user_id": user.id}
        )
        return access_token

    async def get_user(self, user_id: int):
        user = await self.db.users.get_one_or_none(id=user_id)
        if not user:
            raise UserNotFoundError
        return user

    async def get_user_by_email(self, email: str):
        user = await self.db.users.get_one_or_none(email=email)
        if not user:
            raise UserNotFoundError
        return user

    async def get_all_users(self):
        users = await self.db.users.get_all()
        return users

    async def get_me(self, user_id: int):
        user = await self.db.users.get_one_or_none(id=user_id)
        if not user:
            raise UserNotFoundError
        return user
