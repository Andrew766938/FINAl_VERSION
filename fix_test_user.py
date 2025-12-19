#!/usr/bin/env python3
"""
Quick fix script: Make test@betony.local a regular user (NOT admin)

Usage: python fix_test_user.py
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update
from app.models.users import UserModel
from app.config import settings

async def fix_test_user():
    """Set test@betony.local to be a regular user (is_admin = False)"""
    
    # Create engine
    engine = create_async_engine(settings.get_db_url, echo=False)
    
    # Create session
    async_session = sessionmaker(engine, class_=sessionmaker, expire_on_commit=False)
    
    async with engine.begin() as conn:
        # Try to update is_admin for test user
        try:
            async_session_maker = sessionmaker(engine, expire_on_commit=False)
            async with async_session_maker() as session:
                # Find test user
                result = await session.execute(
                    select(UserModel).where(UserModel.email == "test@betony.local")
                )
                test_user = result.scalars().first()
                
                if test_user:
                    print(f"Found test user: {test_user.name} (ID: {test_user.id})")
                    print(f"Current is_admin value: {test_user.is_admin}")
                    
                    # Set to regular user
                    test_user.is_admin = False
                    await session.commit()
                    
                    print(f"✅ Updated! test@betony.local is now a REGULAR USER (is_admin = False)")
                else:
                    print("❌ test@betony.local user not found in database")
                    print("   Hint: The database may need to be recreated")
        except Exception as e:
            print(f"❌ Error updating user: {e}")
            import traceback
            traceback.print_exc()
    
    await engine.dispose()

if __name__ == "__main__":
    print("\n[FIX] Setting test@betony.local as REGULAR USER...\n")
    asyncio.run(fix_test_user())
    print("\n[DONE] You can now start the app!\n")
