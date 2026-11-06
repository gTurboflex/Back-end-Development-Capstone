#!/bin/sh
set -eu
python manage.py migrate --noinput
if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
    python manage.py shell -c 'import os; from django.contrib.auth import get_user_model; User=get_user_model(); name=os.environ["DJANGO_SUPERUSER_USERNAME"]; User.objects.filter(username=name).exists() or User.objects.create_superuser(name,os.environ.get("DJANGO_SUPERUSER_EMAIL",""),os.environ["DJANGO_SUPERUSER_PASSWORD"])'
fi
exec "$@"
