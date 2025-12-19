# 🗄️ Database Migrations with Alembic

## Что это?

Alembic - это система управления версиями БД для SQLAlchemy. Все изменения БД теперь сохраняются в файлы миграций, а не локально.

## 📁 Структура

```
alembic/
├── env.py              # Конфигурация окружения
├── script.py.mako      # Шаблон для новых миграций
├── versions/           # Папка со всеми миграциями
│   └── 001_initial_schema.py  # Начальная схема БД
└── alembic.ini         # Конфиг Alembic
```

## 🚀 Первый запуск

### 1. Установи Alembic
```bash
pip install alembic
```

### 2. Примени миграции
```bash
# Примени все миграции к БД
alembic upgrade head
```

Вывод:
```
  [alembic.runtime.migration] Context impl SQLiteImpl.
  [alembic.runtime.migration] Will assume non-transactional DDL.
  [alembic.runtime.migration] Running upgrade  -> 001_initial, Create all initial tables
  ✅ Created table: roles
  ✅ Created table: users
  ✅ Created table: posts
  ✅ Created table: comments
  ✅ Created table: likes
  ✅ Created table: friendships
```

## 📝 Когда нужна новая миграция?

Если ты изменил модели (добавил/удалил поле, таблицу):

### 1. Обнови модель

Например, в `app/models/users.py` добавляешь:
```python
class UserModel(Base):
    __tablename__ = "users"
    # ...
    bio: Mapped[str] = mapped_column(String(500), nullable=True)  # ✨ Новое поле
```

### 2. Создай миграцию
```bash
# Alembic автоматически обнаружит изменения
alembic revision --autogenerate -m "Add bio field to users"
```

Это создаст файл: `alembic/versions/002_add_bio_field_to_users.py`

### 3. Посмотри миграцию
```python
def upgrade() -> None:
    op.add_column('users', sa.Column('bio', sa.String(500), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'bio')
```

### 4. Примени миграцию
```bash
alembic upgrade head
```

## 📊 Полезные команды

```bash
# Посмотреть текущую версию БД
alembic current

# Посмотреть все миграции
alembic history

# Откатить последнюю миграцию
alembic downgrade -1

# Откатить до конкретной версии
alembic downgrade 001_initial

# Создать пустую миграцию (для кастома)
alembic revision -m "Custom migration"

# Показать SQL для миграции без применения
alembic upgrade head --sql
```

## ✅ Текущие таблицы

### roles
- `id` - Primary Key
- `name` - Уникальное имя роли

### users
- `id` - Primary Key
- `name` - Имя пользователя
- `email` - Уникальный email
- `hashed_password` - Хеш пароля
- `is_admin` - Флаг администратора (TRUE/FALSE)
- `role_id` - Foreign Key к roles

### posts
- `id` - Primary Key
- `user_id` - Foreign Key к users
- `title` - Название поста
- `content` - Содержимое
- `created_at` - Время создания
- `updated_at` - Время обновления
- `likes_count` - Счётчик лайков

### comments
- `id` - Primary Key
- `post_id` - Foreign Key к posts
- `user_id` - Foreign Key к users
- `content` - Текст комментария
- `created_at` - Время создания
- `updated_at` - Время обновления

### likes
- `id` - Primary Key
- `user_id` - Foreign Key к users
- `post_id` - Foreign Key к posts
- `created_at` - Время создания
- **Unique:** (user_id, post_id) - один лайк на пост

### friendships
- `id` - Primary Key
- `user_id` - Foreign Key к users (инициатор)
- `friend_id` - Foreign Key к users (друг)
- `created_at` - Время добавления
- **Unique:** (user_id, friend_id) - без дубликатов

## 🎯 Best Practices

1. **Всегда создавай миграцию для изменений БД**
2. **Коммитай миграции в Git** - это часть версионирования
3. **Никогда не редактируй старые миграции** - создавай новые
4. **Тестируй миграции** перед деплоем
5. **Используй autogenerate** для быстрого создания

## 🚨 Если что-то пошло не так

```bash
# Посмотри логи
alembic current
alembic history --verbose

# Откатись и попробуй заново
alembic downgrade base
alembic upgrade head

# Если БД повреждена - удали betony.db и начни заново
rm betony.db
alembic upgrade head
```

## 📚 Полезные ссылки

- [Alembic документация](https://alembic.sqlalchemy.org/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/orm/)
