web: python scripts/create_superuser.py && gunicorn app.wsgi --log-file -
release: python manage.py migrate --noinput