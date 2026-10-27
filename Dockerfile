FROM python:3.12-slim

# Dependências de sistema: libmagic (python-magic) e libpq (psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pdm

ENV PDM_CHECK_UPDATE=false \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml pdm.lock* /app/

RUN pdm install --check

ENV PATH="/app/.venv/bin:$PATH"

COPY . /app/

EXPOSE 8000

CMD ["gunicorn", "app.wsgi:application", "--bind", "0.0.0.0:8000"]