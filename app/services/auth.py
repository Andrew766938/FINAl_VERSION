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
        """Create JWT token"""
        try:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            payload = {"user_id": user_id, "exp": expire.timestamp()}
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
            print(f"[TOKEN] ✅ Token created for user_id: {user_id}")
            return token
        except Exception as e:
            print(f"[TOKEN] ❌ Error creating token: {e}")
            raise

    @classmethod
    def verify_token(cls, token: str) -> int:
        """Verify JWT token and return user_id"""
        try:
            print(f"[TOKEN] Verifying token...")
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("user_id")
            print(f"[TOKEN] ✅ Token verified, user_id: {user_id}")
            return user_id
        except jwt.ExpiredSignatureError:
            print(f"[TOKEN] ❌ Token expired")
            return None
        except jwt.InvalidTokenError as e:
            print(f"[TOKEN] ❌ Invalid token: {e}")
            return None
        except Exception as e:
            print(f"[TOKEN] ❌ Error verifying token: {e}")
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
                print("[AUTH] ✅ Default role created")
        except Exception as e:
            print(f"[AUTH] Error ensuring role: {e}")

    async def count_users(self) -> int:
        """Count total users in database"""
        try:
            result = await self.db.session.execute(select(UserModel))
            users = result.scalars().all()
            return len(users) if users else 0
        except Exception as e:
            print(f"[AUTH] Error counting users: {e}")
            return 0

    async def register_and_login(self, email: str, password: str, name: str):
        """
        Register user and return user + token
        First user becomes admin automatically
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
            
            # Count existing users - first user becomes admin
            user_count = await self.count_users()
            is_admin = user_count == 0
            
            # Create user
            hashed = self.hash_password(password)
            user = UserModel(
                name=name,
                email=email,
                hashed_password=hashed,
                role_id=1,
                is_admin=is_admin
            )
            self.db.session.add(user)
            await self.db.commit()
            
            print(f"[AUTH] ✅ User registered: {user.id}, is_admin: {is_admin}")
            
            # Create token
            token = self.create_token(user.id)
            
            return user, token
        except IntegrityError as e:
            print(f"[AUTH] Integrity error: {e}")
            raise ValueError("User already exists")
        except Exception as e:
            print(f"[AUTH] ❌ Registration error: {e}")
            import traceback
            traceback.print_exc()
            raise

    async def login(self, email: str, password: str):
        """
        Login user and return user + token
        """
        try:
            print(f"[AUTH] Login attempt: {email}")
            
            # Get user
            result = await self.db.session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            user = result.scalars().first()
            
            if not user:
                print(f"[AUTH] ❌ User not found: {email}")
                raise ValueError("Invalid email or password")
            
            # Verify password
            if not self.verify_password(password, user.hashed_password):
                print(f"[AUTH] ❌ Password incorrect for {email}")
                raise ValueError("Invalid email or password")
            
            # Create token
            token = self.create_token(user.id)
            print(f"[AUTH] ✅ Login successful for {email}")
            print(f"[AUTH] User is_admin: {user.is_admin}")
            
            return user, token
        except ValueError:
            raise
        except Exception as e:
            print(f"[AUTH] ❌ Login error: {e}")
            import traceback
            traceback.print_exc()
            raise ValueError("Login failed")

    async def get_user(self, user_id: int):
        """Get user by ID"""
        try:
            result = await self.db.session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            return result.scalars().first()
        except Exception as e:
            print(f"[AUTH] Error getting user: {e}")
            return None

    async def get_all_users(self):
        """Get all users"""
        try:
            result = await self.db.session.execute(select(UserModel))
            return result.scalars().all()
        except Exception as e:
            print(f"[AUTH] Error getting users: {e}")
            return []
