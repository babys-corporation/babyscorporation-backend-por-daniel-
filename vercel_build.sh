#!/usr/bin/env bash
set -euo pipefail

if [ "${VERCEL_ENV:-}" = "production" ]; then
  python manage.py migrate --noinput
fi

python manage.py collectstatic --noinput
