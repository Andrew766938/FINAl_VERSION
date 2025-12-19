#!/usr/bin/env python3
"""
Initialize the database with test data and admin accounts.
Runs Alembic migrations first, then seeds the database.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.database.database import engine, get_db
from app.models.roles import RoleModel
from app.models.users import UserModel
from app.core.security import get_password_hash
from app.database.base import Base


def print_header(text):
    """Print formatted header."""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)


def print_section(text):
    """Print section header."""
    print(f"\n[{text}]", end=" ")


def init_database():
    """Initialize database with Alembic and test data."""
    
    print_header("BETONY DATABASE INITIALIZATION")
    
    # Step 1: Run Alembic migrations
    print_section("MIGRATIONS")
    print("Running Alembic migrations...")
    
    try:
        import subprocess
        
        # Run alembic upgrade head
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "heads"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"\n⚠️  Warning: Alembic had issues:")
            print(result.stderr)
        else:
            print("✅ Alembic migrations applied successfully")
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if line.strip() and ('✅' in line or 'Running upgrade' in line):
                        print(f"   {line}")
    except subprocess.TimeoutExpired:
        print("❌ Alembic migrations timed out")
        return False
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False
    
    # Step 2: Create tables (if migrations didn't work)
    print_section("DATABASE")
    try:
        with engine.begin() as connection:
            # Try to create tables using SQLAlchemy
            Base.metadata.create_all(engine)
            print("✅ Database tables created")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    # Step 3: Seed test accounts
    print_section("ACCOUNTS")
    print("Creating 3 test accounts...\n")
    
    try:
        with Session(engine) as session:
            # Check if accounts already exist
            existing_admin = session.execute(
                select(UserModel).where(UserModel.email == "admin@betony.local")
            ).first()
            
            if existing_admin:
                print("ℹ️  Test accounts already exist, skipping...")
                print("\nℹ️  Existing accounts:")
                
                # List existing accounts
                users = session.execute(select(UserModel)).scalars().all()
                for user in users:
                    role = "👑 Admin" if user.is_admin else "👤 User"
                    print(f"   {role}: {user.email} (ID: {user.id})")
                
                return True
            
            # Create default role
            existing_role = session.execute(
                select(RoleModel).where(RoleModel.name == "user")
            ).first()
            
            if not existing_role:
                user_role = RoleModel(name="user")
                session.add(user_role)
                session.flush()
            else:
                user_role = existing_role[0]
            
            # Create admin account
            admin = UserModel(
                name="Admin",
                email="admin@betony.local",
                hashed_password=get_password_hash("admin123"),
                is_admin=True,
                role_id=user_role.id
            )
            session.add(admin)
            session.flush()
            print(f"✅ Admin: admin@betony.local (password: admin123) [ID: {admin.id}]")
            
            # Create regular user account
            user = UserModel(
                name="Test User",
                email="test@betony.local",
                hashed_password=get_password_hash("test123"),
                is_admin=False,
                role_id=user_role.id
            )
            session.add(user)
            session.flush()
            print(f"✅ User: test@betony.local (password: test123) [ID: {user.id}]")
            
            # Create guest account (no password)
            guest = UserModel(
                name="Guest",
                email="guest@betony.local",
                hashed_password=get_password_hash("guest_no_login"),
                is_admin=False,
                role_id=user_role.id
            )
            session.add(guest)
            session.flush()
            print(f"✅ Guest: guest@betony.local (no password needed)\n")
            
            session.commit()
            print("✅ All accounts created successfully!")
            
    except Exception as e:
        print(f"❌ Error creating accounts: {e}")
        return False
    
    # Step 4: Print credentials
    print("\n" + "="*80)
    print("ACCOUNT CREDENTIALS:")
    print("="*80)
    print("""
1️⃣  ADMIN ACCOUNT (Full privileges)
   Email: admin@betony.local
   Password: admin123

2️⃣  REGULAR USER ACCOUNT (Normal user)
   Email: test@betony.local
   Password: test123

3️⃣  GUEST MODE (No login needed)
   Click: 'Гостевой режим' button on login
""")
    print("="*80)
    print("\n✅ Database initialization complete!\n")
    
    return True


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
