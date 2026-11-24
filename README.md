# КТ6 — финальный проект TaskBoard (FastAPI)

**Тема:** API управления проектами и задачами. **Максимум по заданию:** 40 баллов. Это учебная реализация без фиктивного утверждения, что публичный деплой уже выполнен.

## Возможности и структура

- Три функциональных модуля `auth`, `projects`, `todos`: отдельные `router.py`, `service.py`, `schemas.py`.
- `User → Project → Todo` (связи один-ко-многим), PostgreSQL, SQLAlchemy ORM, миграция Alembic.
- Регистрация (201/409), bcrypt-хеш, JWT OAuth2 Password Flow (login), `/auth/me` (401), `/auth/admin` (403/200).
- CORS — только перечисленные адреса; SlowAPI — максимум 5 запросов/мин с IP на `/auth/login`.
- При создании Todo ставится фоновая **имитация отправки уведомления** через Celery + Redis (`.delay()`), возвращается UUID задачи; `/todos/job/{task_id}` показывает состояние `PENDING/STARTED/SUCCESS` и результат. **Реальная почта не отправляется.**
- Docker Compose поднимает PostgreSQL, Redis, FastAPI, Celery worker. GitHub Actions выполняет pytest на push/PR.

## Запуск одной командой

Требуется Docker Desktop или Docker Engine + Compose.

```bash
cp .env.example .env
```

Измените в `.env` `JWT_SECRET_KEY`, `POSTGRES_PASSWORD` и `ADMIN_PASSWORD` на собственные сложные значения. Ключ можно создать командой:

```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(48))'
```

> Важно: при изменении POSTGRES_PASSWORD **после** первого запуска нужно также обновить `DATABASE_URL`. Для новой установки эти значения должны совпадать.

```bash
docker compose up --build -d
```

API автоматически выполнит `alembic upgrade head` и запустит Uvicorn. Swagger: **http://localhost:8000/docs**. Проверка: `http://localhost:8000/health`.

```bash
docker compose ps
docker compose logs -f api worker
```

## Демонстрация преподавателю

1. В Swagger `POST /auth/register`: `alice@example.com`, `Password123` → **201**, повтор → **409**.
2. `POST /auth/login` OAuth2 form: поле `username` — email, поле `password` — пароль. Получить JWT и нажать **Authorize** в Swagger.
3. `GET /auth/me` с токеном → **200**; без токена → **401**.
4. `GET /auth/admin` под обычным пользователем → **403**.
5. Создать admin (следующий раздел), войти под ним и показать `/auth/admin` → **200**.
6. `POST /projects` → id проекта, `GET /projects`, `PATCH /projects/{id}`, `DELETE /projects/{id}`.
7. `POST /todos` с id проекта → **201** и `notification_task_id`; ответ приходит сразу (worker задерживается 5 секунд). `GET /todos/job/{task_id}` сразу → `PENDING` или `STARTED`, через 5–10 секунд → **SUCCESS** и JSON-результат. Статус `PENDING` можно не успеть увидеть, если worker быстр.
8. `GET /todos?project_id=...`, `GET /todos/{id}`, `PATCH`, `DELETE`. У второго пользователя доступ к чужому проекту → **403**.
9. Шесть попыток входа с одной IP в течение минуты (учитывайте, что предыдущие успешные входы тоже считаются): 6-я → **429**. Подождите минуту перед демонстрацией этого сценария.
10. Показать `alembic/versions/20261114_001_initial.py`, `app/db/models.py`, `docker-compose.yml`, `.github/workflows/tests.yml`.

### Создание admin без регистрации с повышенными правами

В `.env` задайте `ADMIN_EMAIL` и новый `ADMIN_PASSWORD`, затем:

```bash
docker compose exec api python -m scripts.create_admin
```

Обычная публичная регистрация всегда выдаёт роль `user`.

## Тесты

```bash
# Можно запускать тесты без действующих PostgreSQL/Redis — используется SQLite и mock очереди.
docker compose exec api pytest -q
# Или локально в venv:
pip install -r requirements.txt
pytest -q
```

## Миграции

```bash
docker compose exec api alembic current
docker compose exec api alembic upgrade head
# Для новой версии схемы (после изменения моделей):
docker compose exec api alembic revision --autogenerate -m "schema update"
```

## Публикация для последних 5 баллов

**Публичный URL не предоставляется**, потому что деплой на личный VPS/Railway требует доступа к твоему аккаунту, домену и секретам.

На VPS с Docker: скопировать репозиторий, создать `.env` с секретами и `DATABASE_URL` на сервис `db`, выполнить `docker compose up --build -d`. Настроить домен и HTTPS через Caddy или Nginx (проксировать на `127.0.0.1:8000`), не выставлять PostgreSQL/Redis наружу. Ограничить входящий порт 8000 при использовании reverse proxy и обновить CORS_ORIGINS под фронтенд. После деплоя проверить `https://ВАШ_ДОМЕН/health` и `https://ВАШ_ДОМЕН/docs`. Запушить репозиторий на GitHub и убедиться в зелёном workflow в Actions.

### Безопасность и ограничения

Учебный API: нет refresh/revocation токенов, настоящей почтовой отправки и production observability. История статусов Celery хранится в Redis 1 час, PENDING также означает неизвестный task_id; пользовательский endpoint статуса не является полноценной проверкой владения до момента SUCCESS. Не публикуйте `.env` в Git.

## Структура файлов

```text
app/
  main.py
  core/       # settings, JWT, limiter
  db/         # SQLAlchemy engine, models
  modules/
    auth/     # регистрация, login, me, admin
    projects/ # CRUD проектов
    todos/    # CRUD задач + enqueue/job status
  workers/    # Celery и задача уведомления
alembic/versions/  # миграции
scripts/create_admin.py
.github/workflows/tests.yml
tests/
Dockerfile
docker-compose.yml
```

## Краткий ответ на защиту

*REST* синхронно выполняет HTTP-запросы, но долгую операцию (например, отправку уведомления) не стоит задерживать в обработчике. Celery ставит работу в Redis, отдельный worker выполняет её независимо, а API сразу возвращает идентификатор задачи. SQLAlchemy защищает от SQL-инъекций при использовании ORM и параметризации. Alembic версионирует изменения схемы. JWT удостоверяет пользователя, RBAC ограничивает роль, а проверка owner_id защищает ресурсы других пользователей.
