# Foodgram

Сервис рецептов: пользователи публикуют рецепты, подписываются на авторов,
добавляют рецепты в избранное и скачивают список покупок, где ингредиенты
суммированы по всем выбранным рецептам.

Backend — Django REST Framework, база — PostgreSQL, фронтенд — React
(собирается в контейнере и отдаётся nginx'ом). Всё поднимается
docker-compose'ом.

## Запуск

Нужны Docker и docker-compose.

```
cd infra
cp .env.example .env
docker-compose up
```

Контейнер backend при старте сам применяет миграции, импортирует
ингредиенты из `data/ingredients.csv` и создаёт суперпользователя
из переменных `DJANGO_SUPERUSER_*` (по умолчанию `admin@foodgram.local`
/ `admin`).

После запуска:

- http://localhost — сайт
- http://localhost/api/docs/ — документация API
- http://localhost/admin/ — админка

## Переменные окружения

Задаются в `infra/.env` (пример — `infra/.env.example`): `SECRET_KEY`,
`DEBUG`, `ALLOWED_HOSTS`, `DB_ENGINE`, `POSTGRES_DB`, `POSTGRES_USER`,
`POSTGRES_PASSWORD`, `DB_HOST`, `DB_PORT`. Без них (или локально без
docker) Django работает на sqlite.

Спецификация API — `docs/openapi-schema.yml`, там же `docs/redoc.html`.
