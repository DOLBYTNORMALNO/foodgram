#!/bin/sh
set -e

echo "Ожидание базы данных и применение миграций..."
attempts=0
until python manage.py migrate; do
  attempts=$((attempts + 1))
  if [ "$attempts" -ge 30 ]; then
    echo "База данных недоступна, остановка." >&2
    exit 1
  fi
  sleep 2
done

python manage.py collectstatic --noinput

python manage.py load_ingredients

if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py createsuperuser --noinput || true
fi

exec gunicorn backend.wsgi:application --bind 0.0.0.0:8000
