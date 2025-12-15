#!/usr/bin/env python3
"""
Fix All Script - Automatically fixes all issues in the project
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from app.database.database import Base
from app.config import settings

# Import all models to register them
from app.models.users import UserModel
from app.models.roles import RoleModel
from app.models.posts import PostModel
from app.models.comments import CommentModel
from app.models.likes import LikeModel
from app.models.friendships import FriendshipModel


async def init_database():
    """
    Initialize database - create all tables
    """
    print("Creating database tables...")
    
    # Create async engine
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{settings.DB_NAME}",
        echo=True
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Drop existing
        await conn.run_sync(Base.metadata.create_all)  # Create new
    
    print("✅ Database tables created successfully!")
    
    await engine.dispose()


if __name__ == "__main__":
    print("=" * 50)
    print("🔧 FIXING ALL ISSUES")
    print("=" * 50)
    
    try:
        asyncio.run(init_database())
        print("\n✅ All fixes applied successfully!")
        print("\nNow run: uvicorn main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
