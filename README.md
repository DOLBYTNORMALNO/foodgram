# Foodgram

«Продуктовый помощник»: сайт, на котором пользователи публикуют рецепты,
подписываются на публикации других авторов, добавляют удачные рецепты
в избранное и скачивают список покупок с суммарным количеством ингредиентов.

## Стек

- **Backend**: Python 3.9, Django 3.2, Django REST Framework, Djoser, PostgreSQL
- **Frontend**: React (сборка в контейнере, отдаётся nginx'ом)
- **Инфраструктура**: docker-compose (nginx, PostgreSQL, backend/gunicorn)

## Запуск

Нужны установленные [Docker](https://docs.docker.com/get-docker/) и docker-compose.

1. Перейдите в папку `infra/`:

   ```bash
   cd infra
   ```

2. При необходимости создайте файл `.env` (или скопируйте из примера
   `.env.example` — рабочие значения уже прописаны):

   ```bash
   cp .env.example .env
   ```

3. Выполните команду:

   ```bash
   docker-compose up
   ```

   При выполнении этой команды контейнер `frontend` подготовит файлы,
   необходимые для работы френденд-приложения, а затем прекратит свою работу.
   Контейнер `backend` применит миграции, импортирует ингредиенты из
   `data/ingredients.csv` и запустит приложение.

После старта:

- фронтенд веб-приложения — [http://localhost](http://localhost)
- спецификация API (Redoc) — [http://localhost/api/docs/](http://localhost/api/docs/)
- админ-зона Django — [http://localhost/admin/](http://localhost/admin/)

Администратор создаётся автоматически из переменных `DJANGO_SUPERUSER_*`
файла `infra/.env` (по умолчанию `admin@foodgram.local` / пароль `admin`).

## Локальный запуск backend (без Docker)

Проекту нужен Python 3.9 (на Python 3.12 Django 3.2 не работает).
Если в системе другой Python, создайте виртуальное окружение с нужной
версией через [uv](https://docs.astral.sh/uv/) — он сам скачает CPython 3.9:

```bash
# установка uv (без root)
curl -LsSf https://astral.sh/uv/install.sh | sh

cd backend
uv venv --python 3.9 .venv
source .venv/bin/activate
uv pip install -r requirements.txt

python manage.py migrate
python manage.py load_ingredients   # возьмёт ../data/ingredients.csv
python manage.py runserver
```

Без переменных окружения локально используется sqlite (`backend/db.sqlite3`)
и `DEBUG=True`, поэтому локальный запуск работает сразу после миграций.

## Переменные окружения

| Переменная | Описание |
|---|---|
| `SECRET_KEY` | Секретный ключ Django |
| `DEBUG` | `True`/`False` — режим отладки |
| `ALLOWED_HOSTS` | Хосты через запятую |
| `DB_ENGINE` | `django.db.backends.postgresql` (по умолчанию sqlite) |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Реквизиты БД |
| `DB_HOST`, `DB_PORT` | Хост и порт БД |

## Основные API-эндпоинты

| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/api/auth/token/login/` | Получение токена |
| `POST` | `/api/auth/token/logout/` | Удаление токена |
| `GET/POST` | `/api/recipes/` | Список и создание рецептов |
| `GET/PUT/PATCH/DELETE` | `/api/recipes/{id}/` | Рецепт |
| `POST/DELETE` | `/api/recipes/{id}/favorite/` | Избранное |
| `POST/DELETE` | `/api/recipes/{id}/shopping_cart/` | Список покупок |
| `GET` | `/api/recipes/download_shopping_cart/` | Скачать список покупок |
| `GET` | `/api/recipes/{id}/get-link/` | Короткая ссылка на рецепт |
| `GET` | `/api/tags/` | Теги |
| `GET` | `/api/ingredients/?name=` | Ингредиенты (поиск по названию) |
| `GET` | `/api/users/subscriptions/` | Подписки |
| `POST/DELETE` | `/api/users/{id}/subscribe/` | Подписка на автора |
| `PUT/DELETE` | `/api/users/me/avatar/` | Аватар |
| `POST` | `/api/users/` | Регистрация |

Полная спецификация — в `docs/openapi-schema.yml` и на `/api/docs/`.
