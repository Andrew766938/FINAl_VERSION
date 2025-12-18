#!/usr/bin/env python
"""
🔲 ЧЕРНЫЙ ЯЩИК ТЕСТИРОВАНИЕ API BETONY

Тестирует все API эндпоинты без знания внутреннего устройства.
Проверяет:
- HTTP коды ответов
- Структуру JSON
- Валидность данных
- Ошибки и граничные случаи

Запуск: python test_api_black_box.py
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Any

# Конфиг
API_URL = "http://localhost:8000"
TEST_EMAIL = "alice@betony.local"
TEST_PASSWORD = "password123"

# Глобальные переменные для тестов
auth_token = None
user_id = None
post_id = None
comment_id = None

# Цвета для консоли
COLORS = {
    "GREEN": "\033[92m",
    "RED": "\033[91m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "CYAN": "\033[96m",
    "END": "\033[0m",
}


class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def add_test(self, name: str, passed: bool, message: str = "", details: Dict = None):
        self.tests.append({
            "name": name,
            "passed": passed,
            "message": message,
            "details": details or {},
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1

    def print_summary(self):
        print(f"\n{'='*70}")
        print(f"{COLORS['CYAN']}📊 ИТОГИ ТЕСТИРОВАНИЯ{COLORS['END']}")
        print(f"{'='*70}")
        print(f"{COLORS['GREEN']}✅ Пройдено: {self.passed}{COLORS['END']}")
        print(f"{COLORS['RED']}❌ Не пройдено: {self.failed}{COLORS['END']}")
        print(f"{COLORS['BLUE']}📈 Всего: {self.passed + self.failed}{COLORS['END']}")
        print(f"{COLORS['YELLOW']}⚡ Успешность: {self.passed / max(1, self.passed + self.failed) * 100:.1f}%{COLORS['END']}")
        print(f"{'='*70}\n")

        # Список неудачных тестов
        failed_tests = [t for t in self.tests if not t["passed"]]
        if failed_tests:
            print(f"{COLORS['RED']}❌ ОШИБКИ:{COLORS['END']}")
            for test in failed_tests:
                print(f"  • {test['name']}: {test['message']}")
                if test['details']:
                    print(f"    Детали: {test['details']}")


results = TestResults()


def log_test(status: str, name: str, message: str = ""):
    """Логирование результата теста"""
    if status == "PASS":
        print(f"{COLORS['GREEN']}✅ {name}{COLORS['END']} {message}")
        results.add_test(name, True, message)
    elif status == "FAIL":
        print(f"{COLORS['RED']}❌ {name}{COLORS['END']} {message}")
        results.add_test(name, False, message)
    elif status == "INFO":
        print(f"{COLORS['BLUE']}ℹ️  {name}{COLORS['END']} {message}")
    elif status == "WARN":
        print(f"{COLORS['YELLOW']}⚠️  {name}{COLORS['END']} {message}")


# ===== AUTH ТЕСТЫ =====

def test_register():
    """Тест регистрации новых пользователей"""
    print(f"\n{COLORS['CYAN']}🔐 ТЕСТ РЕГИСТРАЦИИ{COLORS['END']}")
    print("="*70)

    # Тест 1: Успешная регистрация
    test_user = {
        "email": f"testuser_{datetime.now().timestamp()}@test.local",
        "password": "test123456",
        "name": "Test User",
    }

    try:
        res = requests.post(f"{API_URL}/auth/register", json=test_user)
        if res.status_code == 201:
            log_test("PASS", "Успешная регистрация", f"Статус: {res.status_code}")
        else:
            log_test("FAIL", "Успешная регистрация", f"Ожидаем 201, получили {res.status_code}")
    except Exception as e:
        log_test("FAIL", "Успешная регистрация", f"Ошибка: {e}")

    # Тест 2: Дублирующийся email
    try:
        res = requests.post(f"{API_URL}/auth/register", json=test_user)
        if res.status_code in [400, 409]:
            log_test("PASS", "Отказ при дублирующемся email", f"Статус: {res.status_code}")
        else:
            log_test("WARN", "Отказ при дублирующемся email", f"Ожидаем 400/409, получили {res.status_code}")
    except Exception as e:
        log_test("FAIL", "Отказ при дублирующемся email", f"Ошибка: {e}")

    # Тест 3: Пустой email
    try:
        res = requests.post(f"{API_URL}/auth/register", json={"email": "", "password": "test"})
        if res.status_code in [400, 422]:
            log_test("PASS", "Валидация пустого email", f"Статус: {res.status_code}")
        else:
            log_test("WARN", "Валидация пустого email", f"Ожидаем 400/422, получили {res.status_code}")
    except Exception as e:
        log_test("FAIL", "Валидация пустого email", f"Ошибка: {e}")


def test_login():
    """Тест логина"""
    global auth_token, user_id

    print(f"\n{COLORS['CYAN']}🔑 ТЕСТ ЛОГИНА{COLORS['END']}")
    print("="*70)

    # Тест 1: Успешный логин
    try:
        res = requests.post(f"{API_URL}/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
        if res.status_code == 200:
            data = res.json()
            if "access_token" in data:
                auth_token = data["access_token"]
                log_test("PASS", "Успешный логин", f"Получен токен")
            else:
                log_test("FAIL", "Успешный логин", "Токен не найден в ответе")
        else:
            log_test("FAIL", "Успешный логин", f"Статус: {res.status_code}")
    except Exception as e:
        log_test("FAIL", "Успешный логин", f"Ошибка: {e}")

    # Тест 2: Неправильный пароль
    try:
        res = requests.post(f"{API_URL}/auth/login", json={"email": TEST_EMAIL, "password": "wrongpassword"})
        if res.status_code in [401, 403]:
            log_test("PASS", "Отказ при неправильном пароле", f"Статус: {res.status_code}")
        else:
            log_test("WARN", "Отказ при неправильном пароле", f"Ожидаем 401/403, получили {res.status_code}")
    except Exception as e:
        log_test("FAIL", "Отказ при неправильном пароле", f"Ошибка: {e}")

    # Тест 3: Несуществующий пользователь
    try:
        res = requests.post(f"{API_URL}/auth/login", json={"email": "nonexistent@test.local", "password": "pass"})
        if res.status_code in [401, 403, 404]:
            log_test("PASS", "Отказ при несуществующем пользователе", f"Статус: {res.status_code}")
        else:
            log_test("WARN", "Отказ при несуществующем пользователе", f"Ожидаем 401/403/404, получили {res.status_code}")
    except Exception as e:
        log_test("FAIL", "Отказ при несуществующем пользователе", f"Ошибка: {e}")


def test_auth_me():
    """Тест получения текущего пользователя"""
    global user_id

    print(f"\n{COLORS['CYAN']}👤 ТЕСТ GET /auth/me{COLORS['END']}")
    print("="*70)

    if not auth_token:
        log_test("FAIL", "GET /auth/me", "Токен не установлен (не прошли login)")
        return

    try:
        res = requests.get(f"{API_URL}/auth/me", headers={"Authorization": f"Bearer {auth_token}"})
        if res.status_code == 200:
            data = res.json()
            user_id = data.get("id")
            if user_id and "email" in data:
                log_test("PASS", "GET /auth/me", f"Получена инфо пользователя (ID: {user_id})")
            else:
                log_test("FAIL", "GET /auth/me", "Структура данных неправильна")
        else:
            log_test("FAIL", "GET /auth/me", f"Статус: {res.status_code}")
    except Exception as e:
        log_test("FAIL", "GET /auth/me", f"Ошибка: {e}")

    # Тест без токена
    try:
        res = requests.get(f"{API_URL}/auth/me")
        if res.status_code in [401, 403]:
            log_test("PASS", "GET /auth/me без токена", f"Отказано (статус: {res.status_code})")
        else:
            log_test("WARN", "GET /auth/me без токена", f"Ожидаем 401/403, получили {res.status_code}")
    except Exception as e:
        log_test("FAIL", "GET /auth/me без токена", f"Ошибка: {e}")


# ===== POSTS ТЕСТЫ =====

def test_posts_list():
    """Тест получения списка постов"""
    print(f"\n{COLORS['CYAN']}📝 ТЕСТ GET /posts/{COLORS['END']}")
    print("="*70)

    if not auth_token:
        log_test("FAIL", "GET /posts", "Токен не установлен")
        return

    try:
        res = requests.get(f"{API_URL}/posts/", headers={"Authorization": f"Bearer {auth_token}"})
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list):
                log_test("PASS", "GET /posts", f"Получено {len(data)} постов")
                if data:
                    post = data[0]
                    if all(k in post for k in ["id", "title", "content", "user_id"]):
                        log_test("PASS", "Структура поста", "Все необходимые поля присутствуют")
                    else:
                        log_test("FAIL", "Структура поста", "Отсутствуют обязательные поля")
            else:
                log_test("FAIL", "GET /posts", "Ответ не является массивом")
        else:
            log_test("FAIL", "GET /posts", f"Статус: {res.status_code}")
    except Exception as e:
        log_test("FAIL", "GET /posts", f"Ошибка: {e}")


def test_create_post():
    """Тест создания поста"""
    global post_id

    print(f"\n{COLORS['CYAN']}✍️  ТЕСТ POST /posts/{COLORS['END']}")
    print("="*70)

    if not auth_token:
        log_test("FAIL", "POST /posts", "Токен не установлен")
        return

    post_data = {
        "title": f"🧪 Тестовый пост {datetime.now().isoformat()}",
        "content": "Это автоматический тест API методом черного ящика. Проверяем создание постов.",
    }

    try:
        res = requests.post(
            f"{API_URL}/posts/",
            json=post_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        if res.status_code == 201:
            data = res.json()
            post_id = data.get("id")
            if post_id:
                log_test("PASS", "POST /posts", f"Пост создан (ID: {post_id})")
            else:
                log_test("FAIL", "POST /posts", "ID поста не найден в ответе")
        else:
            log_test("FAIL", "POST /posts", f"Статус: {res.status_code}")
    except Exception as e:
        log_test("FAIL", "POST /posts", f"Ошибка: {e}")

    # Тест с пустым название
    try:
        res = requests.post(
            f"{API_URL}/posts/",
            json={"title": "", "content": "Content"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        if res.status_code in [400, 422]:
            log_test("PASS", "Валидация пустого названия", f"Статус: {res.status_code}")
        else:
            log_test("WARN", "Валидация пустого названия", f"Ожидаем 400/422, получили {res.status_code}")
    except Exception as e:
        log_test("FAIL", "Валидация пустого названия", f"Ошибка: {e}")


def test_get_post():
    """Тест получения одного поста"""
    print(f"\n{COLORS['CYAN']}📖 ТЕСТ GET /posts/{{id}}{COLORS['END']}")
    print("="*70)

    if not auth_token or not post_id:
        log_test("FAIL", "GET /posts/{id}", "Токен или ID поста не установлены")
        return

    try:
        res = requests.get(
            f"{API_URL}/posts/{post_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        if res.status_code == 200:
            data = res.json()
            if data.get("id") == post_id:
                log_test("PASS", "GET /posts/{id}", f"Пост получен")
            else:
                log_test("FAIL", "GET /posts/{id}", "ID не совпадает")
        else:
            log_test("FAIL", "GET /posts/{id}", f"Статус: {res.status_code}")
    except Exception as e:
        log_test("FAIL", "GET /posts/{id}", f"Ошибка: {e}")

    # Тест с несуществующим ID
    try:
        res = requests.get(
            f"{API_URL}/posts/999999",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        if res.status_code == 404:
            log_test("PASS", "GET /posts/{{id}} несуществующего", f"Статус: {res.status_code}")
        else:
            log_test("WARN", "GET /posts/{{id}} несуществующего", f"Ожидаем 404, получили {res.status_code}")
    except Exception as e:
        log_test("FAIL", "GET /posts/{{id}} несуществующего", f"Ошибка: {e}")


def test_like_post():
    """Тест лайка поста"""
    print(f"\n{COLORS['CYAN']}❤️  ТЕСТ LIKE /posts/{{id}}/like{COLORS['END']}")
    print("="*70)

    if not auth_token or not post_id:
        log_test("FAIL", "POST /posts/{id}/like", "Токен или ID поста не установлены")
        return

    try:
        res = requests.post(
            f"{API_URL}/posts/{post_id}/like",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        if res.status_code in [200, 201]:
            log_test("PASS", "POST /posts/{id}/like", f"Лайк добавлен (статус: {res.status_code})")
        else:
            log_test("FAIL", "POST /posts/{id}/like", f"Статус: {res.status_code}")
    except Exception as e:
        log_test("FAIL", "POST /posts/{id}/like", f"Ошибка: {e}")

    # Тест удаления лайка
    try:
        res = requests.delete(
            f"{API_URL}/posts/{post_id}/like",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        if res.status_code == 200:
            log_test("PASS", "DELETE /posts/{id}/like", "Лайк удален")
        else:
            log_test("WARN", "DELETE /posts/{id}/like", f"Статус: {res.status_code}")
    except Exception as e:
        log_test("FAIL", "DELETE /posts/{id}/like", f"Ошибка: {e}")


def test_comments():
    """Тест комментариев"""
    global comment_id

    print(f"\n{COLORS['CYAN']}💬 ТЕСТ COMMENTS{COLORS['END']}")
    print("="*70)

    if not auth_token or not post_id:
        log_test("FAIL", "Comments", "Токен или ID поста не установлены")
        return

    # Тест получения комментариев
    try:
        res = requests.get(
            f"{API_URL}/posts/{post_id}/comments",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list):
                log_test("PASS", "GET /posts/{id}/comments", f"Получено {len(data)} комментариев")
            else:
                log_test("FAIL", "GET /posts/{id}/comments", "Ответ не является массивом")
        else:
            log_test("FAIL", "GET /posts/{id}/comments", f"Статус: {res.status_code}")
    except Exception as e:
        log_test("FAIL", "GET /posts/{id}/comments", f"Ошибка: {e}")

    # Тест добавления комментария
    try:
        res = requests.post(
            f"{API_URL}/posts/{post_id}/comments",
            json={"content": "🧪 Тестовый комментарий из черного ящика"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        if res.status_code in [201, 200]:
            data = res.json()
            comment_id = data.get("id")
            log_test("PASS", "POST /posts/{id}/comments", f"Комментарий создан (ID: {comment_id})")
        else:
            log_test("FAIL", "POST /posts/{id}/comments", f"Статус: {res.status_code}")
    except Exception as e:
        log_test("FAIL", "POST /posts/{id}/comments", f"Ошибка: {e}")


def test_delete_comment():
    """Тест удаления комментария"""
    print(f"\n{COLORS['CYAN']}🗑️  ТЕСТ DELETE /posts/{{id}}/comments/{{id}}{COLORS['END']}")
    print("="*70)

    if not auth_token or not post_id or not comment_id:
        log_test("FAIL", "DELETE /posts/{id}/comments/{id}", "Необходимые параметры не установлены")
        return

    try:
        res = requests.delete(
            f"{API_URL}/posts/{post_id}/comments/{comment_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        if res.status_code == 200:
            log_test("PASS", "DELETE /posts/{id}/comments/{id}", "Комментарий удален")
        else:
            log_test("FAIL", "DELETE /posts/{id}/comments/{id}", f"Статус: {res.status_code}")
    except Exception as e:
        log_test("FAIL", "DELETE /posts/{id}/comments/{id}", f"Ошибка: {e}")


def test_delete_post():
    """Тест удаления поста"""
    print(f"\n{COLORS['CYAN']}🗑️  ТЕСТ DELETE /posts/{{id}}{COLORS['END']}")
    print("="*70)

    if not auth_token or not post_id:
        log_test("FAIL", "DELETE /posts/{id}", "Токен или ID поста не установлены")
        return

    try:
        res = requests.delete(
            f"{API_URL}/posts/{post_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        if res.status_code == 200:
            log_test("PASS", "DELETE /posts/{id}", "Пост удален")
        else:
            log_test("FAIL", "DELETE /posts/{id}", f"Статус: {res.status_code}")
    except Exception as e:
        log_test("FAIL", "DELETE /posts/{id}", f"Ошибка: {e}")


def main():
    """Главная функция"""
    print(f"""
╔{'='*68}╗
║ {COLORS['CYAN']}🔲 ЧЕРНЫЙ ЯЩИК ТЕСТИРОВАНИЕ API BETONY{COLORS['END']:<36} ║
║ {f"API URL: {API_URL}":<68} ║
╚{'='*68}╝
    """)

    try:
        # Тесты аутентификации
        test_register()
        test_login()
        test_auth_me()

        # Тесты постов
        test_posts_list()
        test_create_post()
        test_get_post()
        test_like_post()

        # Тесты комментариев
        test_comments()
        test_delete_comment()

        # Тесты удаления
        test_delete_post()

    except requests.exceptions.ConnectionError:
        print(f"{COLORS['RED']}❌ ОШИБКА: Не удаётся подключиться к {API_URL}{COLORS['END']}")
        print("Убедитесь, что сервер запущен: python -m uvicorn main:app --reload")
    except Exception as e:
        print(f"{COLORS['RED']}❌ НЕОЖИДАННАЯ ОШИБКА: {e}{COLORS['END']}")

    finally:
        results.print_summary()


if __name__ == "__main__":
    main()
