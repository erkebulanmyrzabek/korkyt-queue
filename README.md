# Korkyt Queue

Стартовый монорепозиторий для электронной очереди с Telegram-ботом, веб-панелями и TV-экраном.

## Структура

```text
korkyt-queue/
├── backend/             # FastAPI, aiogram, Celery, PostgreSQL, Redis
├── frontend/            # Vue 3 + Vite + i18n
├── infra/
│   └── nginx/           # reverse proxy
├── scripts/             # локальные утилиты
├── uploads/             # фото пользователей
├── .env                 # локальная конфигурация
├── docker-compose.yml
└── Makefile
```

## Быстрый старт

```bash
make init
make up
```

После запуска:

- `http://localhost:8080` - веб-интерфейс
- `http://localhost:8080/tv` - TV режим
- `http://localhost:8080/api/v1/health` - healthcheck API
- `http://localhost:8000/docs` - FastAPI напрямую
- `http://localhost:5173` - Vue frontend напрямую

## Как запускать фронт и бэк

Все сервисы уже прописаны в контейнерах в `docker-compose.yml`.

Полный запуск:

```bash
make up
```

Только backend-часть:

```bash
make up-backend
```

Это поднимет:

- `postgres`
- `redis`
- `api`
- `bot`
- `worker`
- `beat`

Только frontend-часть:

```bash
make up-frontend
```

Это поднимет:

- `frontend`

Базовый веб-стек без bot/celery:

```bash
make up-core
```

Что где открывать:

- `http://localhost:8080` - фронт через `nginx`
- `http://localhost:8000` - backend напрямую
- `http://localhost:8000/docs` - Swagger
- `http://localhost:5173` - frontend без `nginx`

## Что уже подготовлено

- FastAPI backend с моделями под очередь, инструкторов и сессии
- aiogram bot scaffold с `/start`, `/queue`, `/language`
- Redis rate limit для `/queue`
- Celery worker и beat
- Vue-панели для admin, instructor и TV display
- Nginx reverse proxy
- `.env` и `.env.example`
- локальная `.venv` через `scripts/init_venv.sh`

## Дальше логично добавить

- полноценную аутентификацию admin/instructor
- Alembic миграции
- хранение фото в S3/MinIO или выделенном storage
- реальный WebSocket push вместо polling
- audit-лог и мониторинг
