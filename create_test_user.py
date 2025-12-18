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
    engine = create_async_engine(settings.get_db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            print("\n📝 Updating admin user...")
            from sqlalchemy import select
            
            # Ensure role exists
            result = await session.execute(select(RoleModel).where(RoleModel.id == 1))
            role = result.scalars().first()
            if not role:
                role = RoleModel(id=1, name="user", description="Default user role")
                session.add(role)
                await session.commit()
            
            # Check if user exists
            result = await session.execute(select(UserModel).where(UserModel.email == "alice@betony.local"))
            user = result.scalars().first()
            
            if user:
                print(f"User alice@betony.local exists (ID: {user.id})")
                if not user.is_admin:
                    user.is_admin = True
                    await session.commit()
                    print("✅ User updated to admin!")
                else:
                    print("✅ User is already admin")
            else:
                hashed_password = AuthService.hash_password("password123")
                new_user = UserModel(
                    name="Alice",
                    email="alice@betony.local",
                    hashed_password=hashed_password,
                    role_id=1,
                    is_admin=True
                )
                session.add(new_user)
                await session.commit()
                print(f"✅ User created: {new_user.id}")
            
            print("\n✅ Done!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await session.close()
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_test_data())
