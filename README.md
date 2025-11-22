# 🧩 Task Tracker API

**Task Tracker** — это REST API для управления задачами и сотрудниками.  
Проект реализован на **Django 5.2** и **Django REST Framework**, использует **JWT-аутентификацию**, **PostgreSQL**, а также поддерживает запуск как напрямую, так и через Docker.

---

## 🚀 Возможности

- Создание, редактирование и удаление задач  
- Назначение исполнителей и дедлайнов  
- Иерархия задач (родительская / подзадача)  
- Просмотр сотрудников и их активных задач  
- Отчёт по "важным задачам"  
- JWT-аутентификация пользователей  
- Swagger и Redoc-документация  
- Поддержка Docker и docker-compose

---

## 📂 Структура проекта

```text
Task_tracker/
├── config/                 # Настройки Django
├── tasks/                  # Приложение задач и сотрудников
├── users/                  # Регистрация, JWT и профиль пользователя
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env_sample
└── README.md
```

---

## ⚙️ Переменные окружения

Перед запуском скопируй пример и создай `.env`:

```bash
cp .env_sample .env
```

Пример (`.env_sample`):

```
SECRET_KEY=django-insecure-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

POSTGRES_DB=task_tracker
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

---

## 💻 Запуск без Docker

### 1. Создай виртуальное окружение

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\Activate.ps1
# Linux/macOS
# source .venv/bin/activate
```

### 2. Установи зависимости

```bash
pip install -r requirements.txt
```

### 3. Настрой окружение и базу

Создай `.env` и укажи параметры (см. пример выше).  
Если PostgreSQL недоступен, можно временно использовать SQLite, изменив `DATABASES` в `config/settings.py`.

### 4. Применение миграций и запуск сервера

```bash
python manage.py migrate
python manage.py runserver
```

API доступно по адресу:  
👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

Документация:  
- Swagger: [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)  
- Redoc: [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

---

## 🐳 Запуск через Docker / Docker Compose

### 1. Подготовь `.env`

```bash
cp .env_sample .env
```

### 2. Сборка и запуск контейнеров

```bash
docker compose build
docker compose up
```

API будет доступно на  
👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

### ⚙️ Применение миграций в Docker

После первого запуска нужно выполнить миграции:

```bash
docker compose run --rm web python manage.py migrate
```

Создание суперпользователя:

```bash
docker compose run --rm web python manage.py createsuperuser
```

---

## 🔑 JWT Аутентификация

| Метод | URL | Описание |
|--------|-----|----------|
| `POST` | `/users/auth/register/` | Регистрация нового пользователя |
| `POST` | `/users/auth/token/` | Получение JWT-токенов |
| `POST` | `/users/auth/token/refresh/` | Обновление access-токена |
| `GET/PATCH` | `/users/profile/` | Просмотр и редактирование профиля |

**Пример запроса:**

```json
POST /users/auth/token/
{
  "email": "user@example.com",
  "password": "12345678"
}
```

**Ответ:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJh...",
  "access": "eyJhbGciOiJIUzI1NiIs..."
}
```

---

## 👥 Эндпоинты сотрудников

| Метод | URL | Описание |
|--------|-----|----------|
| `GET` | `/api/employees/` | Список всех сотрудников |
| `POST` | `/api/employees/` | Создать сотрудника |
| `GET` | `/api/employees/{id}/` | Просмотр сотрудника |
| `PATCH` | `/api/employees/{id}/` | Изменение данных |
| `DELETE` | `/api/employees/{id}/` | Удаление сотрудника |

**Пример ответа:**

```json
{
  "id": 3,
  "full_name": "Иван Иванов",
  "position": "Backend-разработчик"
}
```

---

## ✅ Эндпоинты задач

| Метод | URL | Описание |
|--------|-----|----------|
| `GET` | `/api/tasks/` | Список задач |
| `POST` | `/api/tasks/` | Создание задачи |
| `GET` | `/api/tasks/{id}/` | Просмотр задачи |
| `PATCH` | `/api/tasks/{id}/` | Обновление |
| `DELETE` | `/api/tasks/{id}/` | Удаление |

**Пример ответа:**

```json
{
  "id": 1,
  "title": "Реализация API авторизации",
  "parental_task_info": null,
  "performer_info": {
    "id": 2,
    "full_name": "Анна Смирнова",
    "position": "Frontend-разработчик"
  },
  "deadline": "2025-11-30T18:00:00Z",
  "status": "new"
}
```

---

## 📊 Дополнительные отчёты

| Метод | URL | Описание |
|--------|-----|----------|
| `GET` | `/api/tasks/busy_employees/` | Сотрудники с наибольшей загрузкой |
| `GET` | `/api/tasks/important_tasks/` | Важные задачи и рекомендованные исполнители |

### Пример `/api/tasks/busy_employees/`

```json
[
  {
    "id": 2,
    "full_name": "Анна Смирнова",
    "position": "Frontend-разработчик",
    "active_tasks_count": 3,
    "tasks": [
      {"id": 5, "title": "Исправить UI", "status": "at_work", "deadline": "2025-11-15T12:00:00Z"},
      {"id": 6, "title": "Проверить тесты", "status": "new", "deadline": "2025-11-18T09:00:00Z"}
    ]
  }
]
```

### Пример `/api/tasks/important_tasks/`

```json
[
  {
    "task_id": 7,
    "task_title": "Проверить API заказов",
    "deadline": "2025-11-20T17:00:00Z",
    "employees": ["Иван Иванов", "Анна Смирнова"]
  }
]
```

---

## 🧪 Тестирование и покрытие кода

### Локально:

```bash
python manage.py test
```

### В Docker:

```bash
docker compose run --rm web python manage.py test
```

### Покрытие:

```bash
coverage run manage.py test
coverage report
```

Сохранить в файл:

```bash
coverage report > coverage.txt
```

HTML-отчёт:

```bash
coverage html
```

---

## 🧰 Инструменты разработки

| Инструмент | Назначение |
|-------------|------------|
| **Django 5.2** | Основной фреймворк |
| **Django REST Framework** | API |
| **SimpleJWT** | JWT-аутентификация |
| **drf-yasg** | Swagger и Redoc |
| **PostgreSQL + psycopg2** | База данных |
| **black / flake8** | Форматирование и линтинг |
| **coverage** | Покрытие тестами |

---

## 📜 Лицензия

Проект распространяется свободно, если не указано иное.  
