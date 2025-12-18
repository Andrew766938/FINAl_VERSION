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
            
            # Create sample users - expanded to 15 users
            auth_service = AuthService(db)
            
            users_data = [
                {"email": "alice@betony.local", "password": "password123", "name": "Алиса Джонсон"},
                {"email": "bob@betony.local", "password": "password123", "name": "Боб Смит"},
                {"email": "charlie@betony.local", "password": "password123", "name": "Чарли Браун"},
                {"email": "diana@betony.local", "password": "password123", "name": "Диана Принс"},
                {"email": "evan@betony.local", "password": "password123", "name": "Иван Дэвис"},
                {"email": "fiona@betony.local", "password": "password123", "name": "Фиона Гарсия"},
                {"email": "george@betony.local", "password": "password123", "name": "Джордж Мартинес"},
                {"email": "hannah@betony.local", "password": "password123", "name": "Ханна Родригес"},
                {"email": "ian@betony.local", "password": "password123", "name": "Ян Вилсон"},
                {"email": "julia@betony.local", "password": "password123", "name": "Юлия Андерсон"},
                {"email": "kevin@betony.local", "password": "password123", "name": "Кевин Тейлор"},
                {"email": "lisa@betony.local", "password": "password123", "name": "Лиза Томас"},
                {"email": "michael@betony.local", "password": "password123", "name": "Майкл Ли"},
                {"email": "nina@betony.local", "password": "password123", "name": "Нина Уайт"},
                {"email": "oliver@betony.local", "password": "password123", "name": "Оливер Харрис"},
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
                    "title": "Мой первый пост в блоге",
                    "content": "Привет всем! Это мой первый пост в Betony. Я рад поделиться своими мыслями и пообщаться с сообществом.",
                    "user_id": users[0].id
                },
                {
                    "title": "Изучение Python - это потрясающе",
                    "content": "Начал изучать Python в прошлом месяце и это был удивительный путь. Синтаксис очень чистый и выразительный.",
                    "user_id": users[1].id
                },
                {
                    "title": "Советы по веб-разработке",
                    "content": "Вот несколько советов, которые я узнал о веб-разработке: 1) Всегда тестируйте код, 2) Используйте контроль версий, 3) Пишите чистый код.",
                    "user_id": users[2].id
                },
                {
                    "title": "Создание приложений на FastAPI",
                    "content": "FastAPI - это современный, быстрый веб-фреймворк для создания API на Python. Я использую его и люблю опыт разработки.",
                    "user_id": users[0].id
                },
                {
                    "title": "Советы для удаленной работы",
                    "content": "Удаленная работа имеет свои плюсы и минусы. Вот мои советы: соблюдайте график, имейте отдельное рабочее место, делайте перерывы.",
                    "user_id": users[3].id
                },
                {
                    "title": "Книги, которые стоит прочитать",
                    "content": "В последнее время я читаю отличные книги. Проверьте 'Clean Code' и 'Design Patterns' - они улучшили мои навыки программирования.",
                    "user_id": users[4].id
                },
                {
                    "title": "Кофе и кодирование",
                    "content": "Есть что-то магическое в хорошей чашке кофе во время кодирования. Какой ваш любимый напиток для программирования?",
                    "user_id": users[5].id
                },
                {
                    "title": "Путешествие в Machine Learning",
                    "content": "На этой неделе начал изучать машинное обучение. Возможности безграничны и я с нетерпением жду глубокого погружения!",
                    "user_id": users[6].id
                },
                {
                    "title": "Frontend vs Backend",
                    "content": "И фронтенд, и бэкенд разработка имеют свои преимущества. Я люблю работать над полнофункциональными проектами, где я могу делать оба!",
                    "user_id": users[7].id
                },
                {
                    "title": "Вклад в Open Source",
                    "content": "Сегодня я сделал свой первый вклад в открытый исходный код! Это замечательное чувство - вносить вклад в сообщество.",
                    "user_id": users[8].id
                },
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
                (posts[6].id, users[7].id),
                (posts[7].id, users[8].id),
                (posts[8].id, users[9].id),
                (posts[9].id, users[10].id),
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
                    "content": "Отличный первый пост! Добро пожаловать в Betony!"
                },
                {
                    "post_id": posts[0].id,
                    "user_id": users[2].id,
                    "content": "С нетерпением жду больше постов от вас!"
                },
                {
                    "post_id": posts[1].id,
                    "user_id": users[0].id,
                    "content": "Python просто замечательный! Ты уже пробовал FastAPI?"
                },
                {
                    "post_id": posts[2].id,
                    "user_id": users[1].id,
                    "content": "Это отличные советы! Чистый код очень важен."
                },
                {
                    "post_id": posts[3].id,
                    "user_id": users[2].id,
                    "content": "FastAPI действительно революционер для разработки API."
                },
                {
                    "post_id": posts[4].id,
                    "user_id": users[1].id,
                    "content": "Я полностью согласен с советом про отдельное рабочее место!"
                },
                {
                    "post_id": posts[5].id,
                    "user_id": users[0].id,
                    "content": "Clean Code - моя любимая книга! Спасибо за рекомендации."
                },
                {
                    "post_id": posts[6].id,
                    "user_id": users[8].id,
                    "content": "Кофе просто необходим! Хотя я предпочитаю зелёный чай."
                },
                {
                    "post_id": posts[7].id,
                    "user_id": users[9].id,
                    "content": "ML просто фантастика! Проверь PyTorch если ещё не пробовал."
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
            
            # Create sample friendships - REMOVED to allow manual testing
            # Users can now add friends manually through the UI
            
            print(f"\n[INIT] ✅ Sample data initialization completed successfully!")
            print(f"[INIT] Created {len(users)} users")
            print(f"[INIT] Created {len(posts)} posts")
            print(f"[INIT] Created {len(like_pairs)} likes")
            print(f"[INIT] Created {len(comments_data)} comments")
            print(f"\n[INIT] 📌 Test credentials:")
            print(f"[INIT] Email: alice@betony.local")
            print(f"[INIT] Password: password123")
            
    except Exception as e:
        print(f"[INIT] ❌ Error initializing sample data: {e}")
        import traceback
        traceback.print_exc()