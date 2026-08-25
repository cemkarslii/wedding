FROM python:3.13-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

COPY requirements/ requirements/
RUN pip wheel --wheel-dir /wheels -r requirements/production.txt


FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

RUN groupadd --system django \
    && useradd --system --gid django --home-dir /app django

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

COPY --chown=django:django . .

RUN SECRET_KEY=collectstatic-build-key \
    python manage.py collectstatic --noinput

RUN mkdir -p /app/media \
    && chown django:django /app/media

USER django

VOLUME ["/app/media"]
EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-", "--error-logfile", "-"]
