# 🚀 Установка FINAL_VERSION

## Быстрая установка

### Windows (CMD или PowerShell)

```cmd
setup.bat
```

### Git Bash / Linux / MacOS

```bash
chmod +x setup.sh
./setup.sh
```

---

## Ручная установка

### 1. Проверь Python

```bash
python --version
# Должна быть версия 3.12+
```

### 2. Создай виртуальное окружение

**Windows (PowerShell):**
```powershell
# Удалить старый venv (если есть)
Remove-Item -Recurse -Force venv

# Создать новый
python -m venv venv

# Активировать
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
rmdir /s /q venv
python -m venv venv
venv\Scripts\activate.bat
```

**Git Bash:**
```bash
rm -rf venv
python -m venv venv
source venv/Scripts/activate
```

### 3. Обнови pip

```bash
python -m pip install --upgrade pip
```

### 4. Установи зависимости

```bash
pip install -r requirements.txt
```

### 5. Настрой переменные окружения

```bash
cp .env.example .env
# Отредактируй .env файл
```

### 6. Инициализируй базу данных

```bash
# Применить миграции
alembic upgrade head

# Или создать тестового пользователя
python create_test_user.py
```

### 7. Запусти приложение

```bash
uvicorn main:app --reload
```

Приложение будет доступно по адресу: http://127.0.0.1:8000

---

## 🔧 Решение проблем

### Ошибка: "python не является внутренней командой"

**Решение:** Используй `py` вместо `python`:
```cmd
py -m venv venv
```

### Ошибка: "Execution of scripts is disabled"

**Решение (PowerShell):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Ошибка: "Microsoft Visual C++ 14.0 is required"

**Решение:** Установи [Build Tools for Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

### Ошибка при установке passlib или bcrypt

**Решение:**
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### venv не активируется

**Git Bash:**
```bash
source venv/Scripts/activate
```

**CMD:**
```cmd
venv\Scripts\activate.bat
```

**PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

---

## 📦 Альтернативный метод с uv (быстрее)

```bash
# Установить uv
pip install uv

# Создать venv и установить зависимости одной командой
uv sync

# Активировать
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate.bat  # Windows
```

---

## ✅ Проверка установки

```bash
# Проверь что venv активирован
which python  # должен показать путь к venv/Scripts/python

# Проверь установленные пакеты
pip list

# Тест импортов
python -c "import fastapi; print('FastAPI OK')"
python -c "import sqlalchemy; print('SQLAlchemy OK')"
```

---

## 🎯 Готово!

Теперь можешь запустить приложение:

```bash
uvicorn main:app --reload
```

Документация API: http://127.0.0.1:8000/docs
