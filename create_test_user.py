#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, '.')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.users import UserModel
from app.models.roles import RoleModel
from app.services.auth import AuthService

async def create_test_data():
    # Create async engine
    engine = create_async_engine(settings.get_db_url, echo=False)
    
    # Create session factory
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            print("\n📝 Creating test data...")
            
            # Ensure role exists
            from sqlalchemy import select
            result = await session.execute(select(RoleModel).where(RoleModel.id == 1))
            role = result.scalars().first()
            if not role:
                print("📦 Creating default role...")
                role = RoleModel(id=1, name="user", description="Default user role")
                session.add(role)
                await session.commit()
                print("✅ Role created")
            
            # Check if user exists
            result = await session.execute(
                select(UserModel).where(UserModel.email == "alice@betony.local")
            )
            user = result.scalars().first()
            
            if user:
                print(f"⚠️  User alice@betony.local already exists (ID: {user.id})")
                if not user.is_admin:
                    print(f"    Updating to admin...")
                    user.is_admin = True
                    await session.commit()
                    print(f"    ✅ User is now admin")
                else:
                    print(f"    ✅ User is already admin")
            else:
                print("👤 Creating user alice@betony.local...")
                hashed_password = AuthService.hash_password("password123")
                new_user = UserModel(
                    name="Alice",
                    email="alice@betony.local",
                    hashed_password=hashed_password,
                    role_id=1,
                    is_admin=True  # SET AS ADMIN
                )
                session.add(new_user)
                await session.commit()
                print(f"✅ User created (ID: {new_user.id}, is_admin: True)")
            
            print("\n✅ Test data ready!")
            print("📧 Email: alice@betony.local")
            print("🔑 Password: password123")
            print("👑 Role: ADMIN")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await session.close()
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_test_data())
