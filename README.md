# Mini-Marketplace

Маркетплейс с Outbox паттерном, JWT-auth и идемпотентностью.

## Технологии

- **FastAPI** — веб-фреймворк
- **PostgreSQL** — база данных
- **SQLAlchemy 2.x** — ORM (async)
- **Alembic** — миграции
- **RabbitMQ** — очередь сообщений
- **JWT** — аутентификация
- **Docker** — контейнеризация
- **Ruff + Pyright + Pytest** — линтеры и тесты
- **Structlog** — структурное логирование

## Архитектура

app/
├── domain/ # Бизнес-логика, сущности, события
├── application/ # Use-cases, порты (интерфейсы)
├── infrastructure/ # SQLAlchemy, RabbitMQ, Outbox
└── interfaces/ # FastAPI роутеры, схемы

### Поток создания заказа

Client → POST /orders → CreateOrder (use-case) → Order + Outbox → RabbitMQ


#### Установка

1. Клонируй репозиторий
```bash
git clone https://github.com/Jagoxx/final_project.git
cd final_project

2. Установи зависимости
pip install -r requirements.txt

3. Настрой .env
DATABASE_URL=postgresql+asyncpg://postgres:ПАРОЛЬ@localhost:5432/mini_marketplace
JWT_SECRET=your-secret-key-change-me-to-something-longer-32-bytes

4. Создай БД
psql -U postgres -c "CREATE DATABASE mini_marketplace;"

5. Примени миграции
alembic upgrade head

6. Запусти RabbitMQ (Docker)
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

7. Запусти API
uvicorn app.main:app --reload

8. Запусти воркер 
python -m app.infrastructure.queue.worker

Запуск через Docker
docker compose up --build
(Поднимет API, PostgreSQL и RabbitMQ одной командой.)


## API Эндпоинты

Auth
POST	/register	Регистрация пользователя
POST	/login	Получение JWT-токена

Products
POST	/products	Создать товар
GET	/products/{id}	Получить товар

Orders
POST	/orders	Создать заказ (требует JWT + Idempotency-Key)
GET	/orders/{id}	Получить заказ

## Тестирование
Unit-тесты
pytest tests/unit -v

Integration-тесты
pytest tests/integration -v

Все тесты
pytest -v