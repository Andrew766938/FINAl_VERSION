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
from app.models.users import UserModel
from app.schemes.posts import PostCreate
from app.schemes.comments import CommentCreate

# 50 примеров постов
SAMPLE_POSTS_FULL = [
    {"title": "🚀 Новые возможности FastAPI", "content": "Вышла новая версия FastAPI с поддержкой асинхронных операций. Это значительно улучшит производительность веб-приложений. Рекомендую обновиться!"},
    {"title": "💻 Как стать веб-разработчиком за 6 месяцев", "content": "Поделюсь своим опытом обучения веб-разработке. Начал с HTML/CSS, потом JavaScript, затем Python. Главное - практиковаться каждый день!"},
    {"title": "🎨 Дизайн в веб-разработке", "content": "Недооценивают важность дизайна в веб-разработке. Хороший дизайн повышает юзабилити и конверсию. Изучайте UX/UI!"},
    {"title": "🔐 Безопасность веб-приложений", "content": "SQL injection, XSS, CSRF - основные уязвимости в веб-приложениях. Всегда валидируйте входные данные и используйте HTTPS!"},
    {"title": "📚 Лучшие ресурсы для обучения программированию", "content": "Делюсь своим любимым курсом и ресурсами: Codecademy, freeCodeCamp, Udemy. Выбирайте то, что вам подходит!"},
    {"title": "🌍 Разработка с использованием облачных сервисов", "content": "AWS, Google Cloud, Azure - мощные платформы для разворачивания приложений. Попробуйте free tier и начните экспериментировать!"},
    {"title": "⚡ Оптимизация производительности веб-сайтов", "content": "Кэширование, минификация, CDN - способы ускорить ваш сайт. Помните, что каждая миллисекунда важна!"},
    {"title": "🧠 Мотивация в программировании", "content": "Бывают моменты, когда хочется бросить. Но продолжайте! Каждый баг - урок, каждый проект - опыт."},
    {"title": "🔗 REST API vs GraphQL", "content": "Обсуждаем различия между REST и GraphQL. Какой выбрать для вашего проекта? Зависит от требований!"},
    {"title": "📱 Мобильная разработка на Flutter", "content": "Flutter позволяет писать приложения для iOS и Android на одном языке Dart. Отличный выбор для кроссплатформенной разработки!"},
    {"title": "🤖 Искусственный интеллект в веб-разработке", "content": "ML модели теперь легко интегрировать в веб-приложения. Chatbots, рекомендации, анализ текста - всё возможно!"},
    {"title": "🎮 Разработка игр на Unreal Engine", "content": "Unreal Engine - мощный инструмент для создания 3D игр. Даже новичок может создать свою первую игру!"},
    {"title": "💡 Креативный дизайн пользовательского интерфейса", "content": "Дизайн должен быть не только красивым, но и функциональным. Помните о контрастности и читаемости!"},
    {"title": "🚀 DevOps: автоматизация и разворачивание", "content": "Docker и Kubernetes - стандарты в DevOps. Научитесь контейнеризировать ваши приложения!"},
    {"title": "🎓 Сертификаты в IT: стоят ли они?", "content": "Сертификаты помогают, но опыт главнее. Фокусируйтесь на портфолио и реальных проектах!"},
    {"title": "🔍 SEO для веб-разработчиков", "content": "Оптимизация для поисковых систем - часть работы разработчика. Meta tags, структурированные данные, скорость загрузки!"},
    {"title": "💰 Как зарабатывать на фрилансе", "content": "Вот мой способ: выбрать нишу, накопить портфолио, повышать цены постепенно. Терпение и качество работы!"},
    {"title": "⭐ Лучшие практики кода", "content": "Clean Code, SOLID принципы, паттерны проектирования - основа для хорошего кода. Читайте книги, учитесь на чужих ошибках!"},
    {"title": "🐛 Отладка и тестирование", "content": "Unit тесты, интеграционные тесты, end-to-end тесты. Тестирование сокращает время на отладку!"},
    {"title": "🎨 Вёрстка на CSS Grid и Flexbox", "content": "Grid и Flexbox - мощные инструменты для создания адаптивных макетов. Забудьте о float и inline-block!"},
    {"title": "📊 Аналитика и мониторинг приложений", "content": "Google Analytics, Sentry, New Relic - инструменты для понимания поведения пользователей и ошибок."},
    {"title": "🔐 Двухфакторная аутентификация", "content": "2FA повышает безопасность аккаунтов. Используйте TOTP или SMS для защиты пользовательских данных!"},
    {"title": "🌐 Интернационализация веб-приложений", "content": "i18n и l10n - способы поддержки нескольких языков и культур. Расширьте аудиторию вашего приложения!"},
    {"title": "⏱️ Асинхронное программирование в Python", "content": "async/await делает код более читаемым и производительным. Идеально для I/O операций!"},
    {"title": "🎬 Видео контент о программировании", "content": "YouTube каналы: Traversy Media, The Net Ninja, Fireship. Отличные источники для обучения!"},
    {"title": "🤝 Работа в команде разработчиков", "content": "Git, code reviews, коммуникация - ключи к успешной командной работе. Уважайте друг друга!"},
    {"title": "💾 Базы данных: SQL vs NoSQL", "content": "SQL для структурированных данных, NoSQL для гибкости. Выбирайте в зависимости от требований проекта!"},
    {"title": "🏪 Вход в big tech компании", "content": "Подготовка к интервью: алгоритмы, структуры данных, система проектирования. LeetCode и Hackerrank - ваши друзья!"},
    {"title": "🌈 Colorspace и цвета в веб-дизайне", "content": "RGB, HSL, HEX - разные способы задавать цвета. Изучите цветовую палитру и гармонию!"},
    {"title": "🎁 Открытый исходный код: как начать", "content": "Начните с простых проектов на GitHub. Найдите issue для новичков и сделайте pull request!"},
    {"title": "🚴 Велосипед: когда не изобретать заново", "content": "Используйте существующие библиотеки и фреймворки. Не тратьте время на переизобретение колеса!"},
    {"title": "🎸 Творчество и программирование", "content": "Программирование - это творчество. Позвольте себе экспериментировать и пробовать новое!"},
    {"title": "📈 Монетизация своего приложения", "content": "Подписки, реклама, продажи. Выберите подходящую модель для вашего проекта!"},
    {"title": "🔍 Будущее веб-разработки", "content": "WebAssembly, Progressive Web Apps, Jamstack. Будущее выглядит интересно!"},
    {"title": "🧭 Целеполагание в карьере программиста", "content": "Ставьте реалистичные цели. Senior разработчик, team lead, founder - выберите свой путь!"},
    {"title": "🏃 Спринты и планирование", "content": "Agile методология помогает организовать работу. Спринты по 2 недели - оптимальный вариант!"},
    {"title": "💬 Общение и soft skills", "content": "Мягкие навыки важны не менее технических. Учитесь слушать и объяснять сложное просто!"},
    {"title": "🔧 Инструменты разработчика", "content": "IDE, версионирование, контейнеризация. Выберите инструменты, которые вам нравятся!"},
    {"title": "📖 Чтение кода других разработчиков", "content": "Лучший способ научиться - читать качественный код. GitHub полен примеров!"},
    {"title": "🎨 Компоненты в React", "content": "Компоненты - кирпичики React приложений. Функциональные компоненты с хуками - будущее!"},
    {"title": "🌍 Локализация контента", "content": "Разные регионы - разные требования. Адаптируйте ваш контент под аудиторию!"},
    {"title": "⚙️ Микросервисы: архитектура будущего", "content": "Микросервисы позволяют масштабировать части приложения независимо. Но и сложность растёт!"},
    {"title": "🎓 Менторинг: помощь новичкам", "content": "Помогайте новичкам! Это развивает ваши навыки и укрепляет сообщество."},
    {"title": "🚀 Запуск своего стартапа", "content": "Идея, MVP, инвестиции. Путь непростой, но возможный. Начните с валидации идеи!"},
    {"title": "📱 Responsive Design в 2025", "content": "Mobile-first подход больше не опция, это норма. Разрабатывайте для мобильных первыми!"},
    {"title": "🎬 Live coding и стриминг", "content": "YouTube, Twitch - способы поделиться своим процессом разработки с миром!"},
    {"title": "🏆 Участие в хакатонах", "content": "Хакатоны - отличная возможность сетить и попробовать что-то новое. Плюс призы!"},
    {"title": "💼 Карьерный рост в компании", "content": "Junior -> Middle -> Senior -> Lead. У каждого уровня свои задачи и вызовы."},
    {"title": "🎨 Тёмная тема в приложении", "content": "Тёмная тема теперь ожидается пользователями. Используйте CSS переменные для лёгкого переключения!"},
    {"title": "🔐 Password Management Best Practices", "content": "Хешируйте пароли (bcrypt, Argon2), не сохраняйте в plain text. Уважайте данные пользователей!"},
    {"title": "⭐ Создание портфолио на GitHub", "content": "Ваш GitHub - ваше резюме. Делайте качественные проекты, пишите документацию!"},
]

async def init_sample_data():
    """
    Initialize database with sample data
    This includes:
    - Test user account
    - Admin user
    - Sample users (15)
    - Sample posts (50)
    - Sample likes
    - Sample comments
    """
    try:
        async with DBManager(session_factory=async_session_maker) as db:
            # Check if alice@betony.local exists
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
            
            # Create test user first
            auth_service = AuthService(db)
            test_user = None
            try:
                print(f"[INIT] 🧪 Creating TEST user: Тестовый Пользователь")
                test_user, token = await auth_service.register_and_login(
                    email="test@betony.local",
                    password="test123",
                    name="Тестовый Пользователь"
                )
                print(f"[INIT] ✅ TEST user created: {test_user.name} (ID: {test_user.id})")
            except Exception as e:
                print(f"[INIT] ❌ Error creating test user: {e}")
                import traceback
                traceback.print_exc()
            
            # Create sample users - expanded to 15 users + 1 admin
            # ADMIN USER
            admin_user = None
            try:
                print(f"[INIT] 👑 Creating ADMIN user: Админ Бетони")
                admin_user, token = await auth_service.register_and_login(
                    email="alice@betony.local",
                    password="password123",
                    name="Алиса Джонсон"
                )
                # Set admin flag
                admin_user.is_admin = True
                await db.session.commit()
                print(f"[INIT] ✅ ADMIN user created: {admin_user.name} (ID: {admin_user.id})")
            except Exception as e:
                print(f"[INIT] ❌ Error creating admin user: {e}")
                import traceback
                traceback.print_exc()
            
            users_data = [
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
            
            users = [admin_user] if admin_user else []
            for user_data in users_data:
                try:
                    print(f"[INIT] 👤 Creating user: {user_data['name']}")
                    user, token = await auth_service.register_and_login(
                        email=user_data["email"],
                        password=user_data["password"],
                        name=user_data["name"]
                    )
                    users.append(user)
                    print(f"[INIT] ✅ User created successfully: {user.name} (ID: {user.id})")
                except Exception as e:
                    print(f"[INIT] ❌ Error creating user {user_data['name']}: {e}")
            
            if not users:
                print("[INIT] ❌ No users created, aborting data initialization")
                return
            
            # Create 50 sample posts
            posts = []
            print(f"\n[INIT] 📝 Creating 50 sample posts...")
            for i, post_data in enumerate(SAMPLE_POSTS_FULL, 1):
                try:
                    # Alternate between users
                    user_id = users[i % len(users)].id
                    post_create = PostCreate(
                        title=post_data["title"],
                        content=post_data["content"]
                    )
                    post = await db.posts.create_post(post_create, user_id)
                    await db.commit()
                    posts.append(post)
                    print(f"[INIT]   {i}. {post_data['title'][:60]}...")
                except Exception as e:
                    print(f"[INIT] ❌ Error creating post: {e}")
            
            if not posts:
                print("[INIT] ❌ No posts created, aborting")
                return
            
            # Create sample likes (random likes on posts)
            print(f"\n[INIT] ❤️  Adding likes to posts...")
            like_count = 0
            for i, post in enumerate(posts):
                # Each post gets 2-4 likes from random users
                num_likes = 2 + (i % 3)
                for j in range(num_likes):
                    try:
                        user_id = users[(i + j) % len(users)].id
                        # Skip if user is post author
                        if user_id != post.user_id:
                            like = await db.likes.create_like(post.id, user_id)
                            await db.commit()
                            like_count += 1
                    except:
                        pass  # Ignore like creation errors (might be duplicate)
            print(f"[INIT] ✅ Added {like_count} likes")
            
            # Create sample comments
            print(f"\n[INIT] 💬 Adding comments...")
            comments_data = [
                "Отличный пост! Спасибо за информацию!",
                "Очень полезно! Буду использовать эти советы.",
                "Согласен с каждым словом!",
                "Это именно то, что мне нужно было знать.",
                "Спасибо за мотивацию!",
                "Прекрасное объяснение!",
                "Буду учиться по вашим советам.",
                "Очень своевременно!",
                "Спасибо за ссылки на ресурсы!",
                "Это была огромной помощью!",
            ]
            
            comment_count = 0
            for i, post in enumerate(posts[:30]):  # Add comments only to first 30 posts
                num_comments = 1 + (i % 2)
                for j in range(num_comments):
                    try:
                        user_id = users[(i + j + 1) % len(users)].id
                        # Skip if user is post author
                        if user_id != post.user_id:
                            comment_text = comments_data[(i + j) % len(comments_data)]
                            comment_create = CommentCreate(content=comment_text)
                            comment = await db.comments.create_comment(
                                comment_create,
                                user_id,
                                post.id
                            )
                            await db.commit()
                            comment_count += 1
                    except Exception as e:
                        pass  # Ignore comment creation errors
            print(f"[INIT] ✅ Added {comment_count} comments")
            
            print(f"\n{'='*60}")
            print(f"[INIT] ✅ Sample data initialization completed successfully!")
            print(f"{'='*60}")
            print(f"[INIT] Created {len(users)} users")
            print(f"[INIT] Created {len(posts)} posts")
            print(f"[INIT] Created {like_count} likes")
            print(f"[INIT] Created {comment_count} comments")
            print(f"\n[INIT] 📌 Test credentials:")
            print(f"[INIT] Admin/User    - Email: alice@betony.local | Password: password123")
            print(f"[INIT] TEST user     - Email: test@betony.local | Password: test123")
            print(f"{'='*60}")
            
    except Exception as e:
        print(f"[INIT] ❌ Error initializing sample data: {e}")
        import traceback
        traceback.print_exc()
