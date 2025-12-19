#!/usr/bin/env python3
"""
Initialize database with exactly 3 test accounts:
1. Admin account
2. Regular user account  
3. Guest mode (no real account needed, but info for reference)

Usage: python init_db.py
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.users import UserModel
from app.models.posts import PostModel
from app.models.comments import CommentModel
from app.models.likes import LikeModel
from app.models.friends import FriendModel
from app.database.base import Base
from app.config import settings
from app.utils.security import hash_password

async def init_database():
    """Initialize database with test data"""
    
    # Create engine
    engine = create_async_engine(settings.get_db_url, echo=False)
    
    print("\n[DATABASE] Initializing database...\n")
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("[DROP] Dropped all tables")
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("[CREATE] Created all tables")
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # ===== CREATE ACCOUNTS =====
        print("\n[ACCOUNTS] Creating 3 test accounts...\n")
        
        # 1. ADMIN account
        admin = UserModel(
            name="Администратор",
            email="admin@betony.local",
            hashed_password=hash_password("admin123"),
            is_admin=True
        )
        session.add(admin)
        await session.flush()  # Get ID
        print(f"✅ Admin: admin@betony.local (password: admin123) [ID: {admin.id}]")
        
        # 2. REGULAR USER account
        user = UserModel(
            name="Тестовый Пользователь",
            email="test@betony.local",
            hashed_password=hash_password("test123"),
            is_admin=False
        )
        session.add(user)
        await session.flush()  # Get ID
        print(f"✅ User: test@betony.local (password: test123) [ID: {user.id}]")
        
        # 3. GUEST MODE (info only - no real account in DB)
        print(f"✅ Guest: guest@betony.local (no password needed, use 'Guest Mode' button)\n")
        
        # Commit accounts
        await session.commit()
        
        print("[SUCCESS] All accounts created successfully!\n")
        print("═" * 60)
        print("ACCOUNT CREDENTIALS:")
        print("═" * 60)
        print("\n1️⃣  ADMIN ACCOUNT (Full privileges)")
        print("   Email: admin@betony.local")
        print("   Password: admin123")
        print("   Can: Delete any posts/comments, see admin features")
        print("\n2️⃣  REGULAR USER ACCOUNT (Normal user)")
        print("   Email: test@betony.local")
        print("   Password: test123")
        print("   Can: Create posts, comment, like, manage own content")
        print("\n3️⃣  GUEST MODE (No login needed)")
        print("   Click: 'Гостевой режим' button on login page")
        print("   Can: View posts and comments (read-only)")
        print("\n" + "═" * 60)
        print("\nDatabase initialized! You can now start the app.\n")
    
    await engine.dispose()

if __name__ == "__main__":
    print("\n" + "█" * 60)
    print("  BETONY DATABASE INITIALIZATION")
    print("█" * 60)
    
    asyncio.run(init_database())
