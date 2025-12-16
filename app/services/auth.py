from datetime import datetime, timezone, timedelta
import jwt
from passlib.context import CryptContext

from app.config import settings
from app.exceptions.auth import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidPasswordError,
    InvalidJWTTokenError,
    JWTTokenExpiredError,
)
from app.schemes.users import SUserAdd, SUserAddRequest, SUserAuth
from app.schemes.roles import SRoleAdd
from app.services.base import BaseService


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def create_access_token(cls, data: dict) -> str:
        to_encode = data.copy()
        expire: datetime = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode["exp"] = expire.timestamp()
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
        return encoded_jwt

    @classmethod
    def verify_password(cls, plain_password, hashed_password) -> bool:
        try:
            return cls.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            print(f"[AUTH] Password verification error: {e}")
            return False

    @classmethod
    def hash_password(cls, plain_password) -> str:
        return cls.pwd_context.hash(plain_password)

    @classmethod
    def decode_token(cls, token: str) -> dict:
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except jwt.exceptions.DecodeError as ex:
            raise InvalidJWTTokenError from ex
        except jwt.exceptions.ExpiredSignatureError as ex:
            raise JWTTokenExpiredError from ex

    async def ensure_default_role(self):
        """Ensure default role exists"""
        try:
            existing_role = await self.db.roles.get_one_or_none(id=1)
            if not existing_role:
                print("[AUTH] Creating default role")
                role_data = SRoleAdd(name="user", description="Default user role")
                await self.db.roles.add(role_data)
                await self.db.commit()
                print("[AUTH] Default role created")
        except Exception as e:
            print(f"[AUTH] Error ensuring default role: {e}")

    async def register_user(self, user_data: SUserAddRequest):
        try:
            print(f"[AUTH] Starting registration for: {user_data.email}")
            
            # Ensure default role exists
            await self.ensure_default_role()
            
            hashed_password = self.hash_password(user_data.password)
            role_id = user_data.role_id if user_data.role_id else 1
            
            new_user_data = SUserAdd(
                email=user_data.email,
                hashed_password=hashed_password,
                name=user_data.name,
                role_id=role_id,
            )
            
            print(f"[AUTH] Adding user to database")
            user = await self.db.users.add(new_user_data)
            await self.db.commit()
            print(f"[AUTH] User registered successfully: {user.id}")
            return user
            
        except Exception as e:
            print(f"[AUTH] Registration error: {e}")
            raise UserAlreadyExistsError

    async def login_user(self, user_data: SUserAuth) -> str:
        try:
            print(f"[AUTH] Login attempt for: {user_data.email}")
            
            # Get user from database
            user = await self.db.users.get_one_or_none(email=user_data.email)
            
            if not user:
                print(f"[AUTH] User not found: {user_data.email}")
                raise UserNotFoundError
            
            print(f"[AUTH] User found: {user.id}")
            print(f"[AUTH] Verifying password...")
            
            # Verify password
            is_valid = self.verify_password(user_data.password, user.hashed_password)
            
            if not is_valid:
                print(f"[AUTH] Password verification failed")
                raise InvalidPasswordError
            
            print(f"[AUTH] Password verified successfully")
            
            # Create token
            access_token = self.create_access_token({"user_id": user.id})
            print(f"[AUTH] Token created successfully")
            
            return access_token
            
        except (UserNotFoundError, InvalidPasswordError):
            raise
        except Exception as e:
            print(f"[AUTH] Login error: {e}")
            raise UserNotFoundError

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
        return users if users else []

    async def get_me(self, user_id: int):
        user = await self.db.users.get_one_or_none(id=user_id)
        if not user:
            raise UserNotFoundError
        return user
