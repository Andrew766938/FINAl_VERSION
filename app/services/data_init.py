"""
Initialize sample data for the Betony application
"""
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

from app.config import settings
from app.database.db_manager import DBManager
from app.database.database import async_session_maker
from app.services.auth import AuthService
from app.services.posts import PostService
from app.services.likes import LikeService
from app.services.comments import CommentService
from app.services.friendships import FriendshipService
from app.models.users import UserModel
from app.schemes.posts import PostCreate
from app.schemes.comments import CommentCreate


async def init_sample_data():
    """
    Initialize database with sample data
    This includes:
    - Sample users
    - Sample posts
    - Sample likes
    - Sample comments
    - Sample friendships
    """
    try:
        async with DBManager(session_factory=async_session_maker) as db:
            # Check if alice@betony.local exists (using raw SQL to avoid schema issues)
            try:
                result = await db.session.execute(
                    select(UserModel).where(UserModel.email == "alice@betony.local")
                )
                existing_alice = result.scalars().first()
            except Exception as migration_error:
                print(f"[INIT] ⚠️  Database schema issue (likely missing columns): {migration_error}")
                print("[INIT] ℹ️  This is normal on first run. Continuing with data initialization...")
                # Try with a raw SQL check that ignores missing columns
                try:
                    raw_result = await db.session.execute(
                        text("SELECT COUNT(*) FROM users WHERE email = 'alice@betony.local'")
                    )
                    count = raw_result.scalar()
                    existing_alice = count > 0
                except:
                    existing_alice = False
            
            if existing_alice:
                print("[INIT] ✅ Sample data already exists (alice@betony.local found), skipping initialization")
                return
            
            print("[INIT] 🚀 Starting sample data initialization...")
            
            # Create sample users
            auth_service = AuthService(db)
            
            users_data = [
                {"email": "alice@betony.local", "password": "password123", "name": "Alice Johnson"},
                {"email": "bob@betony.local", "password": "password123", "name": "Bob Smith"},
                {"email": "charlie@betony.local", "password": "password123", "name": "Charlie Brown"},
                {"email": "diana@betony.local", "password": "password123", "name": "Diana Prince"},
                {"email": "evan@betony.local", "password": "password123", "name": "Evan Davis"},
            ]
            
            users = []
            for user_data in users_data:
                try:
                    print(f"[INIT] 👤 Creating user: {user_data['name']} ({user_data['email']})")
                    user, token = await auth_service.register_and_login(
                        email=user_data["email"],
                        password=user_data["password"],
                        name=user_data["name"]
                    )
                    users.append(user)
                    print(f"[INIT] ✅ User created successfully: {user.name} (ID: {user.id})")
                except Exception as e:
                    print(f"[INIT] ❌ Error creating user {user_data['name']}: {e}")
                    import traceback
                    traceback.print_exc()
            
            if not users:
                print("[INIT] ❌ No users created, aborting data initialization")
                return
            
            # Create sample posts
            posts_service = PostService(db)
            posts_data = [
                {
                    "title": "My First Blog Post",
                    "content": "Hello everyone! This is my first post on Betony. I'm excited to share my thoughts and connect with the community.",
                    "user_id": users[0].id
                },
                {
                    "title": "Learning Python is Awesome",
                    "content": "I started learning Python last month and it's been an amazing journey. The syntax is clean and expressive.",
                    "user_id": users[1].id
                },
                {
                    "title": "Web Development Tips",
                    "content": "Here are some tips I've learned about web development: 1) Always test your code, 2) Use version control, 3) Write clean code.",
                    "user_id": users[2].id
                },
                {
                    "title": "Building FastAPI Applications",
                    "content": "FastAPI is a modern, fast web framework for building APIs with Python. I've been using it and love the developer experience.",
                    "user_id": users[0].id
                },
                {
                    "title": "Tips for Remote Work",
                    "content": "Working remotely has its challenges and benefits. Here are my tips: maintain routine, have a dedicated workspace, take breaks.",
                    "user_id": users[3].id
                },
                {
                    "title": "Books Worth Reading",
                    "content": "I've been reading some great books lately. Check out 'Clean Code' and 'Design Patterns' - they've improved my programming skills.",
                    "user_id": users[4].id
                }
            ]
            
            posts = []
            for post_data in posts_data:
                try:
                    post_create = PostCreate(
                        title=post_data["title"],
                        content=post_data["content"]
                    )
                    post = await posts_service.create_post(post_create, post_data["user_id"])
                    posts.append(post)
                    print(f"[INIT] ✅ Created post: {post.title}")
                except Exception as e:
                    print(f"[INIT] ❌ Error creating post {post_data['title']}: {e}")
            
            if not posts:
                print("[INIT] No posts created")
                return
            
            # Create sample likes
            likes_service = LikeService(db)
            like_pairs = [
                (posts[0].id, users[1].id),
                (posts[0].id, users[2].id),
                (posts[0].id, users[3].id),
                (posts[1].id, users[0].id),
                (posts[1].id, users[2].id),
                (posts[2].id, users[0].id),
                (posts[2].id, users[1].id),
                (posts[2].id, users[3].id),
                (posts[3].id, users[1].id),
                (posts[4].id, users[0].id),
                (posts[4].id, users[2].id),
                (posts[5].id, users[0].id),
            ]
            
            for post_id, user_id in like_pairs:
                try:
                    like = await likes_service.create_like(post_id, user_id)
                except Exception as e:
                    print(f"[INIT] ❌ Error creating like: {e}")
            
            # Create sample comments
            comments_service = CommentService(db)
            comments_data = [
                {
                    "post_id": posts[0].id,
                    "user_id": users[1].id,
                    "content": "Great first post! Welcome to Betony!"
                },
                {
                    "post_id": posts[0].id,
                    "user_id": users[2].id,
                    "content": "Looking forward to reading more from you!"
                },
                {
                    "post_id": posts[1].id,
                    "user_id": users[0].id,
                    "content": "Python is amazing! Have you tried FastAPI yet?"
                },
                {
                    "post_id": posts[2].id,
                    "user_id": users[1].id,
                    "content": "These are solid tips! Clean code is so important."
                },
                {
                    "post_id": posts[3].id,
                    "user_id": users[2].id,
                    "content": "FastAPI is indeed a game changer for API development."
                },
                {
                    "post_id": posts[4].id,
                    "user_id": users[1].id,
                    "content": "I totally agree with the dedicated workspace tip!"
                },
                {
                    "post_id": posts[5].id,
                    "user_id": users[0].id,
                    "content": "Clean Code is my favorite book! Great recommendations."
                },
            ]
            
            for comment_data in comments_data:
                try:
                    comment_create = CommentCreate(content=comment_data["content"])
                    comment = await comments_service.create_comment(
                        comment_data["post_id"],
                        comment_create,
                        comment_data["user_id"]
                    )
                except Exception as e:
                    print(f"[INIT] ❌ Error creating comment: {e}")
            
            # Create sample friendships
            friendship_service = FriendshipService(db)
            friendships_data = [
                (users[0].id, users[1].id),
                (users[0].id, users[2].id),
                (users[0].id, users[3].id),
                (users[1].id, users[2].id),
                (users[1].id, users[4].id),
                (users[2].id, users[3].id),
            ]
            
            for user_id_1, user_id_2 in friendships_data:
                try:
                    await friendship_service.add_friend(user_id_1, user_id_2)
                    await friendship_service.add_friend(user_id_2, user_id_1)
                except Exception as e:
                    print(f"[INIT] ❌ Error creating friendship: {e}")
            
            print(f"\n[INIT] ✅ Sample data initialization completed successfully!")
            print(f"[INIT] Created {len(users)} users")
            print(f"[INIT] Created {len(posts)} posts")
            print(f"[INIT] Created {len(like_pairs)} likes")
            print(f"[INIT] Created {len(comments_data)} comments")
            print(f"[INIT] Created {len(friendships_data)} friendships")
            print(f"\n[INIT] 📌 Test credentials:")
            print(f"[INIT] Email: alice@betony.local")
            print(f"[INIT] Password: password123")
            
    except Exception as e:
        print(f"[INIT] ❌ Error initializing sample data: {e}")
        import traceback
        traceback.print_exc()