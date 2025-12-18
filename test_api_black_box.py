#!/usr/bin/env python
"""
🔲 ЧЕРНЫЙ ЯЩИК ТЕСТИРОВАНИЕ API BETONY

Тестирует граничные случаи (Boundary Testing):
- Пустые значения
- Слишком короткие значения
- Слишком длинные значения
- Некорректный формат
- Специальные символы

Валидация:
- Имя (name): 4-15 символов
- Пароль (password): 6-10 символов
- Email: стандартный формат
- Название поста: 1-200 символов
- Содержание поста: 1-5000 символов

Запуск: python test_api_black_box.py
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Any
import string
import random

# Конфиг
API_URL = "http://localhost:8000"
TEST_EMAIL_BASE = f"test_{datetime.now().timestamp()}"

# Глобальные переменные для тестов
auth_token = None
user_id = None
post_id = None

# Цвета для консоли
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

    def add(self, name: str, passed: bool, message: str = "", expected: str = "", got: str = ""):
        self.tests.append({
            "name": name,
            "passed": passed,
            "message": message,
            "expected": expected,
            "got": got,
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
        
        if self.passed + self.failed > 0:
            percent = self.passed / (self.passed + self.failed) * 100
            if percent == 100:
                emoji = "🟢"
            elif percent >= 80:
                emoji = "🟡"
            else:
                emoji = "🔴"
            print(f"{COLORS['YELLOW']}{emoji} Успешность: {percent:.1f}%{COLORS['END']}")
        
        print(f"{'='*70}\n")

        # Список неудачных тестов
        failed_tests = [t for t in self.tests if not t["passed"]]
        if failed_tests:
            print(f"{COLORS['RED']}❌ ОШИБКИ:{COLORS['END']}")
            for test in failed_tests:
                print(f"  • {test['name']}")
                if test['message']:
                    print(f"    └─ {test['message']}")
                if test['expected']:
                    print(f"    └─ Ожидали: {test['expected']}")
                if test['got']:
                    print(f"    └─ Получили: {test['got']}")
            print()


results = TestResults()


def log_test(status: str, name: str, message: str = "", expected: str = "", got: str = ""):
    if status == "PASS":
        print(f"{COLORS['GREEN']}✅{COLORS['END']} {name}")
        results.add(name, True, message, expected, got)
    elif status == "FAIL":
        print(f"{COLORS['RED']}❌{COLORS['END']} {name} {COLORS['RED']}{message}{COLORS['END']}")
        results.add(name, False, message, expected, got)
    elif status == "INFO":
        print(f"{COLORS['BLUE']}ℹ️ {name}{COLORS['END']} {message}")
    elif status == "TEST":
        print(f"\n{COLORS['MAGENTA']}{'─'*70}")
        print(f"🧪 {name}")
        print(f"{'─'*70}{COLORS['END']}")


# ===== ГЕНЕРАТОРЫ ТЕСТОВЫХ ДАННЫХ =====

def gen_random_string(length: int) -> str:
    """Генерирует случайную строку"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# ===== ТЕСТЫ ВАЛИДАЦИИ ИМЕНИ (4-15 символов) =====

def test_name_validation():
    log_test("TEST", "ВАЛИДАЦИЯ ИМЕНИ (4-15 символов)")
    
    test_cases = [
        # (name, should_pass, description)
        ("", False, "Пустое имя"),
        ("ab", False, "2 символа (минимум 4)"),
        ("abc", False, "3 символа (минимум 4)"),
        ("abcd", True, "4 символа (минимум - валидно)"),
        ("TestUser", True, "8 символов (валидно)"),
        ("abcdefghijklmno", True, "15 символов (максимум - валидно)"),
        ("abcdefghijklmnop", False, "16 символов (максимум 15)"),
        ("x" * 100, False, "100 символов (слишком длинное)"),
        ("123", False, "3 символа (только цифры)"),
        ("1234", True, "4 символа (только цифры - валидно)"),
        ("Test User", True, "9 символов со строкой - валидно (если разрешены пробелы)"),
    ]
    
    for name, should_pass, desc in test_cases:
        email = f"{TEST_EMAIL_BASE}_{len(results.tests)}@test.local"
        password = "validpass7"
        
        try:
            res = requests.post(
                f"{API_URL}/auth/register",
                json={"name": name, "email": email, "password": password},
                timeout=5
            )
            
            is_success = res.status_code == 201
            
            if should_pass and is_success:
                log_test("PASS", f"✓ {desc}", f"Статус: {res.status_code}")
            elif not should_pass and not is_success:
                log_test("PASS", f"✓ {desc} (отклонено)", f"Статус: {res.status_code}")
            elif should_pass and not is_success:
                log_test("FAIL", f"✗ {desc}", f"Ожидалось принять, но отклонено", "201", str(res.status_code))
            else:
                log_test("FAIL", f"✗ {desc}", f"Ожидалось отклонить, но принято", "4xx", str(res.status_code))
                
        except Exception as e:
            log_test("FAIL", f"✗ {desc}", f"Ошибка: {e}")


# ===== ТЕСТЫ ВАЛИДАЦИИ ПАРОЛЯ (6-10 символов) =====

def test_password_validation():
    log_test("TEST", "ВАЛИДАЦИЯ ПАРОЛЯ (6-10 символов)")
    
    test_cases = [
        # (password, should_pass, description)
        ("", False, "Пустой пароль"),
        ("12345", False, "5 символов (минимум 6)"),
        ("123456", True, "6 символов (минимум - валидно)"),
        ("ValidPass", True, "9 символов (валидно)"),
        ("1234567890", True, "10 символов (максимум - валидно)"),
        ("12345678901", False, "11 символов (максимум 10)"),
        ("x" * 100, False, "100 символов (слишком длинное)"),
        ("pass!@#$", True, "8 символов со спецсимволами (валидно)"),
        ("Pass123", True, "7 символов - буквы и цифры (валидно)"),
    ]
    
    for password, should_pass, desc in test_cases:
        email = f"{TEST_EMAIL_BASE}_{len(results.tests)}@test.local"
        name = "ValidName123"
        
        try:
            res = requests.post(
                f"{API_URL}/auth/register",
                json={"name": name, "email": email, "password": password},
                timeout=5
            )
            
            is_success = res.status_code == 201
            
            if should_pass and is_success:
                log_test("PASS", f"✓ {desc}", f"Статус: {res.status_code}")
            elif not should_pass and not is_success:
                log_test("PASS", f"✓ {desc} (отклонено)", f"Статус: {res.status_code}")
            elif should_pass and not is_success:
                log_test("FAIL", f"✗ {desc}", f"Ожидалось принять", "201", str(res.status_code))
            else:
                log_test("FAIL", f"✗ {desc}", f"Ожидалось отклонить", "4xx", str(res.status_code))
                
        except Exception as e:
            log_test("FAIL", f"✗ {desc}", f"Ошибка: {e}")


# ===== ТЕСТЫ ВАЛИДАЦИИ EMAIL =====

def test_email_validation():
    log_test("TEST", "ВАЛИДАЦИЯ EMAIL")
    
    test_cases = [
        # (email, should_pass, description)
        ("", False, "Пустой email"),
        ("notanemail", False, "Без @"),
        ("@test.com", False, "Нет части перед @"),
        ("user@", False, "Нет домена после @"),
        ("user@domain", False, "Нет TLD"),
        ("user@domain.com", True, "Валидный email"),
        ("user.name@domain.co.uk", True, "Email с точкой и .co.uk"),
        ("user+tag@domain.com", True, "Email с + (обычно валидно)"),
        ("user @domain.com", False, "Email с пробелом"),
        ("user@domain..com", False, "Двойная точка"),
    ]
    
    for email, should_pass, desc in test_cases:
        name = "ValidName123"
        password = "validpass7"
        
        try:
            res = requests.post(
                f"{API_URL}/auth/register",
                json={"name": name, "email": email, "password": password},
                timeout=5
            )
            
            is_success = res.status_code == 201
            
            if should_pass and is_success:
                log_test("PASS", f"✓ {desc}", f"Статус: {res.status_code}")
            elif not should_pass and not is_success:
                log_test("PASS", f"✓ {desc} (отклонено)", f"Статус: {res.status_code}")
            elif should_pass and not is_success:
                log_test("FAIL", f"✗ {desc}", f"Ожидалось принять", "201", str(res.status_code))
            else:
                log_test("FAIL", f"✗ {desc}", f"Ожидалось отклонить", "4xx", str(res.status_code))
                
        except Exception as e:
            log_test("FAIL", f"✗ {desc}", f"Ошибка: {e}")


# ===== ТЕСТЫ ВАЛИДАЦИИ НАЗВАНИЯ ПОСТА =====

def test_post_title_validation():
    log_test("TEST", "ВАЛИДАЦИЯ НАЗВАНИЯ ПОСТА (1-200 символов)")
    
    global auth_token
    
    if not auth_token:
        log_test("FAIL", "Пропуск: нет токена авторизации")
        return
    
    test_cases = [
        # (title, should_pass, description)
        ("", False, "Пустое название"),
        ("T", True, "1 символ (минимум - валидно)"),
        ("Test", True, "4 символа (валидно)"),
        ("x" * 200, True, "200 символов (максимум - валидно)"),
        ("x" * 201, False, "201 символ (максимум 200)"),
        ("x" * 500, False, "500 символов (слишком длинное)"),
    ]
    
    for title, should_pass, desc in test_cases:
        content = "Valid test content for post validation"
        
        try:
            res = requests.post(
                f"{API_URL}/posts/",
                json={"title": title, "content": content},
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=5
            )
            
            is_success = res.status_code in [200, 201]
            
            if should_pass and is_success:
                log_test("PASS", f"✓ {desc}", f"Статус: {res.status_code}")
            elif not should_pass and not is_success:
                log_test("PASS", f"✓ {desc} (отклонено)", f"Статус: {res.status_code}")
            elif should_pass and not is_success:
                log_test("FAIL", f"✗ {desc}", f"Ожидалось принять", "201", str(res.status_code))
            else:
                log_test("FAIL", f"✗ {desc}", f"Ожидалось отклонить", "4xx", str(res.status_code))
                
        except Exception as e:
            log_test("FAIL", f"✗ {desc}", f"Ошибка: {e}")


# ===== ТЕСТЫ ВАЛИДАЦИИ СОДЕРЖАНИЯ ПОСТА =====

def test_post_content_validation():
    log_test("TEST", "ВАЛИДАЦИЯ СОДЕРЖАНИЯ ПОСТА (1-5000 символов)")
    
    global auth_token
    
    if not auth_token:
        log_test("FAIL", "Пропуск: нет токена авторизации")
        return
    
    test_cases = [
        # (content, should_pass, description)
        ("", False, "Пустое содержание"),
        ("C", True, "1 символ (минимум - валидно)"),
        ("Valid content", True, "13 символов (валидно)"),
        ("x" * 5000, True, "5000 символов (максимум - валидно)"),
        ("x" * 5001, False, "5001 символ (максимум 5000)"),
        ("x" * 10000, False, "10000 символов (слишком длинное)"),
    ]
    
    for content, should_pass, desc in test_cases:
        title = "Test Post Title"
        
        try:
            res = requests.post(
                f"{API_URL}/posts/",
                json={"title": title, "content": content},
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=5
            )
            
            is_success = res.status_code in [200, 201]
            
            if should_pass and is_success:
                log_test("PASS", f"✓ {desc}", f"Статус: {res.status_code}")
            elif not should_pass and not is_success:
                log_test("PASS", f"✓ {desc} (отклонено)", f"Статус: {res.status_code}")
            elif should_pass and not is_success:
                log_test("FAIL", f"✗ {desc}", f"Ожидалось принять", "201", str(res.status_code))
            else:
                log_test("FAIL", f"✗ {desc}", f"Ожидалось отклонить", "4xx", str(res.status_code))
                
        except Exception as e:
            log_test("FAIL", f"✗ {desc}", f"Ошибка: {e}")


# ===== ТЕСТЫ ВАЛИДАЦИИ КОММЕНТАРИЯ =====

def test_comment_validation():
    log_test("TEST", "ВАЛИДАЦИЯ КОММЕНТАРИЯ (1-1000 символов)")
    
    global auth_token, post_id
    
    if not auth_token or not post_id:
        log_test("FAIL", "Пропуск: нет токена или ID поста")
        return
    
    test_cases = [
        # (comment, should_pass, description)
        ("", False, "Пустой комментарий"),
        ("C", True, "1 символ (минимум - валидно)"),
        ("Nice post!", True, "10 символов (валидно)"),
        ("x" * 1000, True, "1000 символов (максимум - валидно)"),
        ("x" * 1001, False, "1001 символ (максимум 1000)"),
    ]
    
    for comment, should_pass, desc in test_cases:
        try:
            res = requests.post(
                f"{API_URL}/posts/{post_id}/comments",
                json={"content": comment},
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=5
            )
            
            is_success = res.status_code in [200, 201]
            
            if should_pass and is_success:
                log_test("PASS", f"✓ {desc}", f"Статус: {res.status_code}")
            elif not should_pass and not is_success:
                log_test("PASS", f"✓ {desc} (отклонено)", f"Статус: {res.status_code}")
            elif should_pass and not is_success:
                log_test("FAIL", f"✗ {desc}", f"Ожидалось принять", "201", str(res.status_code))
            else:
                log_test("FAIL", f"✗ {desc}", f"Ожидалось отклонить", "4xx", str(res.status_code))
                
        except Exception as e:
            log_test("FAIL", f"✗ {desc}", f"Ошибка: {e}")


def authenticate_for_tests():
    """Авторизуемся один раз для всех тестов"""
    global auth_token, post_id
    
    log_test("INFO", "🔐 Авторизация для тестов")
    
    try:
        res = requests.post(
            f"{API_URL}/auth/login",
            json={"email": "alice@betony.local", "password": "password123"},
            timeout=5
        )
        
        if res.status_code == 200:
            auth_token = res.json().get("access_token")
            log_test("INFO", "✅ Авторизация успешна")
            
            # Создаём тестовый пост
            post_res = requests.post(
                f"{API_URL}/posts/",
                json={"title": "Test Post for Comments", "content": "Test content"},
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=5
            )
            if post_res.status_code in [200, 201]:
                post_id = post_res.json().get("id")
                log_test("INFO", f"✅ Тестовый пост создан (ID: {post_id})")
        else:
            log_test("FAIL", "❌ Ошибка авторизации", f"Статус: {res.status_code}")
    except Exception as e:
        log_test("FAIL", "❌ Ошибка авторизации", str(e))


def main():
    print(f"""
╔{'='*68}╗
║ {COLORS['CYAN']}🔲 ЧЕРНЫЙ ЯЩИК ТЕСТИРОВАНИЕ API BETONY{COLORS['END']:<35} ║
║ {f"API URL: {API_URL}":<68} ║
╚{'='*68}╝
    """)
    
    print(f"{COLORS['YELLOW']}📋 ПРАВИЛА ВАЛИДАЦИИ:{COLORS['END']}")
    print("  • Имя (name): 4-15 символов")
    print("  • Пароль (password): 6-10 символов")
    print("  • Email: стандартный формат (user@domain.com)")
    print("  • Название поста: 1-200 символов")
    print("  • Содержание поста: 1-5000 символов")
    print("  • Комментарий: 1-1000 символов\n")
    
    try:
        # Авторизуемся один раз
        authenticate_for_tests()
        
        # Запускаем все тесты
        test_name_validation()
        test_password_validation()
        test_email_validation()
        test_post_title_validation()
        test_post_content_validation()
        test_comment_validation()
        
    except requests.exceptions.ConnectionError:
        print(f"{COLORS['RED']}❌ ОШИБКА: Не удаётся подключиться к {API_URL}{COLORS['END']}")
        print("Убедитесь, что сервер запущен: python -m uvicorn main:app --reload\n")
    except Exception as e:
        print(f"{COLORS['RED']}❌ НЕОЖИДАННАЯ ОШИБКА: {e}{COLORS['END']}\n")
    
    finally:
        results.print_summary()


if __name__ == "__main__":
    main()
