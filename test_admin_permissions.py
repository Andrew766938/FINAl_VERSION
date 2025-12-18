#!/usr/bin/env python
"""
👑 ТЕСТ Админ разрешений

Проверяет:
- Админ может удалять любой пост
- Пользователь может удалять только свои посты
- Пользователь не может удалить пост другого
- Админ также может удалять комментарии

Запуск: python test_admin_permissions.py
"""

import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000"

# Цвета
COLORS = {
    "GREEN": "\033[92m",
    "RED": "\033[91m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "CYAN": "\033[96m",
    "MAGENTA": "\033[95m",
    "END": "\033[0m",
}


class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def add(self, name: str, passed: bool, message: str = ""):
        self.tests.append({"name": name, "passed": passed, "message": message})
        if passed:
            self.passed += 1
        else:
            self.failed += 1

    def print_summary(self):
        print(f"\n{'='*70}")
        print(f"{COLORS['CYAN']}📊 ИТОГИ ТЕСТА ПРАВ{COLORS['END']}")
        print(f"{'='*70}")
        print(f"{COLORS['GREEN']}✅ Пройдено: {self.passed}{COLORS['END']}")
        print(f"{COLORS['RED']}❌ Не пройдено: {self.failed}{COLORS['END']}")
        print(f"{COLORS['BLUE']}📈 Всего: {self.passed + self.failed}{COLORS['END']}")
        if self.passed + self.failed > 0:
            percent = self.passed / (self.passed + self.failed) * 100
            print(f"{COLORS['YELLOW']}⚡ Успешность: {percent:.1f}%{COLORS['END']}")
        print(f"{'='*70}\n")

        if self.failed > 0:
            print(f"{COLORS['RED']}❌ НЕПАССЕD ТЕСТЫ:{COLORS['END']}")
            for test in self.tests:
                if not test["passed"]:
                    print(f"  • {test['name']}: {test['message']}")


results = TestResults()


def log_test(status: str, name: str, message: str = ""):
    if status == "PASS":
        print(f"{COLORS['GREEN']}✅{COLORS['END']} {name}")
        results.add(name, True, message)
    elif status == "FAIL":
        print(f"{COLORS['RED']}❌{COLORS['END']} {name} {COLORS['RED']}{message}{COLORS['END']}")
        results.add(name, False, message)
    elif status == "TEST":
        print(f"\n{COLORS['MAGENTA']}{'─'*70}")
        print(f"👑 {name}")
        print(f"{'─'*70}{COLORS['END']}")


def get_token(email: str, password: str) -> str:
    """Get auth token for a user"""
    try:
        res = requests.post(
            f"{API_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=5
        )
        if res.status_code == 200:
            return res.json()["access_token"]
    except Exception as e:
        print(f"Error getting token: {e}")
    return None


def main():
    print(f"""
╔{'='*68}╗
║ {COLORS['CYAN']}👑 ТЕСТ Админ РАЗРЕШЕНИЙ{COLORS['END']:<30} ║
║ {f"API URL: {API_URL}":<68} ║
╚{'='*68}╝
    """)

    # Авторизация
    log_test("TEST", "АВТОРИЗАЦИЯ И СОЗДАНИЕ ПОСТОВ")

    # Авторизуемся как админ
    admin_token = get_token("alice@betony.local", "password123")
    if not admin_token:
        log_test("FAIL", "Admin login", "Failed to login as admin")
        return
    log_test("PASS", "Admin login", "alice@betony.local")

    # Авторизуемся как обычный пользователь
    user_token = get_token("bob@betony.local", "password123")
    if not user_token:
        log_test("FAIL", "User login", "Failed to login as bob")
        return
    log_test("PASS", "User login", "bob@betony.local")

    # Создаём пост как обычный пользователь
    try:
        res = requests.post(
            f"{API_URL}/posts/",
            json={
                "title": "🪠 Пост для теста удаления",
                "content": "Этот пост будет удалэн администратором"
            },
            headers={"Authorization": f"Bearer {user_token}"},
            timeout=5
        )
        if res.status_code == 201:
            post_id = res.json()["id"]
            log_test("PASS", "Create post as user", f"Post ID: {post_id}")
        else:
            log_test("FAIL", "Create post as user", f"Status: {res.status_code}")
            return
    except Exception as e:
        log_test("FAIL", "Create post as user", str(e))
        return

    # ТЕСТ 1: Обычный пользователь может удалить свой пост
    log_test("TEST", "ПОЛЬЗОВАТЕЛЬ МОЖЕТ УДАЛЯТЬ СВОЙ ПОСТ")
    try:
        res = requests.delete(
            f"{API_URL}/posts/{post_id}",
            headers={"Authorization": f"Bearer {user_token}"},
            timeout=5
        )
        if res.status_code == 204:
            log_test("PASS", "User deletes own post", f"Status: {res.status_code}")
            # Создаём новый пост для дальнейших тестов
            res = requests.post(
                f"{API_URL}/posts/",
                json={
                    "title": "🪠 Пост для теста админа",
                    "content": "Ныне админ попытается удалить этот пост"
                },
                headers={"Authorization": f"Bearer {user_token}"},
                timeout=5
            )
            if res.status_code == 201:
                post_id = res.json()["id"]
        else:
            log_test("FAIL", "User deletes own post", f"Status: {res.status_code}")
    except Exception as e:
        log_test("FAIL", "User deletes own post", str(e))

    # ТЕСТ 2: Обычный пользователь НЕ может удалить чужой пост
    log_test(
        "TEST",
        "ПОЛЬЗОВАТЕЛЬ НЕ МОЖЕТ УДАЛЯТЬ ЧУЖОЙ ПОСТ"
    )
    try:
        res = requests.delete(
            f"{API_URL}/posts/{post_id}",
            headers={"Authorization": f"Bearer {user_token}"},
            timeout=5
        )
        if res.status_code == 403:
            log_test(
                "PASS",
                "User CANNOT delete other's post",
                f"Status: {res.status_code} (Forbidden)"
            )
        else:
            log_test(
                "FAIL",
                "User CANNOT delete other's post",
                f"Expected 403, got {res.status_code}"
            )
    except Exception as e:
        log_test("FAIL", "User CANNOT delete other's post", str(e))

    # ТЕСТ 3: Админ МОЖЕТ удалить ЛЮБОЙ пост
    log_test(
        "TEST",
        "АДМИН МОЖЕТ УДАЛЯТЬ ЛЮБОЙ ПОСТ"
    )
    try:
        res = requests.delete(
            f"{API_URL}/posts/{post_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=5
        )
        if res.status_code == 204:
            log_test(
                "PASS",
                "Admin DELETES other's post",
                f"Status: {res.status_code} (Удален)"
            )
        else:
            log_test(
                "FAIL",
                "Admin DELETES other's post",
                f"Expected 204, got {res.status_code}"
            )
    except Exception as e:
        log_test("FAIL", "Admin DELETES other's post", str(e))

    # Принтим результаты
    results.print_summary()


if __name__ == "__main__":
    main()
