# Task Manager API

Backend для управления задачами на FastAPI.

Сделан с акцентом на авторизацию, работу с redis, миграции и нормальную структуру проекта.

## Возможности

* Регистрация и авторизация (JWT)
* Logout с blacklist токенов в Redis
* Middleware Rare Limiting (по user_id, если пользователь авторизован, иначе - по IP)
* CRUD задач
* Пагинация, фильтрация и поиск
* Миграции через Alembic
* CORS и защитные middleware

## Стек

* FastAPI + Uvicorn
* SQLAlchemy 2.0 + Alembic
* PostgreSQL
* Redis
* Pydantic
* python-jose(JWT)
* passlib(хеширование паролей)
* Docker Compose

## Установка и запуск

1. Клонируйте репозиторий
2. Создайте `.env` из примера:

```bash
cp .env.example .env
```

3. Поднимите сервисы:
```bash
docker compose up --build
```
4.Примените миграции:
```bash
docker compose exec api alembic upgrade head
```

Документация API будет доступна по адресу: http://127.0.0.1:8000/docs
Остановка:
```bash
docker compose down
```


## Структура проекта
```bash
app/
├── api/              # роуты
├── core/             # безопасность, redis
├── db/               # Base,БД
├── models/           # SQLAlchemy модели
├── schemas/          # Pydantic схемы
├── middleware/       # rate limit 
├── main.py
alembic/              # миграции
alembic.ini
.dockerignore
docker-compose.yml
Dockerfile
.env.example
requirements.txt
.gitignore

```
## Несколько решений, которые я принял

- Rate limit сделал в первую очередь по `user_id`, а не по IP. Потому что почти все ручки требуют авторизации.
- Токены при логауте добавляю в Redis blacklist, а не просто удаляю на клиенте.
- Миграции через Alembic, а не `create_all`, чтобы можно было нормально менять схему без потери данных.

## Что можно улучшить

- Более гибкие настройки rate limit для разных эндпоинтов
- Тесты