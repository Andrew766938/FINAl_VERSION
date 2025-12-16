import jwt
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext

from app.config import settings
from app.models.users import UserModel
from app.models.roles import RoleModel
from app.services.base import BaseService
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def hash_password(cls, password: str) -> str:
        return cls.pwd_context.hash(password)

    @classmethod
    def verify_password(cls, password: str, hashed: str) -> bool:
        try:
            return cls.pwd_context.verify(password, hashed)
        except:
            return False

    @classmethod
    def create_token(cls, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"user_id": user_id, "exp": expire.timestamp()}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @classmethod
    def verify_token(cls, token: str) -> int:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload["user_id"]
        except:
            return None

    async def ensure_role(self):
        """Ensure default role exists"""
        try:
            result = await self.db.session.execute(select(RoleModel).where(RoleModel.id == 1))
            role = result.scalars().first()
            if not role:
                print("[AUTH] Creating default role")
                role = RoleModel(id=1, name="user", description="Default user role")
                self.db.session.add(role)
                await self.db.commit()
                print("[AUTH] Default role created")
        except Exception as e:
            print(f"[AUTH] Error ensuring role: {e}")

    async def register_and_login(self, email: str, password: str, name: str):
        """
        Register user and return user + token
        """
        try:
            print(f"[AUTH] Registering: {email}")
            
            # Ensure role exists
            await self.ensure_role()
            
            # Check if user exists
            result = await self.db.session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            existing = result.scalars().first()
            if existing:
                raise ValueError(f"User {email} already exists")
            
            # Create user
            hashed = self.hash_password(password)
            user = UserModel(
                name=name,
                email=email,
                hashed_password=hashed,
                role_id=1
            )
            self.db.session.add(user)
            await self.db.commit()
            
            print(f"[AUTH] User registered: {user.id}")
            
            # Create token
            token = self.create_token(user.id)
            print(f"[AUTH] Token created")
            
            return user, token
        except IntegrityError as e:
            print(f"[AUTH] Integrity error: {e}")
            raise ValueError("User already exists")
        except Exception as e:
            print(f"[AUTH] Registration error: {e}")
            import traceback
            traceback.print_exc()
            raise

    async def login(self, email: str, password: str):
        """
        Login user and return user + token
        """
        try:
            print(f"[AUTH] Login: {email}")
            
            # Get user
            result = await self.db.session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            user = result.scalars().first()
            
            if not user:
                print(f"[AUTH] User not found: {email}")
                raise ValueError("Invalid email or password")
            
            # Verify password
            if not self.verify_password(password, user.hashed_password):
                print(f"[AUTH] Password incorrect for {email}")
                raise ValueError("Invalid email or password")
            
            # Create token
            token = self.create_token(user.id)
            print(f"[AUTH] Login successful")
            
            return user, token
        except ValueError:
            raise
        except Exception as e:
            print(f"[AUTH] Login error: {e}")
            import traceback
            traceback.print_exc()
            raise ValueError("Login failed")

    async def get_user(self, user_id: int):
        result = await self.db.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        return result.scalars().first()

    async def get_all_users(self):
        result = await self.db.session.execute(select(UserModel))
        return result.scalars().all()
